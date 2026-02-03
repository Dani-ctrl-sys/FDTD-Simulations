from PIL import Image
import glob
import os

os.makedirs('frames', exist_ok=True)

ppm_files = sorted(glob.glob('sim_*.ppm'), key=lambda x: int(x.split('_')[1].split('.')[0]))
print(f"Encontradas {len(ppm_files)} imagenes PPM")

for f in ppm_files:
    step = int(f.split('_')[1].split('.')[0])
    out_name = f'frames/sim_{step:04d}.png'
    Image.open(f).save(out_name)
    
print(f"Convertidas {len(ppm_files)} imagenes a PNG en carpeta 'frames/'")
