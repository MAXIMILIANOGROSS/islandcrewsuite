#!/usr/bin/env python3
"""Reel con música de Island Crew: foto + trozo de una canción → vídeo vertical 1080x1920 (mp4, H.264 + AAC) listo para Instagram/Shorts.
Uso: python3 scripts/reel-musical.py foto.jpg cancion.mp3 salida.mp4 [segundos=20] [inicio=0]
La música entra con fundido y sale con fundido; la foto hace un zoom lento para que no sea una imagen congelada. Requiere ffmpeg."""
import subprocess, sys, shutil
def reel(foto, audio, salida, seg=20, inicio=0):
    if not shutil.which("ffmpeg"): raise RuntimeError("Falta ffmpeg.")
    seg = max(5, min(90, float(seg))); fps = 30; n = int(seg * fps)
    vf = f"scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,zoompan=z='min(zoom+0.0006,1.15)':d={n}:s=1080x1920:fps={fps},format=yuv420p"
    af = f"afade=t=in:st=0:d=0.8,afade=t=out:st={seg - 1.5:.2f}:d=1.5"
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", foto, "-ss", str(inicio), "-i", audio, "-t", f"{seg:g}", "-vf", vf, "-af", af, "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-shortest", salida]
    r = subprocess.run(cmd)
    if r.returncode != 0: raise RuntimeError("ffmpeg no pudo crear el Reel.")
    return salida
if __name__ == "__main__":
    a = sys.argv[1:]
    if len(a) < 3: sys.exit(__doc__)
    print(reel(a[0], a[1], a[2], a[3] if len(a) > 3 else 20, a[4] if len(a) > 4 else 0))
