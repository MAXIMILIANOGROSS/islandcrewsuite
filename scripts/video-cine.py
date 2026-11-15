#!/usr/bin/env python3
"""Vídeo cine: monta tomas de Pixabay/Pexels (licencia gratuita, uso comercial) elegidas por las palabras de la letra, sobre el audio de la canción.
Sin letra guardada usa el título y el estilo. Lanza SystemExit con el motivo si no consigue tomas suficientes (el worker entonces sube la versión con imagen)."""
import json, os, re, subprocess, sys, urllib.parse, urllib.request
os.environ["PATH"] = "/opt/homebrew/bin:/usr/local/bin:" + os.environ.get("PATH", "")
UA = {"User-Agent": "IslandCrewCine/1.0"}
# palabra española -> consulta en inglés para el buscador de tomas
TEMAS = {"mar": "ocean waves", "olas": "ocean waves", "ola": "ocean waves", "agua": "water surface", "playa": "beach", "luna": "moon night sky", "estrella": "stars night sky", "estrellas": "stars night sky", "noche": "night city lights", "viento": "wind grass field", "fuego": "fire flames", "lava": "volcano lava", "volcan": "volcano", "volcán": "volcano", "lluvia": "rain drops window", "sol": "sunrise sun", "amanecer": "sunrise", "atardecer": "sunset sea", "faro": "lighthouse", "arena": "desert sand dunes", "desierto": "desert dunes", "bosque": "forest trees", "arbol": "forest trees", "árbol": "forest trees", "montaña": "mountain clouds", "montana": "mountain clouds", "ciudad": "city night traffic", "camino": "road driving", "carretera": "road driving", "tren": "train window", "puerto": "harbor boats", "barco": "sailing boat sea", "barca": "boat sea", "nubes": "clouds timelapse", "nube": "clouds timelapse", "flores": "flowers bloom", "flor": "flowers bloom", "pajaro": "birds flying", "pájaro": "birds flying", "pájaros": "birds flying", "baile": "dancing crowd", "bailar": "dancing crowd", "fiesta": "party lights", "lagrimas": "rain drops", "lágrimas": "rain drops", "niebla": "fog mist", "bruma": "fog mist", "cielo": "sky clouds", "isla": "island aerial", "islas": "island aerial", "tierra": "earth landscape aerial", "espejo": "reflection water", "reloj": "clock time", "tiempo": "time lapse clouds", "nieve": "snow", "invierno": "snow winter", "verano": "summer beach", "mercado": "market street", "pueblo": "village street", "casa": "house window light", "ventana": "window light curtains", "rio": "river", "río": "river", "cascada": "waterfall", "desierto": "desert dunes", "hielo": "ice", "caballo": "horses field", "cabra": "goats mountain", "cabras": "goats mountain", "teide": "volcano mountain", "drago": "tree silhouette sunset", "sal": "salt sea", "humo": "smoke", "lluvia": "rain"}
ESTILO = {"lofi": "rain window city night", "relax": "ocean waves calm", "ambient": "clouds timelapse", "reggaeton": "party lights night", "rock": "road driving storm", "folk": "forest field sunrise", "flamenco": "sunset silhouette", "house": "city night lights", "trap": "city night traffic", "pop": "beach sunset"}
RELLENO = ["ocean waves", "clouds timelapse", "sunset sea", "forest trees", "city night lights", "stars night sky"]
def _dur(r): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", r]).decode().strip())
def consultas(letra, titulo, estilo, n=8):
    t = re.findall(r"[a-záéíóúñ]+", (letra + " " + titulo).lower()); cuenta = {}
    for w in t:
        q = TEMAS.get(w)
        if q: cuenta[q] = cuenta.get(q, 0) + 1
    qs = [q for q, _ in sorted(cuenta.items(), key=lambda x: -x[1])]
    e = ESTILO.get((estilo or "").lower().split("-")[0]);
    if e and e not in qs: qs.append(e)
    for r in RELLENO:
        if len(qs) >= n: break
        if r not in qs: qs.append(r)
    return qs[:n]
