#!/usr/bin/env python3
"""Cabra Beats · Voz de Gemini: rap o recitado con ACENTO REAL (Gemini TTS) sobre la base instrumental del motor de música.
Plan: 1) Gemini lee la letra por estrofas con el acento elegido; 2) el motor de música crea SOLO la base (instrumental) a la duración justa;
3) se detecta el pulso real de la base y cada estrofa se ajusta a compases enteros; 4) mezcla con compresión lateral (la base baja cuando rapea)."""
import os, re, json, base64, time, math, subprocess, shutil, urllib.request as u, urllib.error, tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
MODELOS_TTS = ["gemini-3.8-flash-tts", "gemini-3.8-flash-lite-tts", "gemini-3.1-flash-tts-preview", "gemini-2.5-flash-preview-tts"]
VOCES = {  # nombre de Gemini → (descripción, sexo)
    "Puck": ("Alegre y enérgica", "hombre"), "Charon": ("Informativa y firme", "hombre"), "Fenrir": ("Excitable, con garra", "hombre"), "Orus": ("Firme y seria", "hombre"),
    "Algenib": ("Áspera, de calle", "hombre"), "Enceladus": ("Susurrante, íntima", "hombre"), "Kore": ("Firme", "mujer"), "Zephyr": ("Brillante", "mujer"), "Leda": ("Juvenil", "mujer"), "Aoede": ("Ligera, fresca", "mujer"),
}
ACENTO_DIR = {
    "Argentine Rioplatense": "con acento porteño de Buenos Aires (rioplatense: sh en ll e y, s aspirada, entonación porteña, voseo)",
    "Spanish from Spain": "con acento de España (castellano peninsular)", "Canarian Spanish": "con acento canario (seseo, entonación de las islas)",
    "Mexican": "con acento mexicano", "Colombian": "con acento colombiano", "Chilean": "con acento chileno", "Caribbean": "con acento caribeño",
}


def clave():
    k = os.environ.get("GEMINI_API_KEY", "")
    if not k:
        for f in (os.path.join(AQUI, "..", ".env.local"), os.path.join(AQUI, "..", ".env"), os.path.expanduser("~/IslandCrewAI/.env")):
            try:
                for ln in open(f, encoding="utf8"):
                    if ln.startswith("GEMINI_API_KEY="): k = ln.split("=", 1)[1].strip().strip("\"'"); break
            except OSError: pass
            if k: break
    return k


def direccion(acento, rap=True):
    a = ACENTO_DIR.get(acento or "", "con acento neutro")
    return f"{'rapeando' if rap else 'recitando con ritmo'} {a}, flow rítmico, rápido y marcado, con actitud, sin pausas largas"


