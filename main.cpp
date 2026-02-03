// FILE: src/main.cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <chrono>
#include <fstream> // Necesario para guardar archivos
#include <string>
#include <algorithm> // Para std::clamp

// --- CONFIGURACIÓN ---
constexpr int Nx = 200;
constexpr int Ny = 200;
constexpr int T_STEPS = 500; 

// --- MOTOR DE FÍSICA (Tu código optimizado) ---
struct FDTDEngine {
    int w, h;
    std::vector<double> Ez, Hx, Hy, Cb;
    std::vector<double> Loss; // Mapa de Pérdidas (Conductividad)

    FDTDEngine(int width, int height) : w(width), h(height) {
        size_t size = w * h;
        Ez.resize(size, 0.0);
        Hx.resize(size, 0.0);
        Hy.resize(size, 0.0);
        Cb.assign(size, 0.5); 
        Loss.assign(size, 0.0); // Por defecto, nadie pierde energía
        
        // 1. DEFINICIÓN DEL MATERIAL (VIDRIO)
        for(int y=0; y<h; ++y) {
            for(int x=100; x<140; ++x) {
                Cb[y*w + x] = 0.5 / 4.0; // Vidrio n=2
            }
        }

        // 2. DEFINICIÓN DE FRONTERAS ABSORBENTES
        // Marco de 20 píxeles que "mata" las ondas
        int margin = 20;
        for(int y=0; y<h; ++y) {
            for(int x=0; x<w; ++x) {
                // Distancia al borde más cercano
                int dist_x = std::min(x, w - 1 - x);
                int dist_y = std::min(y, h - 1 - y);
                int dist = std::min(dist_x, dist_y);

                if (dist < margin) {
                    // Factor de pérdida: 0.0 en el interior, sube hasta 0.1 en el borde
                    // Usamos una curva cúbica para que sea suave y no rebote
                    double factor = (double)(margin - dist) / margin;
                    Loss[y*w + x] = 0.1 * factor * factor * factor;
                }
            }
        }
    }

    inline size_t idx(int x, int y) const { return y * w + x; }

    void update() {
        // Hx
        for (int y = 0; y < h - 1; ++y) {
            for (int x = 0; x < w; ++x) {
                Hx[idx(x, y)] -= 0.5 * (Ez[idx(x, y + 1)] - Ez[idx(x, y)]);
            }
        }
        // Hy
        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w - 1; ++x) {
                Hy[idx(x, y)] += 0.5 * (Ez[idx(x + 1, y)] - Ez[idx(x, y)]);
            }
        }
        // Ez + MATERIALES + PÉRDIDAS
        for (int y = 1; y < h - 1; ++y) {
            for (int x = 1; x < w - 1; ++x) {
                size_t i = idx(x, y);
                
                // Paso 1: Calcular el rotacional (la física estándar)
                double curl = (Hy[i] - Hy[idx(x-1, y)]) - (Hx[i] - Hx[idx(x, y-1)]);
                
                // Paso 2: Aplicar la física
                // Ez_new = Ez_old * (1 - loss) + Cb * curl
                // El término (1 - Loss[i]) hace que la onda se atenúe suavemente
                Ez[i] = Ez[i] * (1.0 - Loss[i]) + Cb[i] * curl;
            }
        }
    }
    
    void inject_source(int t) {
        // Fuente movida al centro para ver cómo viaja hacia los bordes
        double pulse = exp(-0.5 * pow((t - 40.0) / 10.0, 2.0));
        Ez[idx(Nx/2, Ny/2)] += pulse; 
    }
};

// --- NUEVO: RENDERIZADOR SIMPLE (SIN LIBRERÍAS) ---
void save_frame(const std::vector<double>& field, int w, int h, int step) {
    // 1. Crear nombre de archivo: "sim_001.ppm", "sim_002.ppm"...
    std::string filename = "sim_" + std::to_string(step) + ".ppm";
    std::ofstream file(filename, std::ios::binary);

    // 2. Cabecera PPM (Magic Number P6, Ancho, Alto, MaxColor)
    file << "P6\n" << w << " " << h << "\n255\n";

    // 3. Escribir píxeles
    for (int y = 0; y < h; ++y) { // Ojo: y=0 es arriba en imágenes
        for (int x = 0; x < w; ++x) {
            double val = field[y * w + x];
            
            // Mapeo de color (Heatmap: Azul=Negativo, Rojo=Positivo)
            unsigned char r = 0, g = 0, b = 0;
            
            // Normalizar valor visualmente (amplificar x10 para ver mejor)
            val = std::clamp(val * 10.0, -1.0, 1.0);

            if (val > 0) { // Positivo -> Rojo
                r = static_cast<unsigned char>(val * 255);
                b = static_cast<unsigned char>((1.0 - val) * 20); // Un poco de azul oscuro de fondo
            } else { // Negativo -> Azul
                b = static_cast<unsigned char>(std::abs(val) * 255);
                r = static_cast<unsigned char>((1.0 - std::abs(val)) * 20);
            }

            // Detectar Muro de Vidrio (Dibujar línea amarilla tenue en x=100 y x=140)
            if (x == 100 || x == 140) { 
                r = 255; // Encendemos Rojo
                g = 255; // Encendemos Verde
                b = 0;   // Apagamos Azul para limpiar
            }

            file << r << g << b;
        }
    }
    file.close();
}

int main() {
    std::cout << "--- RENDERIZADO C++ (PPM EXPORT) ---\n";
    FDTDEngine engine(Nx, Ny);

    auto start = std::chrono::high_resolution_clock::now();

    for (int t = 0; t < T_STEPS; ++t) {
        engine.inject_source(t);
        engine.update();

        // Guardar una imagen cada 5 pasos (para no llenar el disco)
        if (t % 5 == 0) {
            save_frame(engine.Ez, Nx, Ny, t);
            if (t % 50 == 0) std::cout << "Frame guardado: " << t << "\n";
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;
    std::cout << "Simulacion completada en " << diff.count() << " s.\n";
    std::cout << "Busca los archivos .ppm en la carpeta del proyecto.\n";

    return 0;
}