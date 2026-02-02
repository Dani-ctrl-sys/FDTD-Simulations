// FILE: src/main.cpp
#include <iostream>
#include <vector>
#include <cmath>
#include <chrono> // Para medir velocidad

// --- CONFIGURACIÓN ---
constexpr int Nx = 200;
constexpr int Ny = 200;
constexpr int T_STEPS = 1000; // Python hacía 300 sufriendo. Aquí haremos 1000 riendo.

// Estructura de Datos Orientada a Rendimiento
struct FDTDEngine {
    int w, h;
    std::vector<double> Ez;
    std::vector<double> Hx;
    std::vector<double> Hy;
    std::vector<double> Cb; // Nuestro mapa de materiales (Coefficient Map)

    FDTDEngine(int width, int height) : w(width), h(height) {
        // Reservar memoria lineal contigua (Cache Friendly)
        size_t size = w * h;
        Ez.resize(size, 0.0);
        Hx.resize(size, 0.0);
        Hy.resize(size, 0.0);
        
        // Inicializar Materiales (Vacío por defecto)
        // Coeficiente Courant 0.5
        Cb.assign(size, 0.5); 
        
        // [AQUÍ METEREMOS EL VIDRIO MÁS ADELANTE]
    }

    // Helper para convertir (x,y) a índice lineal
    // inline ayuda al compilador a eliminar la llamada a función
    inline size_t idx(int x, int y) const {
        return y * w + x;
    }

    void update() {
        // 1. Actualizar Hx (Depende de diferencias en Y de Ez)
        for (int y = 0; y < h - 1; ++y) {
            for (int x = 0; x < w; ++x) {
                // Hx[x, y] -= 0.5 * (Ez[x, y+1] - Ez[x, y])
                Hx[idx(x, y)] -= 0.5 * (Ez[idx(x, y + 1)] - Ez[idx(x, y)]);
            }
        }

        // 2. Actualizar Hy (Depende de diferencias en X de Ez)
        for (int y = 0; y < h; ++y) {
            for (int x = 0; x < w - 1; ++x) {
                // Hy[x, y] += 0.5 * (Ez[x+1, y] - Ez[x, y])
                Hy[idx(x, y)] += 0.5 * (Ez[idx(x + 1, y)] - Ez[idx(x, y)]);
            }
        }

        // 3. Actualizar Ez (Depende de Hx y Hy) + MATERIALES
        for (int y = 1; y < h - 1; ++y) {
            for (int x = 1; x < w - 1; ++x) {
                size_t i = idx(x, y);
                // Usamos Cb[i] para soportar materiales heterogéneos
                Ez[i] += Cb[i] * (
                    (Hy[i] - Hy[idx(x-1, y)]) - 
                    (Hx[i] - Hx[idx(x, y-1)])
                );
            }
        }
    }
    
    // Inyectar fuente (Soft Source)
    void inject_source(int t) {
        // Pulso gaussiano en el centro
        double pulse = exp(-0.5 * pow((t - 40.0) / 10.0, 2.0));
        Ez[idx(Nx/2, Ny/2)] += pulse;
    }
};

int main() {
    std::cout << "--- LIGHTSPEED ENGINE C++ (CPU CORE) ---\n";
    
    FDTDEngine engine(Nx, Ny);

    auto start = std::chrono::high_resolution_clock::now();

    // Bucle principal
    for (int t = 0; t < T_STEPS; ++t) {
        engine.inject_source(t);
        engine.update();
        
        // Output de diagnóstico cada 100 pasos
        if (t % 100 == 0) {
            // Leemos el valor central para ver si está "viva"
            double center_val = engine.Ez[engine.idx(Nx/2 + 10, Ny/2 + 10)];
            std::cout << "Step " << t << " | Sample Ez: " << center_val << "\n";
        }
    }

    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> diff = end - start;

    std::cout << "--- DONE ---\n";
    std::cout << "Simulated " << T_STEPS << " steps in " << diff.count() << " seconds.\n";
    std::cout << "Speed: " << (double(T_STEPS) * Nx * Ny) / diff.count() / 1e6 << " MCells/sec\n";

    return 0;
}