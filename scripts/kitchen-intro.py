#!/usr/bin/env python3
"""ISLAND CREW KITCHEN · intro y cierre de marca (solo ffmpeg, coste 0, sin dependencias).
- Firma sonora ORIGINAL sintetizada con ffmpeg (arpegio de 4 notas + golpe): sin derechos de terceros.
- Si existe un jingle propio en <salida>/kitchen/jingles/intro.(mp3|wav) se usa ese en vez de la firma sintética.
Uso:  python3 scripts/kitchen-intro.py --prueba [SALIDA.mp4]     genera intro de 6 s 1920x1080 y la comprueba con ffprobe
Funciones: crear_intro(salida, titulo, ancho, alto, seg) · crear_cierre(...)"""
import os as _os
_os.environ["PATH"] = _os.pathsep.join([x for x in ["/opt/homebrew/bin", "/usr/local/bin"] if x not in _os.environ.get("PATH", "")] + [_os.environ.get("PATH", "")])
import glob, json, os, subprocess, sys, tempfile
AZUL, AMARILLO, BLANCO = "07182E", "FFD600", "FFFDF7"
def _run(a): r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error"] + a, capture_output=True, text=True); return r.returncode == 0, r.stderr[-600:]
def _fuente():
    for f in ("/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf"):
        if os.path.isfile(f): return f
    return ""
def _esc(t): return t.replace("\\", "\\\\").replace(":", "\\:").replace("'", "’").replace("%", "\\%")
def firma_sonora(ruta, seg=6.0, carpeta_jingles=None):
    """Audio de marca. Prioriza un jingle propio; si no hay, sintetiza el motivo de Island Crew (La-Do-Mi-La alto + golpe grave)."""
    if carpeta_jingles:
        for ext in ("mp3", "wav"):
            p = os.path.join(carpeta_jingles, "intro." + ext)
            if os.path.isfile(p): ok, er = _run(["-i", p, "-t", f"{seg:.2f}", "-af", f"afade=t=out:st={max(0, seg - 0.8):.2f}:d=0.8,loudnorm=I=-16:TP=-1.5", "-ar", "48000", "-ac", "2", ruta]); return ok, ("jingle propio" if ok else er)
    notas = [(440.0, 0.0), (554.37, 0.35), (659.25, 0.7), (880.0, 1.05)]; ins = []; fl = []
    for i, (f, t0) in enumerate(notas): ins += ["-f", "lavfi", "-i", f"sine=f={f}:d=0.9"]; fl.append(f"[{i}:a]afade=t=out:st=0.4:d=0.5,adelay={int(t0 * 1000)}|{int(t0 * 1000)},volume=0.5[n{i}]")
    ins += ["-f", "lavfi", "-i", "sine=f=65:d=1.2"]; fl.append("[4:a]afade=t=out:st=0.2:d=1.0,volume=0.9[g]")
    fc = ";".join(fl) + f";[n0][n1][n2][n3][g]amix=inputs=5:normalize=0,aecho=0.6:0.5:120:0.3,loudnorm=I=-16:TP=-1.5,aresample=48000,apad=pad_dur={seg:.2f},atrim=0:{seg:.2f}[a]"
    ok, er = _run(ins + ["-filter_complex", fc, "-map", "[a]", "-t", f"{seg:.2f}", "-ar", "48000", "-ac", "2", ruta]); return ok, ("firma sintetizada" if ok else er)
def _tarjeta(salida, titulo, subtitulo, w, h, seg, audio, fuente):
    fs = max(24, h // 12); fs2 = max(16, h // 28); d = f"{seg:.2f}"; dt = lambda txt, tam, col, y, ini: (f"drawtext=fontfile='{fuente}':text='{_esc(txt)}':fontsize={tam}:fontcolor=0x{col}:x=(w-text_w)/2:y={y}:alpha='if(lt(t,{ini}),0,min(1,(t-{ini})/0.5))'" if fuente else "null")
    vf = f"drawbox=x=0:y=h*0.62:w=iw*min(1\\,t/1.2):h=6:color=0x{AMARILLO}:t=fill," + dt(titulo, fs, BLANCO, "h*0.38", 0.8) + "," + dt(subtitulo, fs2, AMARILLO, "h*0.7", 1.6) + ",fade=t=in:st=0:d=0.5,fade=t=out:st=" + f"{max(0, seg - 0.6):.2f}:d=0.6"
    ok, er = _run(["-f", "lavfi", "-i", f"color=c=0x{AZUL}:s={w}x{h}:r=30:d={d}", "-i", audio, "-vf", vf, "-t", d, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast", "-crf", "18", "-c:a", "aac", "-b:a", "160k", "-ar", "48000", salida]); return ok, er
def crear_intro(salida, titulo="ISLAND CREW KITCHEN", subtitulo="Cocina con sabor a isla", w=1920, h=1080, seg=6.0, carpeta_jingles=None):
    tmp = tempfile.mkdtemp(prefix="ic-intro-"); a = os.path.join(tmp, "firma.wav"); ok, info = firma_sonora(a, seg, carpeta_jingles)
    if not ok: return False, "firma sonora: " + info
    ok, er = _tarjeta(salida, titulo, subtitulo, w, h, seg, a, _fuente()); return ok, (info if ok else "intro: " + er)
def crear_cierre(salida, mensaje="Suscríbete a Island Crew Kitchen", w=1920, h=1080, seg=5.0, carpeta_jingles=None): return crear_intro(salida, mensaje, "islandcrew.es", w, h, seg, carpeta_jingles)
def comprobar(p):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,sample_rate:format=duration", "-of", "json", p], capture_output=True, text=True)
    try: j = json.loads(r.stdout)
    except Exception: return None
    return {"duracion": float(j["format"]["duration"]), "streams": [(s["codec_type"], s["codec_name"], s.get("width"), s.get("height"), s.get("sample_rate")) for s in j["streams"]]}
if __name__ == "__main__" and "--prueba" in sys.argv:
    out = next((a for a in sys.argv[2:] if a.endswith(".mp4")), os.path.join(tempfile.mkdtemp(prefix="ic-"), "intro.mp4")); ok, info = crear_intro(out); c = comprobar(out) if ok else None
    print("OK" if ok and c and c["duracion"] > 5 else "FALLO", info, c, out); sys.exit(0 if ok and c and c["duracion"] > 5 else 1)