def _json(u): return json.loads(urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read())
def _bajar(url, ruta): open(ruta, "wb").write(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()); return ruta
def toma(q, carpeta, usadas):
    pk, ke = os.environ.get("PIXABAY_API_KEY", "").strip(), os.environ.get("PEXELS_API_KEY", "").strip()
    if pk:
        try:
            for v in _json("https://pixabay.com/api/videos/?" + urllib.parse.urlencode({"key": pk, "q": q, "per_page": 15, "safesearch": "true"})).get("hits", []):
                f = (v.get("videos", {}).get("medium") or v.get("videos", {}).get("large") or {}); k = "pixabay_" + str(v["id"])
                if k in usadas or not f.get("url") or v.get("duration", 0) < 5 or (f.get("width") or 0) < (f.get("height") or 0): continue
                usadas.add(k); return _bajar(f["url"], os.path.join(carpeta, k + ".mp4"))
        except Exception as e: print("(aviso) Pixabay:", str(e)[:80], flush=True)
    if ke:
        try:
            rq = urllib.request.Request("https://api.pexels.com/videos/search?" + urllib.parse.urlencode({"query": q, "per_page": 12, "orientation": "landscape"}), headers={**UA, "Authorization": ke})
            for v in json.loads(urllib.request.urlopen(rq, timeout=30).read()).get("videos", []):
                k = "pexels_" + str(v["id"]); fs = [f for f in v.get("video_files", []) if f.get("file_type") == "video/mp4" and 700 <= (f.get("height") or 0) <= 1100]
                if k in usadas or not fs or v.get("duration", 0) < 5: continue
                usadas.add(k); return _bajar(fs[0]["link"], os.path.join(carpeta, k + ".mp4"))
        except Exception as e: print("(aviso) Pexels:", str(e)[:80], flush=True)
    return None
def crear(audio, letra, titulo, estilo, salida, vf_extra="", tmp=None):
    """Devuelve la ruta del MP4 (tomas + audio). SystemExit con el motivo si faltan claves o tomas."""
    if not (os.environ.get("PIXABAY_API_KEY") or os.environ.get("PEXELS_API_KEY")): sys.exit("Faltan PIXABAY_API_KEY o PEXELS_API_KEY en el Mac.")
    import tempfile; carpeta = tempfile.mkdtemp(prefix="ic_cine_", dir=tmp); dur = _dur(audio); usadas = set(); tomas = []
    qs = consultas(letra, titulo, estilo); print("Vídeo cine: tomas para", qs, flush=True)
    for q in qs:
        r = toma(q, carpeta, usadas)
        if r: tomas.append(r)
        if len(tomas) >= max(4, min(14, int(dur // 12) + 1)): break
    if len(tomas) < 3: sys.exit("No encontré tomas suficientes (" + str(len(tomas)) + ").")
    seg = max(4.0, dur / len(tomas)); lista = os.path.join(carpeta, "lista.txt"); partes = []
    for i, t in enumerate(tomas):
        o = os.path.join(carpeta, f"p{i}.mp4")
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-stream_loop", "-1", "-i", t, "-t", f"{seg:.2f}", "-vf", "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,fps=25,eq=brightness=-0.08:saturation=1.1,fade=t=in:st=0:d=0.6,fade=t=out:st=" + f"{max(0.1, seg - 0.6):.2f}" + ":d=0.6,format=yuv420p", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "24", o])
        if r.returncode == 0 and os.path.exists(o): partes.append(o)
    if len(partes) < 3: sys.exit("ffmpeg no pudo preparar las tomas.")
    open(lista, "w").write("".join("file '" + p.replace("'", "'\\''") + "'\n" for p in partes))
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista, "-i", audio, "-map", "0:v", "-map", "1:a", "-vf", "format=yuv420p" + vf_extra, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", salida])
    if r.returncode != 0 or not os.path.exists(salida): sys.exit("ffmpeg no pudo montar el vídeo cine.")
    return salida
if __name__ == "__main__":
    a, l, t, e, o = sys.argv[1:6]; print(crear(a, open(l, encoding="utf8").read() if os.path.exists(l) else "", t, e, o))
