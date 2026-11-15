#!/usr/bin/env python3
"""Vídeo lírico: la letra va pasando sobre el fondo de Island Crew mientras suena la canción.
Los tiempos se REPARTEN por duración y longitud de cada verso (no es alineación palabra a palabra): sirve de guía y se puede afinar a mano en YouTube Studio."""
# PATH_EXTRA: el worker arranca desde launchd sin /opt/homebrew/bin; sin esto no encuentra ffmpeg ni ffprobe.
import os as _os
_os.environ["PATH"] = _os.pathsep.join([x for x in ["/opt/homebrew/bin", "/usr/local/bin", "/opt/homebrew/sbin"] if x not in _os.environ.get("PATH", "")] + [_os.environ.get("PATH", "")])

import json, os, re, subprocess, sys
def _dur(ruta): return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", ruta]).decode().strip())
def versos(letra):
    out = []
    for l in str(letra).splitlines():
        l = l.strip()
        if not l or re.fullmatch(r"\[[^\]]*\]", l) or re.fullmatch(r"\([^)]*\)", l): continue
        out.append(re.sub(r"\[[^\]]*\]", "", l).strip())
    return [x for x in out if x]
def _t(s): s = max(0.0, s); return f"{int(s // 3600)}:{int(s % 3600 // 60):02d}:{s % 60:05.2f}"
def reparto(vs, dur):
    """[(inicio, fin, texto)]: deja una introducción (≈6 % o 6 s) y un final de 5 s sin letra; el tiempo se reparte por longitud de verso."""
    if not vs: return []
    ini = min(10.0, max(4.0, dur * 0.06)); fin = max(ini + len(vs) * 1.5, dur - 5.0); util = fin - ini; pesos = [max(len(v), 14) for v in vs]; tot = sum(pesos); t = ini; out = []
    for v, w in zip(vs, pesos): d = util * w / tot; out.append((t, t + d, v)); t += d
    return out
def palabras_cantadas(audio):
    """Instantes REALES de cada palabra cantada, con Whisper si está instalado (faster-whisper, openai-whisper o mlx-whisper). Devuelve [(inicio, fin)] o None."""
    try:
        from faster_whisper import WhisperModel
        seg, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(audio, language="es", word_timestamps=True, vad_filter=False)
        return [(w.start, w.end) for sg in seg for w in (sg.words or [])] or None
    except Exception: pass
    try:
        import whisper
        r = whisper.load_model("small").transcribe(audio, language="es", word_timestamps=True)
        return [(w["start"], w["end"]) for sg in r.get("segments", []) for w in sg.get("words", [])] or None
    except Exception: pass
    try:
        import mlx_whisper
        r = mlx_whisper.transcribe(audio, path_or_hf_repo="mlx-community/whisper-small-mlx", language="es", word_timestamps=True)
        return [(w["start"], w["end"]) for sg in r.get("segments", []) for w in sg.get("words", [])] or None
    except Exception: return None
def transcribir(audio):
    """Para canciones SIN letra guardada: lo que Whisper reconoce que se canta, ya con sus tiempos reales. [(inicio, fin, texto)] o None. Es texto reconocido (puede tener erratas), no la letra original."""
    try:
        from faster_whisper import WhisperModel
        seg, _ = WhisperModel("small", device="cpu", compute_type="int8").transcribe(audio, language="es", vad_filter=False)
        out = [(sg.start, sg.end, " ".join(sg.text.split()).strip(" -")) for sg in seg if len(sg.text.split()) >= 2]
        return out if len(out) >= 3 and sum(len(t.split()) for _, _, t in out) >= 12 else None
    except Exception: return None
