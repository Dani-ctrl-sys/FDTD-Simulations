import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- 1. CONFIGURACIÓN DEL UNIVERSO ---
Nx = 200
Ny = 200
T_STEPS = 200

Ez = np.zeros((Nx, Ny))
Hx = np.zeros((Nx, Ny))
Hy = np.zeros((Nx, Ny))

# Constantes (Vacío)
coef = 0.5 

# --- 2. CONFIGURACIÓN GRÁFICA (Visualización Doble) ---
fig, ax = plt.subplots(figsize=(7, 7))

# A. CAPA 1: Eléctrica (Mapa de Calor)
im = ax.imshow(Ez, cmap='RdBu', vmin=-0.05, vmax=0.05, origin='lower', animated=True)

# B. CAPA 2: Magnética (Vectores / Flechas)
# "step" define cada cuántos píxeles dibujamos una flecha (para no saturar)
step = 8 
# Creamos la rejilla de coordenadas para las flechas
X, Y = np.meshgrid(np.arange(0, Ny, step), np.arange(0, Nx, step))

# Inicializamos el gráfico de flechas (Quiver)
# scale=0.5 controla el tamaño de la flecha. Menor número = flecha más larga.
Q = ax.quiver(X, Y, np.zeros_like(X), np.zeros_like(Y), 
              pivot='mid', color='black', scale=0.2, scale_units='xy')

plt.title("Fase 2 (Honores): Campos E y H Acoplados")
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='black', weight='bold')

# --- 3. KERNEL DE FÍSICA ---
def update(n):
    # --- FÍSICA (Igual que antes) ---
    Hx[:, :-1] -= coef * (Ez[:, 1:] - Ez[:, :-1])
    Hy[:-1, :] += coef * (Ez[1:, :] - Ez[:-1, :])
    
    Ez[1:-1, 1:-1] += coef * (
        (Hy[1:-1, 1:-1] - Hy[:-2, 1:-1]) - 
        (Hx[1:-1, 1:-1] - Hx[1:-1, :-2])   
    )
    
    # Fuente
    pulse = np.exp(-0.5 * ((n - 40) / 10) ** 2)
    Ez[Nx//2, Ny//2] += pulse
    
    # --- RENDERIZADO AVANZADO ---
    
    # 1. Actualizar Calor (Ez)
    im.set_array(Ez.T)
    
    # 2. Actualizar Flechas (Hx, Hy)
    # Tomamos una muestra cada 'step' píxeles y transponemos (.T)
    # Nota: Hx es el vector horizontal en la gráfica visual si Hy apunta en Y.
    # En FDTD 2D TMz:
    # Vector U (Horizontal visual) = Hy
    # Vector V (Vertical visual)   = -Hx  (Por la regla de la mano derecha y ejes)
    
    Hx_sample = Hx[::step, ::step].T
    Hy_sample = Hy[::step, ::step].T
    
    # Truco visual: Invertimos componentes para que coincidan con la intuición visual 
    # de rotación alrededor de Z.
    Q.set_UVC(Hy_sample, -Hx_sample)
    
    time_text.set_text(f'Step: {n}')
    
    return im, Q, time_text

# --- 4. ARRANQUE ---
anim = animation.FuncAnimation(fig, update, frames=T_STEPS, interval=30, blit=True)
plt.show()