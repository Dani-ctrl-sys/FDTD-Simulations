import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# --- 1. CONFIGURACIÓN DEL UNIVERSO ---
Nx = 200
Ny = 200
T_STEPS = 300 # Aumenté un poco para ver el rebote completo

Ez = np.zeros((Nx, Ny))
Hx = np.zeros((Nx, Ny))
Hy = np.zeros((Nx, Ny))

# --- [NUEVO] DEFINICIÓN DE MATERIALES ---
# Coeficiente base del vacío (Courant number aprox 0.5 para estabilidad 2D)
S_courant = 0.5 

# Creamos el Mapa de Coeficientes (Inicialmente todo vacío)
Cb = np.ones((Nx, Ny)) * S_courant

# Propiedades del Material (Vidrio denso)
n_ref = 2.0           # Índice de refracción
epsilon_r = n_ref**2  # Permitividad relativa (4.0)

# Insertamos un bloque de material en el camino del pulso
# Geometría: Rectángulo entre X[100-140] y Y[0-200] (Muro vertical)
mat_start_x = 100
mat_end_x = 140
# Aplicamos la física: Coef_material = Coef_vacio / epsilon_r
Cb[mat_start_x:mat_end_x, :] = S_courant / epsilon_r

# --- 2. CONFIGURACIÓN GRÁFICA ---
fig, ax = plt.subplots(figsize=(7, 7))

# A. CAPA 1: Eléctrica (Ez)
im = ax.imshow(Ez, cmap='RdBu', vmin=-0.05, vmax=0.05, origin='lower', animated=True)

# [NUEVO] Dibujar contorno del material para saber dónde está
# Usamos un contour plot simple sobre la matriz Cb
ax.contour(Cb.T, levels=[S_courant*0.99], colors='yellow', linewidths=2, origin='lower')
ax.text(5, 110, "VACÍO (n=1)", color='black', fontsize=10)
ax.text(105, 110, "VIDRIO\n(n=2)", color='black', fontsize=10, ha='center')

# B. CAPA 2: Magnética (Flechas)
step = 8 
X, Y = np.meshgrid(np.arange(0, Ny, step), np.arange(0, Nx, step))
Q = ax.quiver(X, Y, np.zeros_like(X), np.zeros_like(Y), 
              pivot='mid', color='black', scale=0.005, scale_units='xy')

plt.title("Fase 3: Reflexión y Refracción (Dieléctricos)")
time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, color='black', weight='bold')

# --- 3. KERNEL DE FÍSICA ---
def update(n):
    # --- FÍSICA ---
    # Nota: Hx y Hy se actualizan con coeficiente 0.5 (asumimos materiales no magnéticos)
    # Si mu_r != 1, tendríamos que hacer un mapa para estos coeficientes también.
    Hx[:, :-1] -= S_courant * (Ez[:, 1:] - Ez[:, :-1])
    Hy[:-1, :] += S_courant * (Ez[1:, :] - Ez[:-1, :])
    
    # [MODIFICADO] Actualización de Ez usando el mapa Cb
    # Aquí es donde ocurre la magia: La onda se ralentiza dentro del bloque
    Ez[1:-1, 1:-1] += Cb[1:-1, 1:-1] * (
        (Hy[1:-1, 1:-1] - Hy[:-2, 1:-1]) - 
        (Hx[1:-1, 1:-1] - Hx[1:-1, :-2])   
    )
    
    # Fuente (Desplazada a la izquierda para tener espacio antes del choque)
    pulse = np.exp(-0.5 * ((n - 40) / 10) ** 2)
    Ez[60, Ny//2] += pulse # Fuente en x=60
    
    # --- RENDERIZADO ---
    
    im.set_array(Ez.T)
    
    Hx_sample = Hx[::step, ::step].T
    Hy_sample = Hy[::step, ::step].T
    Q.set_UVC(Hx_sample, Hy_sample)
    
    time_text.set_text(f'Step: {n}')
    
    return im, Q, time_text

# --- 4. ARRANQUE ---
anim = animation.FuncAnimation(fig, update, frames=T_STEPS, interval=30, blit=False)
# Diagnóstico: Imprimir valor en el centro del bloque de vidrio
print(f"Valor en vacío: {Cb[10,10]}")    # Debería ser 0.5
print(f"Valor en vidrio: {Cb[120,100]}") # Debería ser 0.125
plt.show()