import numpy as np

# --- 1. CONFIGURACIÓN DEL UNIVERSO ---
Nx = 200        # Tamaño en X (Filas)
Ny = 200        # Tamaño en Y (Columnas)
T_STEPS = 300   # Pasos temporales

# Campos (Matrices 2D inicializadas a 0.0)
# Ez: Eje Z (Scalar field - Nodos enteros)
Ez = np.zeros((Nx, Ny))

# Hx, Hy: Componentes magnéticas (Nodos desplazados +0.5)
Hx = np.zeros((Nx, Ny))
Hy = np.zeros((Nx, Ny))

# Constantes Físicas (Unidades normalizadas)
# Courant (S) = c * dt / ds <= 1/sqrt(2) ≈ 0.707 en 2D
ds = 1.0        
dt = 0.5        
c = 1.0         

# Coeficiente de actualización (Simplificado para vacío)
# update_coeff = c * dt / ds = 0.5
coef = 0.5 

print(f"Sistema inicializado: {Nx}x{Ny}. Iniciando bucle temporal...")

# --- 2. BUCLE DE TIEMPO PRINCIPAL (LEAPFROG) ---
for n in range(T_STEPS):
    
    # --- A. Actualizar Campos Magnéticos (H) ---
    # Momento: n + 0.5
    
    # Hx depende de -dEz/dy (Diferencia de Columnas)
    # C++: Hx[i][j] = Hx[i][j] - 0.5 * (Ez[i][j+1] - Ez[i][j])
    Hx[:, :-1] -= coef * (Ez[:, 1:] - Ez[:, :-1])
    
    # Hy depende de +dEz/dx (Diferencia de Filas)
    # C++: Hy[i][j] = Hy[i][j] + 0.5 * (Ez[i+1][j] - Ez[i][j])
    Hy[:-1, :] += coef * (Ez[1:, :] - Ez[:-1, :])
    
    # --- B. Actualizar Campo Eléctrico (E) ---
    # Momento: n + 1
    
    # Ez depende de (dHy/dx - dHx/dy) (Curl de H)
    # C++: Ez[i][j] += 0.5 * ((Hy[i][j] - Hy[i-1][j]) - (Hx[i][j] - Hx[i][j-1]))
    # NOTA: Usamos slicing [1:-1] para evitar fronteras y problemas de índice -1
    Ez[1:-1, 1:-1] += coef * (
        (Hy[1:-1, 1:-1] - Hy[:-2, 1:-1]) - # dHy/dx (Filas: actual - anterior)
        (Hx[1:-1, 1:-1] - Hx[1:-1, :-2])   # dHx/dy (Cols: actual - anterior)
    )
    
    # --- C. Fuente (Source) ---
    # Inyectamos un pulso Gaussiano en el centro
    # np.exp es la versión vectorizada de std::exp
    pulse = np.exp(-0.5 * ((n - 40) / 10) ** 2)
    Ez[Nx//2, Ny//2] += pulse

print("Simulación completada (Cálculos realizados en memoria).")