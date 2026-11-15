#!/usr/bin/env python3
"""ISLAND CREW KITCHEN · episodio horizontal 1920x1080: intro + cuerpo + cierre, QA técnico, SHA-256 y miniatura. Solo ffmpeg (coste 0).
Subtítulos: usa Whisper local SOLO si está instalado (whisper-cli de whisper.cpp o el paquete `whisper`); si no, lo dice y no los inventa.
No borra NADA: la limpieza de originales es otra fase y arranca en «conservar todo».
Uso:  python3 scripts/kitchen-episodio.py --prueba"""
import os as _os
_os.environ["PATH"] = _os.pathsep.join([x for x in ["/opt/homebrew/bin", "/usr/local/bin"] if x not in _os.environ.get("PATH", "")] + [_os.environ.get("PATH", "")])
import hashlib, importlib.util, json, os, shutil, subprocess, sys, tempfile
_sp = importlib.util.spec_from_file_location("kitchen_intro", os.path.join(os.path.dirname(os.path.abspath(__file__)), "kitchen-intro.py")); K = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(K)
W, H, FPS = 1920, 1080, 30
def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def _norm(src, dst):
    """Lleva cualquier pieza al mismo formato (1920x1080, 30 fps, H.264, AAC 48 kHz estéreo); si no tiene audio, añade silencio."""
    tiene_a = bool(subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=index", "-of", "csv=p=0", src], capture_output=True, text=True).stdout.strip())
    ent = ["-i", src] + ([] if tiene_a else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"])
    ok, er = K._run(ent + ["-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x{K.AZUL},fps={FPS},format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2"] + ([] if tiene_a else ["-shortest"]) + [dst]); return ok, er
def ensamblar(cuerpo, salida, titulo="ISLAND CREW KITCHEN", subtitulo="Cocina con sabor a isla", jingles=None):
    """cuerpo: lista de rutas de vídeo ya montadas (gancho, preparación, emplatado…). Devuelve (ok, info)."""
    tmp = tempfile.mkdtemp(prefix="ic-ep-")
    try:
        intro = os.path.join(tmp, "intro.mp4"); cierre = os.path.join(tmp, "cierre.mp4"); ok, i1 = K.crear_intro(intro, titulo, subtitulo, W, H, 6.0, jingles)
        if not ok: return False, i1
        ok, i2 = K.crear_cierre(cierre, w=W, h=H, carpeta_jingles=jingles)
        if not ok: return False, i2
        piezas = [intro]
        for n, c in enumerate(cuerpo):
            d = os.path.join(tmp, f"c{n}.mp4"); ok, er = _norm(c, d)
            if not ok: return False, f"No se pudo normalizar {os.path.basename(c)}: {er}"
            piezas.append(d)
        piezas.append(cierre); lista = os.path.join(tmp, "l.txt"); open(lista, "w").write("".join(f"file '{p}'\n" for p in piezas)); fin = os.path.join(tmp, "fin.mp4")
        ok, er = K._run(["-f", "concat", "-safe", "0", "-i", lista, "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-movflags", "+faststart", fin])
        if not ok: return False, "No se pudo unir el episodio: " + er
        qa = qa_tecnico(fin)
        if not qa["ok"]: return False, "QA falló: " + "; ".join(qa["fallos"])
        shutil.copyfile(fin, salida + ".part"); os.replace(salida + ".part", salida)
        if sha256(salida) != sha256(fin): return False, "La copia final no coincide (SHA-256): se conserva todo."
        return True, {"archivo": salida, "sha256": sha256(salida), **qa}
    finally: shutil.rmtree(tmp, ignore_errors=True)
def qa_tecnico(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,sample_rate:format=duration", "-of", "json", p], capture_output=True, text=True); f = []
    try: j = json.loads(r.stdout); s = j["streams"]; dur = float(j["format"]["duration"])
    except Exception: return {"ok": False, "fallos": ["ffprobe no puede leer el archivo"]}
    v = next((x for x in s if x["codec_type"] == "video"), None); a = next((x for x in s if x["codec_type"] == "audio"), None)
    if not v or v["codec_name"] != "h264" or (v["width"], v["height"]) != (W, H): f.append("el vídeo no es H.264 1920x1080")
    if not a or a["codec_name"] != "aac" or a.get("sample_rate") != "48000": f.append("el audio no es AAC 48 kHz")
    if dur < 5: f.append("duración demasiado corta")
    vol = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "volumedetect", "-vn", "-f", "null", "-"], capture_output=True, text=True).stderr
    if "max_volume: -91" in vol or "max_volume" not in vol: f.append("audio mudo")
    return {"ok": not f, "fallos": f, "duracion_s": round(dur, 2)}
def miniatura(video, salida, titulo, t=None):
    """1280x720 JPG: fotograma real del plato + banda de marca y título corto. Nada engañoso: el fotograma sale del propio vídeo."""
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", video]).decode()); t = t if t is not None else max(0, d * 0.85); fu = K._fuente()
    txt = f",drawtext=fontfile='{fu}':text='{K._esc(titulo.upper()[:34])}':fontsize=64:fontcolor=0x{K.BLANCO}:x=40:y=h-150" if fu else ""
    ok, er = K._run(["-ss", f"{t:.2f}", "-i", video, "-frames:v", "1", "-vf", f"scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,eq=saturation=1.1:contrast=1.05,drawbox=x=0:y=h-190:w=iw:h=190:color=0x{K.AZUL}@0.75:t=fill,drawbox=x=0:y=h-196:w=iw:h=6:color=0x{K.AMARILLO}:t=fill{txt}", "-q:v", "3", salida]); return ok, er
def whisper_disponible(): return shutil.which("whisper-cli") or shutil.which("whisper-cpp") or shutil.which("whisper")
def prueba():
    tmp = tempfile.mkdtemp(prefix="ic-prueba-"); ok_all = True
    try:
        a = os.path.join(tmp, "a.mp4"); b = os.path.join(tmp, "b.mp4")
        K._run(["-f", "lavfi", "-i", "testsrc2=s=1280x720:r=25:d=4", "-f", "lavfi", "-i", "sine=f=330:d=4", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", a])
        K._run(["-f", "lavfi", "-i", "smptebars=s=1920x1080:r=30:d=3", "-c:v", "libx264", "-pix_fmt", "yuv420p", b])  # sin audio a propósito
        out = os.path.join(tmp, "ep.mp4"); ok, info = ensamblar([a, b], out); print("EPISODIO", "OK" if ok else "FALLO", info)
        if ok:
            ok2, er = miniatura(out, os.path.join(tmp, "m.jpg"), "Receta de prueba"); print("MINIATURA", "OK" if ok2 and os.path.getsize(os.path.join(tmp, "m.jpg")) > 5000 else "FALLO", er); ok = ok and ok2
            print("DURACION esperada ≈ 6+4+3+5 = 18 s →", info["duracion_s"]); ok = ok and abs(info["duracion_s"] - 18) < 1.5
        print("WHISPER", "instalado" if whisper_disponible() else "NO instalado (los subtítulos no se inventan)"); return ok
    finally: shutil.rmtree(tmp, ignore_errors=True)
if __name__ == "__main__" and "--prueba" in sys.argv: sys.exit(0 if prueba() else 1)