def reparto_cantado(vs, pal, dur):
    """Cada verso aparece cuando se canta: el verso i cubre sus palabras (por orden) dentro de las palabras detectadas por Whisper. Mantiene el orden y no se solapa."""
    nl = [max(1, len(v.split())) for v in vs]; N = sum(nl); M = len(pal)
    if M < max(4, N // 3): return None  # el reconocimiento no vio casi nada cantado: no fiable
    out = []; a = 0
    for v, n in zip(vs, nl):
        i0 = min(M - 1, int(a * M / N)); i1 = min(M - 1, max(i0, int((a + n) * M / N) - 1)); a += n
        out.append([max(0.0, pal[i0][0] - 0.15), pal[i1][1] + 0.35, v])
    for k in range(len(out) - 1): out[k][1] = min(out[k][1], out[k + 1][0] - 0.05) if out[k + 1][0] > out[k][0] + 0.3 else out[k][1]
    return [(a, min(b, dur), v) for a, b, v in out]
def ass(titulo, tramos, dur, ruta):
    cab = "[Script Info]\nScriptType: v4.00+\nPlayResX: 1280\nPlayResY: 720\n\n[V4+ Styles]\nFormat: Name,Fontname,Fontsize,PrimaryColour,OutlineColour,BackColour,Bold,Outline,Shadow,Alignment,MarginL,MarginR,MarginV\nStyle: Letra,Arial,54,&H00FFFFFF,&H00000000,&H80000000,1,3,2,5,80,80,40\nStyle: Titulo,Arial,40,&H0000D6FF,&H00000000,&H80000000,1,3,2,8,80,80,60\n\n[Events]\nFormat: Layer,Start,End,Style,Name,MarginL,MarginR,MarginV,Effect,Text\n"
    ev = [f"Dialogue: 0,{_t(0.5)},{_t(min(dur, 6))},Titulo,,0,0,0,,{{\\fad(600,600)}}{titulo.replace(chr(10), ' ')}"]
    for a, b, v in tramos: ev.append(f"Dialogue: 0,{_t(a)},{_t(b)},Letra,,0,0,0,,{{\\fad(250,250)}}{v.replace('{', '(').replace('}', ')')}")
    open(ruta, "w", encoding="utf8").write(cab + "\n".join(ev) + "\n")
def crear(audio, letra, titulo, imagen, salida, vf_extra=""):
    """Devuelve la ruta del MP4. Lanza SystemExit con el motivo si no hay letra o falla ffmpeg."""
    vs = versos(letra)
    dur = _dur(audio); sub = salida[:-4] + ".ass"
    if len(vs) < 2:
        # Canción antigua sin letra guardada: se reconoce lo cantado con Whisper (texto con sus tiempos reales).
        rec = transcribir(audio)
        if not rec: sys.exit("Esta canción no tiene la letra guardada en el Mac y Whisper no pudo reconocer lo cantado (¿está instalado faster-whisper? o la canción es instrumental): no se crea un vídeo lírico sin letra.")
        print("Sin letra guardada: letra RECONOCIDA del audio con Whisper (puede tener erratas).", flush=True)
        ass(titulo, [(a, min(b, dur), t) for a, b, t in rec], dur, sub)
        esc = sub.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
        vf = f"scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,eq=brightness=-0.22,format=yuv420p,subtitles='{esc}'" + vf_extra
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "25", "-i", imagen, "-i", audio, "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", salida])
        if r.returncode != 0 or not os.path.exists(salida): sys.exit("ffmpeg no pudo crear el vídeo lírico (¿falta el filtro de subtítulos?).")
        return salida
    pal = palabras_cantadas(audio); tr = reparto_cantado(vs, pal, dur) if pal else None
    print("Letra sincronizada con lo cantado (Whisper)." if tr else "Letra con tiempos repartidos (instala faster-whisper para sincronizarla con lo cantado: pip3 install faster-whisper).", flush=True)
    ass(titulo, tr or reparto(vs, dur), dur, sub)
    esc = sub.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    vf = f"scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,eq=brightness=-0.22,format=yuv420p,subtitles='{esc}'" + vf_extra
    r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "25", "-i", imagen, "-i", audio, "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", salida])
    if r.returncode != 0 or not os.path.exists(salida): sys.exit("ffmpeg no pudo crear el vídeo lírico (¿falta el filtro de subtítulos?).")
    return salida
if __name__ == "__main__":
    a, l, t, i, o = sys.argv[1:6]; print(crear(a, open(l, encoding="utf8").read(), t, i, o))
