// FILE: src/fdtd_1d_simple.cpp
#include <vector>
#include <cmath>
#include <iostream>

int main() {
    // 1. Configuración del Universo
    const int N = 200;       // Tamaño de la rejilla
    const int T_STEPS = 500; // Duración simulación
    
    // Arrays para Campos (Inicializados a 0)
    std::vector<double> Ez(N, 0.0);
    std::vector<double> Hy(N, 0.0);
    
    // 2. Física "Mágica" (Courant S = 1) -> Luz viaja 1 celda por turno
    // [ABC] Configuración de "Velocidad de la Luz Perfecta" (S = 1.0)
    // Para absorción perfecta simple, necesitamos que la onda viaje 1 celda por tick.
    double Ce = 1.0; 
    double Ch = 1.0;
    
    // [ABC] Buffers de Memoria
    // Aquí guardaremos el valor del vecino para usarlo en el siguiente turno
    double left_buffer = 0.0;
    double right_buffer = 0.0;

    // 3. Bucle Temporal
    for (int n = 0; n < T_STEPS; n++) {
        
        // --- A. Actualizar H (Magnético) ---
        for (int i = 0; i < N - 1; i++) {
            Hy[i] = Hy[i] + Ch * (Ez[i+1] - Ez[i]);
        }
        
        // --- B. Actualizar E (Eléctrico) ---
        // Guardamos los bordes viejos para la condición de frontera
        // (En S=1 estricto no hace falta buffer complejo, pero conceptualmente sí)
        
        for (int i = 1; i < N - 1; i++) { // Evitamos 0 y N-1
            Ez[i] = Ez[i] + Ce * (Hy[i] - Hy[i-1]);
        }

        // --- C. Fuente (Hard Source) ---
        // Inyectamos un pulso en el centro para verla viajar
        if (n < 20) {
            Ez[N/2] = exp(-0.5 * pow((n - 10.0)/3.0, 2)); // Pulso Gaussiano
        }

        // --- D. Fronteras Absorbentes (Simple ABC) ---
        // Aquí ocurre la magia.
        
        // Lado Izquierdo (i=0): Toma lo que tenía el buffer (que vino de E[1])
        Ez[0] = left_buffer;
        
        // Lado Derecho (i=N-1): Toma lo que tenía el buffer (que vino de E[N-2])
        Ez[N-1] = right_buffer;

        // --- 5. ACTUALIZAR BUFFERS (Para el futuro) ---
        // Guardamos los valores "viejos" de los vecinos AHORA, 
        // para usarlos en la frontera en el SIGUIENTE ciclo (n+1).
        left_buffer  = Ez[1];     // El vecino del borde izquierdo
        right_buffer = Ez[N-2];   // El vecino del borde derecho
        
        // Visualización ASCII simple (Corte central)
        if (n % 10 == 0) {
            std::cout << "T=" << n << " | Centro: " << Ez[N/2] << " | Borde Izq: " << Ez[0] << "\n";
        }
    }
    return 0;
}