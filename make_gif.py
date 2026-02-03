import glob
from PIL import Image

# Sort files numerically
frames = sorted(glob.glob("frames/sim_*.png"), key=lambda x: int(x.split('_')[1].split('.')[0]))

if frames:
    images = [Image.open(f) for f in frames]
    output_file = "fdtd_simulation.gif"
    images[0].save(
        output_file,
        save_all=True,
        append_images=images[1:],
        duration=50,  # 20 fps
        loop=0
    )
    print(f"GIF generado: {output_file} ({len(frames)} frames)")
else:
    print("No frames found to generate GIF")
