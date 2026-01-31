import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# --- CONFIGURACIÓN DEL UNIVERSO ---
N = 200            # Tamaño del espacio
T_STEPS = 500      # Duración (igual que C++)
Ez = np.zeros(N)   # Campo Eléctrico
Hy = np.zeros(N)   # Campo Magnético

# Coeficientes (Courant S = 1, igual que C++)
Ch = 1.0
Ce = 1.0

# [ABC] Buffers de Memoria (como en C++)
left_buffer = 0.0
right_buffer = 0.0

# Preparar la gráfica
fig, ax = plt.subplots(figsize=(10, 4))
line, = ax.plot([], [], 'g-', lw=2, label='Ez (Campo Eléctrico)')
ax.set_xlim(0, N)
ax.set_ylim(-1.5, 1.5)
ax.axhline(0, color='black', lw=0.5)
ax.set_title("Simulación FDTD 1D - Fronteras Absorbentes (ABC)")
ax.legend()
ax.grid(True, alpha=0.3)

# --- EL MOTOR FÍSICO (Bucle por Frame) ---
def update(n):
    global Ez, Hy, left_buffer, right_buffer
    
    # --- A. Actualizar H (Magnético / Faraday) ---
    Hy[:-1] += Ch * (Ez[1:] - Ez[:-1])
    
    # --- B. Actualizar E (Eléctrico / Ampère) ---
    Ez[1:-1] += Ce * (Hy[1:-1] - Hy[:-2])
    
    # --- C. FUENTE (Hard Source) ---
    # Pulso Gaussiano en el centro (igual que C++)
    if n < 20:
        Ez[N//2] = np.exp(-0.5 * ((n - 10.0) / 3.0) ** 2)
        
    # --- D. FRONTERAS ABSORBENTES (Simple ABC) ---
    # Lado Izquierdo: Toma el valor del buffer
    Ez[0] = left_buffer
    # Lado Derecho: Toma el valor del buffer
    Ez[N-1] = right_buffer
    
    # --- E. ACTUALIZAR BUFFERS (Para el siguiente ciclo) ---
    left_buffer = Ez[1]      # Vecino del borde izquierdo
    right_buffer = Ez[N-2]   # Vecino del borde derecho
    
    # Actualizar gráfica
    line.set_data(np.arange(N), Ez)
    ax.set_title(f"FDTD ABC | Paso n={n} | Centro: {Ez[N//2]:.4f} | Borde Izq: {Ez[0]:.4f}")
    return line,

# Lanzar animación
anim = FuncAnimation(fig, update, frames=T_STEPS, interval=20, blit=True)
plt.show()