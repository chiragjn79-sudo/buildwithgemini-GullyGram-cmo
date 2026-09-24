import os
import subprocess
import imageio_ffmpeg

ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
input_webm = "/config/.gemini/antigravity/brain/85508562-8a8d-4770-bc53-48a78970ca96/gullygram_cmo_demo.webm"
output_gif = "/config/.gemini/antigravity/scratch/gullygram-cmo/demo.gif"

if not os.path.exists(input_webm):
    print("Error: input webm file not found at", input_webm)
else:
    print("Converting .webm to optimized looping GIF...")
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", input_webm,
        "-vf", "fps=10,scale=800:-1:flags=lanczos,split[s0][s1];[s0]palettegen=max_colors=128[p];[s1][p]paletteuse=dither=bayer",
        "-loop", "0",
        output_gif
    ]
    subprocess.run(cmd, check=True)
    size_mb = os.path.getsize(output_gif) / (1024 * 1024)
    print(f"✅ Converted demo.gif successfully! Size: {size_mb:.2f} MB")
