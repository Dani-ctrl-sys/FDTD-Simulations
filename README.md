# FDTD Simulations

Simulaciones electromagnéticas 1D usando el método **FDTD** (Finite-Difference Time-Domain) con condiciones de frontera absorbentes (ABC).

## Archivos

| Archivo | Descripción |
|---------|-------------|
| `fdtd_1d_simple.cpp` | Implementación en C++ con salida por consola |
| `fdtd_1d_visual.py` | Implementación en Python con animación matplotlib |

## Física

- **Método**: FDTD (Diferencias Finitas en el Dominio del Tiempo)
- **Ecuaciones**: Maxwell simplificadas 1D (Ez, Hy)
- **Fronteras**: ABC (Absorbing Boundary Conditions) usando buffers
- **Fuente**: Pulso Gaussiano en el centro del dominio
- **Courant**: S = 1 (velocidad de la luz = 1 celda/paso)

## Compilar y Ejecutar

### C++
```bash
g++ -o fdtd_1d_simple.exe fdtd_1d_simple.cpp -std=c++17
./fdtd_1d_simple.exe
```

### Python
```bash
python fdtd_1d_visual.py
```

## Requisitos

- **C++**: Compilador con soporte C++17 (g++, clang++, MSVC)
- **Python**: numpy, matplotlib
