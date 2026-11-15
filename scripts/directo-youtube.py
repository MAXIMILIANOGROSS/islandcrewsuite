#!/usr/bin/env python3
"""DIRECTO 24/7 A YOUTUBE desde el Mac (gratis): emite por RTMP las canciones de la biblioteca, cada una con su portada única (cabra-personaje) y el título.
Lo arranca y lo para el worker cuando la Dirección pulsa «Directo en YouTube» en la Oficina. Necesita YT_STREAM_KEY en ~/.islandcrew-env (la clave de emisión de YouTube Studio → Directo; NUNCA en el chat ni en la web)
y el directo activado en el canal (YouTube Studio → Crear → Emitir en directo; la primera vez tarda hasta 24 h en habilitarse).
Solo emite audio que ya existe en la carpeta de música; no inventa nada. Si no hay clave o no hay audio, sale con un mensaje claro."""
import glob, json, os, random, shutil, signal, subprocess, sys, tempfile, time, urllib.request as u
SALIDA = os.environ.get("MUSICA_DIR", "/Volumes/T5 EVO/IslandCrewAI/musica"); RTMP = os.environ.get("YT_RTMP_URL", "rtmp://a.rtmp.youtube.com/live2")
def _entorno():
    p = os.path.expanduser("~/.islandcrew-env")
    if os.path.exists(p):
        for l in open(p, encoding="utf8"):
            l = l.strip()
            if l.startswith("export ") and "=" in l:
                k, v = l[7:].split("=", 1); os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
def portada(titulo, estilo, dest):
    """Portada única de la canción (la misma que la miniatura de YouTube). Si la web no responde, la cabra fija."""
    try:
        base, tk = os.environ.get("ISLANDCREW_URL", "https://islandcrew.es"), os.environ.get("CRON_SECRET")
        rq = u.Request(base.rstrip("/") + "/api/oficina/youtube-imagen", json.dumps({"titulo": titulo, "estilo": estilo}).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + tk})
        png = u.urlopen(rq, timeout=60).read()
        if len(png) > 2000: open(dest, "wb").write(png); return True
    except Exception as e: print("(portada no disponible:", str(e)[:100] + ")", flush=True)
    return False
def emitir(wav, clave, tmp):
    nombre = os.path.splitext(os.path.basename(wav))[0]; partes = nombre.split("_"); titulo = nombre; estilo = partes[1] if len(partes) > 1 else ""
    loc = os.path.join(tmp, "a.wav"); shutil.copyfile(wav, loc)  # macOS impide a ffmpeg (launchd) leer el T5: se emite desde una copia local
    img = os.path.join(tmp, "p.png")
    if not portada(titulo, estilo, img): img = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "images", "cabra-sunset.webp")
    print("En directo:", titulo, flush=True)
    cmd = ["ffmpeg", "-loglevel", "error", "-re", "-loop", "1", "-framerate", "2", "-i", img, "-i", loc, "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p",
           "-c:v", "libx264", "-preset", "veryfast", "-tune", "stillimage", "-b:v", "1500k", "-g", "4", "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-shortest", "-f", "flv", RTMP.rstrip("/") + "/" + clave]
    return subprocess.run(cmd).returncode
def main():
    _entorno(); clave = os.environ.get("YT_STREAM_KEY", "").strip()
    if not clave: sys.exit("Falta YT_STREAM_KEY en ~/.islandcrew-env (clave de emisión de YouTube Studio → Directo).")
    if not shutil.which("ffmpeg"): sys.exit("Falta ffmpeg.")
    signal.signal(signal.SIGTERM, lambda *_: sys.exit(0)); fallos = 0
    while True:
        wavs = [w for w in glob.glob(os.path.join(SALIDA, "*.wav")) if os.path.getsize(w) > 200000]
        if not wavs: print("No hay canciones en", SALIDA, "; reintento en 60 s.", flush=True); time.sleep(60); continue
        tmp = tempfile.mkdtemp(prefix="ic-directo-")
        try: rc = emitir(random.choice(wavs), clave, tmp)
        finally: shutil.rmtree(tmp, ignore_errors=True)
        fallos = 0 if rc == 0 else fallos + 1
        if fallos >= 5: sys.exit("YouTube rechaza la emisión (5 fallos seguidos): ¿directo activado en el canal y clave correcta?")
        time.sleep(1 if rc == 0 else 10)
if __name__ == "__main__": main()
