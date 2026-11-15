#!/usr/bin/env python3
"""ISLAND CREW · marca en TODOS los vídeos (canciones, jingles, Shorts, Kitchen): entradilla y cierre de marca con la firma sonora original.
Se adapta al formato del vídeo (vertical 9:16, horizontal 16:9, cuadrado) y a su duración: piezas cortas (≤60 s, jingles y Shorts) llevan 1,5 s de entrada y 2,5 s de cierre; las largas, 4 s y 4 s.
Si algo falla devuelve el vídeo ORIGINAL sin tocar (la marca nunca debe impedir una publicación). Solo ffmpeg, coste 0.
Uso:  python3 scripts/video-marca.py --prueba"""
import os as _os
_os.environ["PATH"] = _os.pathsep.join([x for x in ["/opt/homebrew/bin", "/usr/local/bin"] if x not in _os.environ.get("PATH", "")] + [_os.environ.get("PATH", "")])
import importlib.util, json, os, shutil, subprocess, sys, tempfile
_sp = importlib.util.spec_from_file_location("kitchen_intro", os.path.join(os.path.dirname(os.path.abspath(__file__)), "kitchen-intro.py")); K = importlib.util.module_from_spec(_sp); _sp.loader.exec_module(K)
def _info(p):
    j = json.loads(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", p], capture_output=True, text=True).stdout)
    v = next(s for s in j["streams"] if s["codec_type"] == "video"); n, d = (v.get("r_frame_rate") or "30/1").split("/"); fps = max(15, min(60, round(float(n) / float(d or 1)))) if float(d or 1) else 30
    return int(v["width"]), int(v["height"]), fps, float(j["format"]["duration"]), any(s["codec_type"] == "audio" for s in j["streams"])
def _norm(src, dst, w, h, fps, tiene_a):
    ent = ["-i", src] + ([] if tiene_a else ["-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo"])
    ok, er = K._run(ent + ["-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2:color=0x{K.AZUL},fps={fps},format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"] + ([] if tiene_a else ["-shortest"]) + [dst]); return ok, er
def _par(n): return n - (n % 2)
def con_marca(video, salida, titulo="", cta="islandcrew.es", jingles=None):
    """Devuelve la ruta del vídeo con marca; si no se puede, devuelve `video` (el original, intacto)."""
    tmp = tempfile.mkdtemp(prefix="ic-marca-")
    try:
        w, h, fps, dur, tiene_a = _info(video); w, h = _par(w), _par(h); corto = dur <= 60; si, sc = (1.5, 2.5) if corto else (4.0, 4.0)
        intro = os.path.join(tmp, "i.mp4"); cierre = os.path.join(tmp, "c.mp4"); cuerpo = os.path.join(tmp, "b.mp4")
        a = os.path.join(tmp, "firma.wav"); ok, inf = K.firma_sonora(a, si, jingles)
        ok1, e1 = K._tarjeta(intro, "ISLAND CREW", (titulo or "")[:48], w, h, si, a, K._fuente()) if ok else (False, inf)
        a2 = os.path.join(tmp, "firma2.wav"); ok, inf = K.firma_sonora(a2, sc, jingles)
        ok2, e2 = K._tarjeta(cierre, "ISLAND CREW", cta, w, h, sc, a2, K._fuente()) if ok else (False, inf)
        if not (ok1 and ok2): print("Marca: no se pudo crear la entradilla:", (e1 if not ok1 else e2)[:160], flush=True); return video
        ok, er = _norm(video, cuerpo, w, h, fps, tiene_a)
        if not ok: print("Marca: no se pudo normalizar el vídeo:", er[:160], flush=True); return video
        piezas = []
        for n, p in (("i", intro), ("c", cierre)):  # las tarjetas al mismo formato (fps y audio estéreo)
            d = os.path.join(tmp, n + "n.mp4"); ok, er = _norm(p, d, w, h, fps, True)
            if not ok: return video
            piezas.append(d)
        lista = os.path.join(tmp, "l.txt"); open(lista, "w").write(f"file '{piezas[0]}'\nfile '{cuerpo}'\nfile '{piezas[1]}'\n"); fin = os.path.join(tmp, "fin.mp4")
        ok, er = K._run(["-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", "-movflags", "+faststart", fin])
        if not ok: print("Marca: no se pudo unir:", er[:160], flush=True); return video
        w2, h2, _, d2, a_ok = _info(fin)
        if not a_ok or abs(d2 - (dur + si + sc)) > 1.5: print("Marca: duración inesperada; se usa el vídeo original.", flush=True); return video
        shutil.copyfile(fin, salida + ".part"); os.replace(salida + ".part", salida); return salida
    except Exception as ex:
        print("Marca: error, se usa el vídeo original:", str(ex)[:160], flush=True); return video
    finally: shutil.rmtree(tmp, ignore_errors=True)
def prueba():
    tmp = tempfile.mkdtemp(prefix="ic-mp-"); ok_all = True
    try:
        for nombre, size, d in (("jingle-vertical", "1080x1920", 15), ("cancion-horizontal", "1280x720", 70), ("cuadrado", "1080x1080", 8)):
            src = os.path.join(tmp, nombre + ".mp4"); K._run(["-f", "lavfi", "-i", f"testsrc2=s={size}:r=30:d={d}", "-f", "lavfi", "-i", "sine=f=440:d=" + str(d), "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", src])
            out = os.path.join(tmp, nombre + "-marca.mp4"); r = con_marca(src, out, "Prueba", "islandcrew.es"); w, h, fps, du, a = _info(r)
            esperado = d + (4.0 if d <= 60 else 8.0); bien = r == out and (w, h) == tuple(map(int, size.split("x"))) and a and abs(du - esperado) < 1.5
            print(("OK " if bien else "FALLO"), nombre, f"{w}x{h}", f"{du:.1f}s (esperado ≈{esperado:.1f})"); ok_all = ok_all and bien
        malo = os.path.join(tmp, "roto.mp4"); open(malo, "w").write("no es un vídeo"); r = con_marca(malo, os.path.join(tmp, "x.mp4")); print("OK " if r == malo else "FALLO", "vídeo roto → devuelve el original sin tocar"); ok_all = ok_all and r == malo
        return ok_all
    finally: shutil.rmtree(tmp, ignore_errors=True)
if __name__ == "__main__" and "--prueba" in sys.argv: sys.exit(0 if prueba() else 1)