def tts(texto, voz="Puck", dir_="", log=None):
    k = clave()
    if not k: raise RuntimeError("Falta la clave gratuita de Gemini (GEMINI_API_KEY) para la voz.")
    cuerpo = {"contents": [{"parts": [{"text": (f"[{dir_}] " if dir_ else "") + texto}]}],
              "generationConfig": {"responseModalities": ["AUDIO"], "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voz}}}}}
    err = None
    for ronda in range(4):
        for mod in MODELOS_TTS:
            try:
                r = json.load(u.urlopen(u.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{mod}:generateContent", json.dumps(cuerpo).encode(), {"Content-Type": "application/json", "x-goog-api-key": k}), timeout=120))
                p = r["candidates"][0]["content"]["parts"][0]["inlineData"]; datos = base64.b64decode(p["data"])
                if len(datos) > 4000: return datos, p.get("mimeType", "")
            except urllib.error.HTTPError as e:
                err = f"{mod}: HTTP {e.code}"
            except Exception as e:
                err = f"{mod}: {str(e)[:80]}"
        if log: log(f"Gemini va justo de cuota; espero un momento y sigo… ({err})")
        time.sleep(12 + 12 * ronda)
    raise RuntimeError("Gemini no pudo grabar la voz ahora mismo: " + str(err))


def _guardar_wav(datos, mime, ruta):
    if mime.startswith("audio/L16") or mime.startswith("audio/pcm"):
        import wave
        rate = int(re.search(r"rate=(\d+)", mime).group(1)) if "rate=" in mime else 24000
        w = wave.open(ruta, "wb"); w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(datos); w.close()
    else:
        open(ruta, "wb").write(datos)


def duracion(f):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f], capture_output=True, text=True).stdout.strip()
    return float(r or 0)


def _recortar(src, dst):
    af = "silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.05,areverse,silenceremove=start_periods=1:start_threshold=-42dB:start_silence=0.05,areverse"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-af", af, "-ar", "24000", "-ac", "1", dst], check=True)


def trozos(letra):
    """[(etiqueta, texto)] — cada sección en grupos de hasta 4 versos."""
    out = []; et = ""; ls = []
    def cierra():
        for i in range(0, len(ls), 4):
            if ls[i:i + 4]: out.append((et, "\n".join(ls[i:i + 4])))
    for ln in str(letra or "").splitlines():
        s = re.sub(r"\*\*|__", "", ln.strip())
        if not s or s.startswith(("#", "---")): continue
        if s.startswith("["): cierra(); et = s.strip("[] ").lower(); ls = []; continue
        if re.match(r"^[\(\*_].*[\)\*_]$", s): continue
        ls.append(s)
    cierra()
    return out


def preparar(letra, voz, acento, bpm, carpeta, log=None, rap=True, tope=270, intro_bars=2, outro_bars=2):
    """Graba la voz con Gemini por estrofas y calcula duración y BPM de la base. Devuelve el plan."""
    os.makedirs(carpeta, exist_ok=True); tz = trozos(letra)
    if not tz: raise RuntimeError("No hay letra que grabar.")
    dir_ = direccion(acento, rap); cache = {}; piezas = []
    for n, (et, tx) in enumerate(tz):
        clave_t = re.sub(r"\W+", " ", tx.lower()).strip()
        if clave_t not in cache:
            if log: log(f"Gemini graba la voz ({n + 1}/{len(tz)})…")
            datos, mime = tts(tx, voz, dir_, log); crudo = os.path.join(carpeta, f"c{n}_raw.wav"); fin = os.path.join(carpeta, f"c{n}.wav")
            _guardar_wav(datos, mime, crudo); _recortar(crudo, fin); cache[clave_t] = (fin, duracion(fin))
        piezas.append({"etq": et, "texto": tx, "wav": cache[clave_t][0], "dur": cache[clave_t][1]})
    bpm = max(70, min(150, int(bpm or 92)))
    for _ in range(3):   # si no cabe en la duración máxima, sube el tempo
        bar = 240.0 / bpm; barras = sum(max(1, round(p["dur"] / bar)) for p in piezas)
        total = (intro_bars + barras + outro_bars) * bar + 3
        if total <= tope: break
        bpm = min(150, int(bpm * total / tope) + 1)
    return {"piezas": piezas, "bpm": bpm, "duracion": int(min(tope, max(20, math.ceil(total)))), "intro": intro_bars, "carpeta": carpeta}


_PULSO = r'''
import sys, json, numpy as np, librosa
y, sr = librosa.load(sys.argv[1], sr=22050, mono=True); pedido = float(sys.argv[2])
env = librosa.onset.onset_strength(y=y, sr=sr)
t, b = librosa.beat.beat_track(onset_envelope=env, sr=sr, start_bpm=pedido, tightness=120)
t = float(np.atleast_1d(t)[0])
while t < pedido * 0.75: t *= 2
while t > pedido * 1.5: t /= 2
tb = librosa.frames_to_time(b, sr=sr); fr = np.array(b)
mejor = 0; val = -1
for k in range(4):
    sel = fr[k::4][:24]
    v = float(env[sel].mean()) if len(sel) else 0
    if v > val: val = v; mejor = k
print(json.dumps({"bpm": round(t, 2), "primer": float(tb[mejor]) if len(tb) > mejor else 0.0}))
'''


def pulso(base_wav, bpm_pedido, py):
    try:
        r = subprocess.run([py, "-c", _PULSO, base_wav, str(bpm_pedido)], capture_output=True, text=True, timeout=240, env={**os.environ, "OMP_NUM_THREADS": "4", "KMP_DUPLICATE_LIB_OK": "TRUE"})
        d = json.loads(r.stdout.strip().splitlines()[-1]); bpm = float(d["bpm"])
        if abs(bpm - bpm_pedido) / bpm_pedido > 0.12: bpm = float(bpm_pedido)   # detección dudosa: confío en el tempo pedido
        return bpm, max(0.0, float(d["primer"]))
    except Exception:
        return float(bpm_pedido), 0.0


def mezclar(plan, base_wav, salida_wav, py, log=None):
    """Coloca cada estrofa en compases enteros sobre la base y mezcla con compresión lateral."""
    dur_base = duracion(base_wav)
    bpm, primer = pulso(base_wav, plan["bpm"], py); bar = 240.0 / bpm
    t = primer + plan["intro"] * bar; carpeta = plan["carpeta"]; entradas = []; colocadas = 0
    for i, p in enumerate(plan["piezas"]):
        barras = max(1, round(p["dur"] / bar)); L = barras * bar * 0.96
        if t + L > dur_base - 0.3:   # sin hueco: aprieta o descarta
            L = max(1.0, dur_base - 0.6 - t)
            if L < p["dur"] / 1.4: break
        f = min(1.4, max(0.7, p["dur"] / L)); out = os.path.join(carpeta, f"s{i}.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", p["wav"], "-filter:a", f"atempo={f:.4f}", out], check=True)
        entradas.append((out, t)); t += barras * bar; colocadas += 1
    if not entradas: raise RuntimeError("No pude colocar la voz sobre la base.")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", base_wav]; fc = []
    for i, (f, ts) in enumerate(entradas):
        cmd += ["-i", f]; ms = int(ts * 1000); fc.append(f"[{i + 1}:a]aresample=44100,adelay={ms}|{ms}[v{i}]")
    n = len(entradas); mezcla_v = "".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0:dropout_transition=0[vb]" if n > 1 else "[v0]anull[vb]"
    fc.append(mezcla_v)
    fc.append("[vb]highpass=f=85,acompressor=threshold=0.12:ratio=3:attack=5:release=90:makeup=2.5,aecho=0.8:0.55:70:0.16,volume=1.5[vp]")
    fc.append("[vp]asplit=2[vs][vm]")
    fc.append("[0:a]aresample=44100,volume=0.8[ib]")
    fc.append("[ib][vs]sidechaincompress=threshold=0.035:ratio=6:attack=15:release=260[bg]")
    fc.append("[bg][vm]amix=inputs=2:normalize=0[mix]")
    fc.append("[mix]alimiter=limit=0.95[out]")
    cmd += ["-filter_complex", ";".join(fc), "-map", "[out]", "-ar", "44100", "-ac", "2", salida_wav]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 or not os.path.isfile(salida_wav): raise RuntimeError("Falló la mezcla de la voz: " + (r.stderr or "")[-200:])
    return {"bpm": round(bpm, 1), "estrofas": colocadas, "de": len(plan["piezas"])}
