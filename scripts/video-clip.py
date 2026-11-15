#!/usr/bin/env python3
"""Videoclip de cine para cada canción de Cabra Beats.
Cada canción recibe un «universo» propio (estilo de letra, tipografía, paleta, color de cine, movimientos de cámara, escenas) que no se repite
con el de otras. Las letras aparecen frase a frase, con fundidos, sobre escenas creadas con IA gratuita (o arte propio si no hay internet).
Todo se monta con ffmpeg en el Mac, sin servicios de pago."""
import os, sys, re, json, math, random, hashlib, subprocess, shutil, time, io, colorsys, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

AQUI = os.path.dirname(os.path.abspath(__file__)); FUENTES = os.path.join(AQUI, "fuentes"); LOGO = os.path.join(AQUI, "cabra-beats-logo.png")
FPS = 24
SIS = "/System/Library/Fonts/Supplemental/"
FUENTE = {"bebas": os.path.join(FUENTES, "BebasNeue-Regular.ttf"), "archivo": os.path.join(FUENTES, "ArchivoBlack-Regular.ttf"), "barlow": os.path.join(FUENTES, "Barlow-SemiBold.ttf"),
          "marker": os.path.join(FUENTES, "PermanentMarker-Regular.ttf"), "didot": SIS + "Didot.ttc", "georgia": SIS + "Georgia Italic.ttf", "copperplate": SIS + "Copperplate.ttc",
          "futura": SIS + "Futura.ttc", "baskerville": SIS + "Baskerville.ttc", "optima": "/System/Library/Fonts/Optima.ttc"}
def fuente_ok(k): return k if os.path.isfile(FUENTE.get(k, "")) else "barlow"
def cargar_fuente(k, size):
    try: return ImageFont.truetype(FUENTE[fuente_ok(k)], size)
    except Exception: return ImageFont.load_default()

# ── estilos de letra: cada uno es una forma distinta de escribir la canción en pantalla ──
ESTILOS_LETRA = {
    "cine":     {"nombre": "Cine clásico",        "fuentes": ["didot", "georgia", "baskerville", "barlow"], "mayus": False, "tam": 1.0,  "color": "blanco",  "trazo": 0, "brillo": 0.0, "pos": "abajo",  "anim": "fundido", "esp": 0},
    "neon":     {"nombre": "Neón nocturno",       "fuentes": ["bebas", "futura", "archivo"],                 "mayus": True,  "tam": 1.25, "color": "acento",  "trazo": 0, "brillo": 1.0, "pos": "centro", "anim": "fundido", "esp": 3},
    "poster":   {"nombre": "Póster tipográfico",  "fuentes": ["archivo", "bebas"],                           "mayus": True,  "tam": 1.4,  "color": "blanco",  "trazo": 4, "brillo": 0.0, "pos": "centro", "anim": "subida",  "esp": 0},
    "manuscrita": {"nombre": "Manuscrita",        "fuentes": ["marker", "georgia"],                          "mayus": False, "tam": 1.15, "color": "claro",   "trazo": 3, "brillo": 0.2, "pos": "abajo",  "anim": "subida",  "esp": 0},
    "dorado":   {"nombre": "Elegante dorado",     "fuentes": ["copperplate", "didot", "optima", "barlow"],   "mayus": True,  "tam": 0.95, "color": "dorado",  "trazo": 0, "brillo": 0.35, "pos": "abajo", "anim": "fundido", "esp": 5},
    "vhs":      {"nombre": "Retro VHS",           "fuentes": ["bebas", "barlow"],                            "mayus": True,  "tam": 1.2,  "color": "blanco",  "trazo": 0, "brillo": 0.0, "pos": "abajo",  "anim": "fundido", "esp": 2, "vhs": True},
    "minimal":  {"nombre": "Minimalista",         "fuentes": ["barlow", "optima", "futura"],                 "mayus": False, "tam": 0.85, "color": "blanco",  "trazo": 0, "brillo": 0.0, "pos": "izquierda", "anim": "fundido", "esp": 1},
    "titular":  {"nombre": "Gran titular",        "fuentes": ["bebas", "archivo"],                           "mayus": True,  "tam": 1.5,  "color": "claro",   "trazo": 0, "brillo": 0.0, "pos": "arriba", "anim": "bajada",  "esp": 2},
}
GRADES = {
    "calido":  ("Cálido dorado",   "eq=contrast=1.08:saturation=1.15:gamma_r=1.05:gamma_b=0.92"),
    "tealnaranja": ("Teal y naranja", "colorbalance=rs=-0.08:bs=0.12:rh=0.12:bh=-0.10,eq=contrast=1.1:saturation=1.1"),
    "mono":    ("Blanco y negro suave", "eq=saturation=0.2:contrast=1.15"),
    "neon":    ("Neón saturado",   "eq=contrast=1.15:saturation=1.5:brightness=-0.02"),
    "vintage": ("Película antigua", "curves=preset=vintage,eq=saturation=0.9"),
    "frio":    ("Frío azulado",    "colorbalance=bs=0.12:bm=0.08:rs=-0.05,eq=saturation=1.05"),
}
MOVS = ["zoom_in", "zoom_out", "pan_izq", "pan_der"]
TRANS = ["fade", "fadeblack", "dissolve", "wipeleft", "smoothleft", "slideup", "circleopen"]
PALETAS = {"Pop": ("#2b0a4a", "#ff4fa3", "#ffe66b"), "Rock": ("#0d0d0d", "#c1121f", "#f1f1f1"), "Urbano y hip hop": ("#0a0a14", "#7a3cff", "#ffd60a"), "Electrónica": ("#02041c", "#00e5ff", "#ff2bd6"),
           "Latino y tropical": ("#3a0d00", "#ff7a00", "#ffe14d"), "Raíces y folk": ("#2d1b0e", "#c98a3b", "#f5ecd7"), "Reggae y mundo": ("#06280f", "#f2b705", "#e63946"),
           "Jazz, soul y funk": ("#1b0f2e", "#c77d0a", "#f0d9a8"), "Cine, clásica y ambiente": ("#05060f", "#3a6ea5", "#e9eef7"), "Para negocios": ("#0f2a2e", "#2ec4b6", "#fff1d0"),
           "Estilos de Island Crew": ("#04101f", "#0ea5e9", "#fde047")}

def hex_rgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def desplazar(h, grados, luz=0.0):
    r, g, b = [x / 255 for x in hex_rgb(h)]; hh, l, s = colorsys.rgb_to_hls(r, g, b); hh = (hh + grados / 360) % 1; l = max(0, min(1, l + luz))
    r, g, b = colorsys.hls_to_rgb(hh, l, s); return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))

# ── universo: la identidad visual única de una canción ──
def universo(e, usados=None, semilla=None, forzar=None):
    """Elige la identidad visual de la canción y evita las combinaciones que ya usaste en otras (usados = lista de firmas)."""
    usados = set(usados or []); forzar = forzar or {}
    base = semilla if semilla is not None else int(hashlib.md5((str(e.get("numero") or e.get("titulo") or "") + str(random.random())).encode()).hexdigest()[:8], 16)
    fam = e.get("familia") or "Pop"; pal0 = PALETAS.get(fam) or PALETAS["Pop"]
    for intento in range(60):
        r = random.Random(base + intento * 7919)
        est = forzar.get("estilo_letra") or r.choice(list(ESTILOS_LETRA)); st = ESTILOS_LETRA[est]
        fu = forzar.get("fuente") or r.choice(st["fuentes"]); fu = fuente_ok(fu)
        grado = forzar.get("grade") or r.choice(list(GRADES)); gr = r.choice([0, 25, 50, 90, 140, 200, 260, 310]); pal = tuple(desplazar(c, gr, 0) for c in pal0)
        pos = forzar.get("pos") or r.choice([st["pos"], st["pos"], "abajo", "centro"])
        firma = f"{est}|{fu}|{grado}|{gr}|{pos}"
        if firma not in usados or intento == 59: break
    return {"firma": firma, "estilo_letra": est, "estilo_nombre": st["nombre"], "fuente": fu, "paleta": list(pal), "grade": grado, "grade_nombre": GRADES[grado][0], "pos": pos,
            "anim": forzar.get("anim") or st["anim"], "grano": int(forzar.get("grano", r.choice([0, 4, 8, 12]))), "vineta": round(r.uniform(0.25, 0.6), 2), "barras": bool(forzar.get("barras", True)),
            "movs": [r.choice(MOVS) for _ in range(12)], "trans": r.choice(TRANS), "semilla": base, "mundo": forzar.get("mundo") or ""}

# ── texto: letra a frases con tiempos ──
def frases(letra):
    out = []; sec = ""
    for l in str(letra or "").splitlines():
        l = re.sub(r"\*\*|__", "", l.strip()).strip()
        if not l or l.startswith(("#", "---", "===")) or re.match(r"^\*?\s*(g[eé]nero|estilo|t[ií]tulo|tema|genre|style|title|bpm|tempo|idioma|voz)\s*[:：]", l, re.I) or re.match(r"^[\(\*_].*[\)\*_]$", l): continue
        if l.startswith("["): sec = l.strip("[] ").lower(); out.append(("__sec__", sec)); continue
        out.append(("l", l))
    return out

def _py_voz():
    return os.path.join(os.environ.get("RVC_DIR") or "/Volumes/T5 EVO/IslandCrewAI/herramientas/RVC-WebUI-MacOS", ".venv", "bin", "python")
def _voz_sola(audio, carpeta, prog=None):
    """Separa la voz de la música con Demucs (mucho mejor para que Whisper entienda). Devuelve la ruta del vocals.wav o None."""
    dest = os.path.join(carpeta, "vocals.wav")
    try:
        if os.path.isfile(dest) and os.path.getmtime(dest) >= os.path.getmtime(audio): return dest
    except OSError: pass
    py = _py_voz()
    if not os.path.isfile(py): return None
    tmp = os.path.join(carpeta, "demucs-tmp"); shutil.rmtree(tmp, ignore_errors=True)
    try:
        if prog: prog(3, "Separando la voz de la música para sincronizar bien la letra (1-3 minutos)…")
        r = subprocess.run([py, "-m", "demucs", "--two-stems=vocals", "-o", tmp, "-n", "htdemucs", audio], capture_output=True, text=True, timeout=1500, env={**os.environ, "OMP_NUM_THREADS": "4", "KMP_DUPLICATE_LIB_OK": "TRUE", "PYTORCH_ENABLE_MPS_FALLBACK": "1"})
        for raiz, _, fs in os.walk(tmp):
            if "vocals.wav" in fs: shutil.copy(os.path.join(raiz, "vocals.wav"), dest); shutil.rmtree(tmp, ignore_errors=True); return dest
    except Exception: pass
    shutil.rmtree(tmp, ignore_errors=True); return None
def intervalos_voz(wav16k):
    """Tramos [(ini, fin)] en los que realmente se canta (energía de la pista de voz)."""
    try:
        import numpy as np
        raw = subprocess.run(["ffmpeg", "-loglevel", "error", "-i", wav16k, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"], capture_output=True).stdout
        x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
        if len(x) < 8000: return []
        h = 800; n = len(x) // h; e = np.sqrt((x[:n * h].reshape(n, h) ** 2).mean(axis=1))
        umbral = max(0.004, float(np.percentile(e, 90)) * 0.12); vivo = e > umbral
        out = []; ini = None
        for i, v in enumerate(vivo):
            if v and ini is None: ini = i
            if not v and ini is not None:
                if i - ini >= 2: out.append([ini * 0.1, i * 0.1])
                ini = None
        if ini is not None: out.append([ini * 0.1, n * 0.1])
        fus = []
        for a, b in out:   # une pausas cortas (< 0.8 s)
            if fus and a - fus[-1][1] < 0.8: fus[-1][1] = b
            else: fus.append([a, b])
        return [(a, b) for a, b in fus if b - a >= 0.4]
    except Exception: return []
def silabas(t): return max(1, len(re.findall(r"[aeiouyáéíóúüàèìòùäöâêîôû]+", t.lower())))
def tiempos(letra, dur, intro=None, desfase=0.0, voz=None):
    """Reparte las frases a lo largo de la parte cantada de la canción (según sus sílabas). Es una estimación: el desfase y el inicio se pueden ajustar."""
    fr = frases(letra); ls = [x for x in fr if x[0] == "l"]
    if not ls: return []
    intro = intro if intro is not None else max(4.0, min(14.0, dur * 0.07)); fin = dur - max(4.0, dur * 0.06); span = max(8.0, fin - intro)
    peso = [];
    for tipo, t in fr:
        peso.append(3.0 if tipo == "__sec__" else float(silabas(t)) + 1.5)
    tot = sum(peso)
    if voz and sum(b - a for a, b in voz) > 8:   # reparte sobre el tiempo REAL en que se canta, no sobre toda la canción
        V = sum(b - a for a, b in voz); acum = 0.0; out = []
        def pos(s):
            s = max(0.0, min(V, s))
            for a, b in voz:
                if s <= b - a: return a + s
                s -= (b - a)
            return voz[-1][1]
        for (tipo, tx), p in zip(fr, peso):
            d = V * p / tot
            if tipo == "l": out.append({"texto": tx, "ini": round(pos(acum) + desfase, 2), "fin": round(max(pos(acum) + 1.2, pos(acum + d) - 0.1) + desfase, 2)})
            acum += d
        return out
    t0 = intro + desfase; out = []
    for (tipo, t), p in zip(fr, peso):
        d = span * p / tot
        if tipo == "l": out.append({"texto": t, "ini": round(t0, 2), "fin": round(t0 + max(1.4, d - 0.15), 2)})
        t0 += d
    return out


# ── sincronía real: Whisper escucha la canción y se casa con la letra conocida ──
def _norm(t):
    import unicodedata
    t = unicodedata.normalize("NFD", str(t).lower()); t = "".join(c for c in t if unicodedata.category(c) != "Mn"); return re.sub(r"[^a-z0-9]", "", t)
def _tokens_linea(l): return [w for w in (_norm(x) for x in l.split()) if w]
def _casar(lineas, pal, dur):
    """Casa las palabras que se oyen con las frases de la letra (aunque haya errores) y devuelve ([{texto, ini, fin}], acierto)."""
    import difflib
    ly = []; idx_linea = []
    for i, l in enumerate(lineas):
        for tk in _tokens_linea(l): ly.append(tk); idx_linea.append(i)
    if not ly: return None
    sm = difflib.SequenceMatcher(None, ly, [p[0] for p in pal], autojunk=False); mapa = {}
    for b in sm.get_matching_blocks():
        for k in range(b.size): mapa[b.a + k] = b.b + k
    acierto = len(mapa) / max(1, len(ly)); ini = [None] * len(lineas); fin_l = [None] * len(lineas); primero = {}; arranque = {}
    for i, li in enumerate(idx_linea): arranque.setdefault(li, i)
    for a_, b_ in sorted(mapa.items()):
        li = idx_linea[a_]; pos = a_ - arranque[li]; t_ini = pal[b_][1] - pos * 0.32
        if li not in primero: primero[li] = t_ini
        fin_l[li] = max(fin_l[li] or 0, pal[b_][2])
    for li, t in primero.items(): ini[li] = max(0.0, t)
    conocidos = [i for i, v in enumerate(ini) if v is not None]
    if not conocidos: return None
    w = [silabas(x) + 1.5 for x in lineas]
    for i in range(len(lineas)):   # frases sin coincidencias: se reparten entre las conocidas según sus sílabas
        if ini[i] is not None: continue
        a_ = max([c for c in conocidos if c < i], default=None); b_ = min([c for c in conocidos if c > i], default=None)
        if a_ is not None and b_ is not None: ini[i] = ini[a_] + (ini[b_] - ini[a_]) * sum(w[a_:i]) / sum(w[a_:b_])
        elif a_ is not None: ini[i] = ini[a_] + sum(w[a_:i]) * 0.38
        else: ini[i] = max(0.0, ini[b_] - sum(w[i:b_]) * 0.38)
    for i in range(1, len(ini)): ini[i] = max(ini[i], ini[i - 1] + 0.6)
    tl = []
    for i, l in enumerate(lineas):
        nxt = ini[i + 1] if i + 1 < len(ini) else None; est = ini[i] + max(2.4, silabas(l) * 0.32 + 1.0); tope = (nxt - 0.08) if nxt else dur - 0.5; fin = min(tope, est)
        if fin_l[i]: fin = max(fin, min(fin_l[i] + 0.35, tope))
        tl.append({"texto": l, "ini": round(max(0.0, ini[i] - 0.12), 2), "fin": round(max(fin, ini[i] + 1.2), 2)})
    return tl, acierto
def alinear(audio, letra, idioma, cache, dur, prog=None, modelo="small"):
    """Devuelve ([{texto, ini, fin}], acierto 0-1) escuchando el audio, o (None, motivo) si no se puede."""
    lineas = [t for k, t in frases(letra) if k == "l"]
    if not lineas: return None, "sin letra"
    clave = hashlib.md5((str(os.path.getsize(audio)) + str(int(os.path.getmtime(audio))) + letra + modelo + "v3vad").encode()).hexdigest()
    try:
        c = json.load(open(cache))
        if c.get("clave") == clave: return c["tl"], c["acierto"]
    except Exception: pass
    try: from faster_whisper import WhisperModel
    except Exception as ex: return None, "falta el reconocedor de voz (faster-whisper)"
    try:
        wav = os.path.join(os.path.dirname(cache), "voz16k.wav"); fuente = _voz_sola(audio, os.path.dirname(cache), prog); sep = bool(fuente); fuente = fuente or audio; subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", fuente, "-ac", "1", "-ar", "16000", wav], check=True)
        if prog: prog(3, "Escuchando la canción para sincronizar la letra (la primera vez descarga el modelo de voz, unos 500 MB)…")
        m = WhisperModel(modelo, device="cpu", compute_type="int8"); lang = {"es": "es", "en": "en", "it": "it", "de": "de", "pt": "pt", "fr": "fr"}.get(idioma)
        def oir(prompt):
            segs, _ = m.transcribe(wav, language=lang, word_timestamps=True, initial_prompt=prompt, condition_on_previous_text=False, beam_size=5, vad_filter=sep, vad_parameters={"min_silence_duration_ms": 600}, temperature=0.0); out = []
            for sg in segs:
                if prog and dur: prog(3 + int(2 * min(1, sg.end / dur)), f"Escuchando la canción… {int(sg.end)} s de {int(dur)} s")
                for w in (sg.words or []):
                    n = _norm(w.word)
                    if n: out.append((n, float(w.start), float(w.end)))
            lim = []   # quita alucinaciones: la misma palabra repetida muchas veces seguidas
            for i, w in enumerate(out):
                if i >= 4 and all(out[j][0] == w[0] for j in range(i - 4, i)): continue
                if i + 4 < len(out) and all(out[j][0] == w[0] for j in range(i, i + 5)): continue
                lim.append(w)
            return lim
        mejor = (None, 0.0)
        for prompt in (None, " ".join(lineas)[:380]):   # primero sin pista (tiempos más exactos); con la letra de pista solo si no se entiende
            pal = oir(prompt)
            if len(pal) >= 4:
                r_ = _casar(lineas, pal, dur)
                if r_ and r_[1] > mejor[1]: mejor = r_
            if mejor[1] >= 0.55: break
    except Exception as ex: return None, "no pude escuchar la canción: " + str(ex)[:100]
    if mejor[0] is None: return None, "no se entendió casi nada de la voz o la letra no coincide"
    tl, acierto = mejor
    try: json.dump({"clave": clave, "tl": tl, "acierto": acierto}, open(cache, "w"))
    except Exception: pass
    return tl, acierto

# ── dibujo de las frases ──
def _color(st, pal, nombre):
    return {"blanco": (246, 244, 238), "acento": hex_rgb(desplazar(pal[1], 0, 0.18)), "claro": hex_rgb(pal[2]), "dorado": (233, 196, 106)}.get(nombre, (246, 244, 238))
def _ajustar(draw, texto, kf, tam0, ancho, esp):
    for tam in range(int(tam0), 18, -3):
        f = cargar_fuente(kf, tam); pal = texto.split(); lineas = []; cur = ""
        for w in pal:
            prueba = (cur + " " + w).strip()
            if draw.textlength(prueba, font=f) + esp * len(prueba) <= ancho: cur = prueba
            else:
                if cur: lineas.append(cur)
                cur = w
        if cur: lineas.append(cur)
        if len(lineas) <= 3: return f, lineas, tam
    return f, lineas, tam
def render_frase(texto, uni, W, H, tam_base=None, ancla=None):
    """Devuelve (imagen RGBA de una franja con la frase ya estilizada, y su alto)."""
    st = ESTILOS_LETRA[uni["estilo_letra"]]; pal = uni["paleta"]; banda_h = int(H * 0.36); im = Image.new("RGBA", (W, banda_h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    t = texto.upper() if st["mayus"] else texto; tam0 = (tam_base or H * 0.062) * st["tam"]; esp = st["esp"]
    f, lineas, tam = _ajustar(d, t, uni["fuente"], tam0, W * (0.84 if W > H else 0.88), esp); col = _color(st, pal, st["color"])
    alto_l = int(tam * 1.18); total = alto_l * len(lineas); ancla = ancla or uni.get("pos", "centro"); mg = int(H * 0.035)
    y0 = {"abajo": banda_h - total - mg, "izquierda": banda_h - total - mg, "arriba": mg}.get(ancla, (banda_h - total) // 2); y0 = max(0, y0)
    capa_brillo = Image.new("RGBA", im.size, (0, 0, 0, 0)); db = ImageDraw.Draw(capa_brillo); capa_sombra = Image.new("RGBA", im.size, (0, 0, 0, 0)); ds = ImageDraw.Draw(capa_sombra)
    def x_de(l):
        w = d.textlength(l, font=f) + esp * max(0, len(l) - 1)
        return int(W * 0.07) if uni["pos"] == "izquierda" else int((W - w) / 2)
    def escribir(dr, x, y, l, fill, stroke=0, sfill=None):
        if esp:
            xx = x
            for ch in l: dr.text((xx, y), ch, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill); xx += dr.textlength(ch, font=f) + esp
        else: dr.text((x, y), l, font=f, fill=fill, stroke_width=stroke, stroke_fill=sfill)
    for i, l in enumerate(lineas):
        x = x_de(l); y = y0 + i * alto_l
        escribir(ds, x + 3, y + 5, l, (0, 0, 0, 200));
        if st["brillo"]: escribir(db, x, y, l, col + (255,))
    capa_sombra = capa_sombra.filter(ImageFilter.GaussianBlur(5)); im.alpha_composite(capa_sombra)
    if st["brillo"]:
        g1 = capa_brillo.filter(ImageFilter.GaussianBlur(14 * st["brillo"] + 4)); g2 = capa_brillo.filter(ImageFilter.GaussianBlur(5)); im.alpha_composite(g1); im.alpha_composite(g1); im.alpha_composite(g2)
    for i, l in enumerate(lineas):
        x = x_de(l); y = y0 + i * alto_l
        if st.get("vhs"): escribir(d, x - 4, y, l, (255, 40, 60, 170)); escribir(d, x + 4, y, l, (0, 230, 255, 170))
        sf = hex_rgb(pal[1]) + (255,) if st["trazo"] else None
        escribir(d, x, y, l, col + (255,), st["trazo"], sf)
    return im, banda_h
def render_tarjeta(l1, l2, uni, W, H, pie=None):
    """Tarjeta de título o de créditos."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im); pal = uni["paleta"]; st = ESTILOS_LETRA[uni["estilo_letra"]]
    t1 = l1.upper() if st["mayus"] else l1; f, lin, tam = _ajustar(d, t1, uni["fuente"], H * 0.1, W * 0.8, st["esp"]); alto = int(tam * 1.2); y = int(H * 0.40) - alto * len(lin) // 2
    for i, l in enumerate(lin):
        w = d.textlength(l, font=f); d.text(((W - w) / 2 + 3, y + i * alto + 4), l, font=f, fill=(0, 0, 0, 190)); d.text(((W - w) / 2, y + i * alto), l, font=f, fill=_color(st, pal, st["color"]) + (255,))
    y += alto * len(lin) + int(H * 0.025)
    for extra, k, ts in ((l2, "barlow", H * 0.036), (pie, "barlow", H * 0.026)):
        if not extra: continue
        f2 = cargar_fuente(k, int(ts));
        for linea in str(extra).split("\n"):
            w = d.textlength(linea, font=f2); d.text(((W - w) / 2, y), linea, font=f2, fill=hex_rgb(pal[2]) + (235,)); y += int(ts * 1.5)
        y += int(H * 0.01)
    return im
def logo_im(alto):
    try:
        lg = Image.open(LOGO).convert("RGBA"); lg.thumbnail((alto, alto), Image.LANCZOS); return lg
    except Exception: return None

# ── imágenes de las escenas ──
def imagen_escena(prompt, semilla, W, H, timeout=110):
    try:
        w, h = (1280, 720) if W >= H else (720, 1280)
        url = f"https://image.pollinations.ai/prompt/{urllib.parse.quote(prompt[:800])}?width={w}&height={h}&nologo=true&seed={semilla}"
        datos = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "CabraBeats/1.0"}), timeout=timeout).read(); im = Image.open(io.BytesIO(datos)); im.load()
        return im.convert("RGB").crop((0, 0, im.width, int(im.height * 0.95)))
    except Exception: return None
def ajustar_cover(im, W, H):
    r = max(W / im.width, H / im.height); im = im.resize((int(im.width * r) + 1, int(im.height * r) + 1), Image.LANCZOS); x = (im.width - W) // 2; y = (im.height - H) // 2; return im.crop((x, y, x + W, y + H))
def escenas_prompts(llm, e, uni, n):
    """La IA local describe el mundo visual de la canción y n escenas distintas de ese mundo."""
    titulo = e.get("titulo", ""); estilo = e.get("estilo", ""); letra = (e.get("letra") or "")[:1500]; animo = ", ".join((e.get("ops") or {}).get("animo") or [])
    pr = (f"You are a film director making a music video. Song: «{titulo}», style: {estilo}, mood: {animo or 'free'}. Lyrics:\n{letra}\n\n"
          f"Invent a UNIQUE visual universe for this video (a specific world, era, place, color mood) and {n} cinematic shots of it, each different (wide, close-up, detail, silhouette, aerial...). "
          "Shots must follow the story/emotion of the lyrics and share the same look. No text, no letters, no logos, no real celebrities. Each shot max 28 words, in English, concrete visuals. "
          "Answer ONLY JSON: {\"mundo\":\"short name of the universe in Spanish\",\"estetica\":\"one short English phrase of the look\",\"escenas\":[\"...\"]}")
    try:
        t = llm(pr, 0.95); m = re.search(r"\{.*\}", t, re.S); d = json.loads(m.group(0)); sc = [str(x) for x in d.get("escenas", []) if str(x).strip()]
        if len(sc) >= 2: return str(d.get("mundo") or ""), str(d.get("estetica") or ""), (sc * 3)[:n]
    except BaseException: pass  # sin IA local: escenas genéricas (SystemExit también)
    base = ["wide cinematic establishing shot", "close-up portrait, shallow depth of field", "silhouette against glowing light", "detail shot of hands and objects", "night street with light trails", "aerial view at golden hour"]
    return "", f"{estilo} music video, {animo}", [f"{titulo}, {b}" for b in (base * 3)[:n]]

# ── montaje con ffmpeg ──
def _run(cmd, progreso=None, total=None, base=0, ancho=100):
    p = subprocess.Popen(cmd + ["-progress", "pipe:1", "-nostats"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True); ult = []
    for l in p.stdout:
        ult = (ult + [l.strip()])[-8:]
        if progreso and total and l.startswith("out_time_us="):
            try: progreso(int(base + ancho * min(1.0, int(l.split("=")[1]) / 1e6 / total)))
            except Exception: pass
    if p.wait() != 0: raise RuntimeError("ffmpeg falló: " + " | ".join(ult)[-300:])
def segmento(img, mov, dur, W, H, salida):
    n = max(2, int(dur * FPS)); S = f"{W}x{H}"; k = 1.5; w2, h2 = int(W * k), int(H * k)
    z = {"zoom_in": f"z='1+0.2*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'", "zoom_out": f"z='1.2-0.2*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'",
         "pan_izq": f"z='1.18':x='(iw-iw/zoom)*(1-on/{n})':y='ih/2-(ih/zoom/2)'", "pan_der": f"z='1.18':x='(iw-iw/zoom)*on/{n}':y='ih/2-(ih/zoom/2)'"}[mov]
    vf = f"scale={w2}:{h2}:force_original_aspect_ratio=increase,crop={w2}:{h2},zoompan={z}:d={n}:s={S}:fps={FPS},format=yuv420p"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", img, "-vf", vf, "-frames:v", str(n), "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", salida])
def montar(audio, letra, e, uni, salida, trabajo, formato="h", previa=False, llm=None, fallback=None, progreso=None, idioma="es", n_escenas=8, intro=None, desfase=0.0, reusar=True, dur_audio=None):
    """Crea el videoclip. trabajo = carpeta de trabajo de esta canción (guarda las escenas para no repetirlas)."""
    prog = progreso or (lambda p, m="": None); os.makedirs(trabajo, exist_ok=True); esc_dir = os.path.join(trabajo, "escenas"); os.makedirs(esc_dir, exist_ok=True)
    W, H = (1920, 1080) if formato == "h" else (1080, 1920)
    if previa: W, H = W // 2, H // 2
    dur = dur_audio or float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", audio], capture_output=True, text=True).stdout.strip() or 0)
    if dur < 5: raise RuntimeError("No pude leer la duración del audio.")
    sync = "estimada"; tl = None; aviso = ""
    if letra.strip() and "[instrumental]" not in letra.lower():
        tl, ac = alinear(audio, letra, idioma, os.path.join(trabajo, "alineacion.json"), dur, prog)
        if tl is None: aviso = str(ac)
        elif ac < 0.25: aviso = f"la voz se entendió poco (acierto {int(ac * 100)} %)"; tl = None
        else: sync = f"exacta ({int(ac * 100)} % de acierto)"; tl = [dict(x, ini=round(x["ini"] + desfase, 2), fin=round(x["fin"] + desfase, 2)) for x in tl]
    if tl is None:
        vw = os.path.join(trabajo, "voz16k.wav")
        iv = intervalos_voz(vw) if os.path.isfile(vw) and os.path.isfile(os.path.join(trabajo, "vocals.wav")) else []
        tl = tiempos(letra, dur, intro, desfase, iv or None)
        if iv: sync = "estimada sobre la voz detectada"
    t0 = 0.0; T = dur
    if previa and tl: t0 = max(0.0, tl[0]["ini"] - 2.5); T = min(24.0, dur - t0)
    tl = [dict(x, ini=round(x["ini"] - t0, 2), fin=round(x["fin"] - t0, 2)) for x in tl if x["fin"] > t0 and x["ini"] < t0 + T]
    for x in tl: x["ini"] = max(0.0, x["ini"]); x["fin"] = min(T - 0.2, x["fin"])
    n = 3 if previa else max(3, min(14, int(n_escenas))); xf = 1.0; d = (T + (n - 1) * xf) / n
    # 1) escenas (IA gratuita; si no hay internet, arte propio)
    prog(2, "Imaginando el universo de la canción…"); metaf = os.path.join(esc_dir, "universo.json"); pr = None
    if reusar and os.path.isfile(metaf):
        try: pr = json.load(open(metaf))
        except Exception: pr = None
    if not pr or len(pr.get("escenas", [])) < n:
        mundo, estetica, sc = escenas_prompts(llm, e, uni, max(n, 8)) if llm else ("", "", [e.get("titulo", "") + " cinematic"] * max(n, 8)); pr = {"mundo": mundo, "estetica": estetica, "escenas": sc}
        for f in os.listdir(esc_dir):
            if f.endswith(".jpg"): os.remove(os.path.join(esc_dir, f))
        json.dump(pr, open(metaf, "w"), ensure_ascii=False)
    if not uni.get("mundo"): uni["mundo"] = pr.get("mundo") or ""
    imgs = []; buenas = []; fallos = 0; tmp = os.path.join(trabajo, "tmp"); shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    for i in range(n):
        p = os.path.join(esc_dir, f"{i:02d}-{'h' if W >= H else 'v'}.jpg")
        if os.path.isfile(p): imgs.append(p); buenas.append(p); continue
        prog(4 + int(30 * i / n), f"Creando la escena {i + 1} de {n} con IA…"); im = None; base_p = f"{pr['escenas'][i % len(pr['escenas'])]}, {pr.get('estetica', '')}, cinematic lighting, film still, highly detailed"
        for intento in range(4):
            im = imagen_escena(base_p if intento < 2 else pr['escenas'][i % len(pr['escenas'])], uni["semilla"] % 100000 + i * 13 + intento * 101, W, H, timeout=120)
            if im is not None: break
            prog(4 + int(30 * i / n), f"La escena {i + 1} tarda: reintento {intento + 2} de 4…"); time.sleep(4 + intento * 5)
        if im is not None: ajustar_cover(im.convert("RGB"), W, H).save(p, quality=92); imgs.append(p); buenas.append(p); continue
        fallos += 1; q = os.path.join(tmp, f"rel{i}.jpg")   # relleno: NO se guarda en la caché, así la próxima vez se reintenta con IA
        if buenas:
            o = Image.open(random.Random(i).choice(buenas)).convert("RGB"); r = random.Random(uni["semilla"] + i); z = r.uniform(0.62, 0.8); w2, h2 = int(o.width * z), int(o.height * z)
            x = r.randint(0, o.width - w2); y = r.randint(0, o.height - h2); o = o.crop((x, y, x + w2, y + h2)).resize((W, H), Image.LANCZOS)
            if r.random() < 0.5: o = o.transpose(Image.FLIP_LEFT_RIGHT)
            o.save(q, quality=92)
        else:
            g = fallback(e.get("titulo", ""), tuple(uni["paleta"]), uni["semilla"] + i) if fallback is not None else None
            ajustar_cover((g or Image.new("RGB", (W, H), hex_rgb(uni["paleta"][0]))).convert("RGB"), W, H).save(q, quality=92)
        imgs.append(q)
    # 2) fondo en movimiento
    segs = []
    for i, p in enumerate(imgs):
        prog(36 + int(14 * i / n), f"Moviendo la cámara en la escena {i + 1} de {n}…"); s = os.path.join(tmp, f"s{i}.mp4"); segmento(p, uni["movs"][i % len(uni["movs"])], d, W, H, s); segs.append(s)
    bg = os.path.join(tmp, "fondo.mp4")
    if n == 1: shutil.copy(segs[0], bg)
    else:
        cmd = ["ffmpeg", "-y", "-loglevel", "error"]; [cmd.extend(["-i", s]) for s in segs]; fc = ""; prev = "[0:v]"
        for i in range(1, n):
            out = f"[x{i}]" if i < n - 1 else "[vout]"; fc += f"{prev}[{i}:v]xfade=transition={uni['trans']}:duration={xf}:offset={round(i * (d - xf), 3)}{out};"; prev = out
        _run(cmd + ["-filter_complex", fc.rstrip(";"), "-map", "[vout]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "17", "-pix_fmt", "yuv420p", bg])
    # 3) letras, tarjetas y acabado de cine
    prog(52, "Escribiendo la letra sobre las imágenes…"); piezas = []   # (png, ini, fin, anim, ypos)
    banda = int(H * 0.36)
    for i, x in enumerate(tl):
        im, bh = render_frase(x["texto"], uni, W, H); p = os.path.join(tmp, f"l{i}.png"); im.save(p)
        barra = int((H - W / 2.39) / 2) if (uni["barras"] and W > H) else 0
        y = {"abajo": H - bh - barra - int(H * 0.02), "centro": (H - bh) // 2, "izquierda": H - bh - barra - int(H * 0.04), "arriba": barra + int(H * 0.04)}.get(uni["pos"], H - bh - barra)
        piezas.append((p, x["ini"], x["fin"], uni["anim"], y))
    tit = render_tarjeta(e.get("titulo", ""), e.get("artista") or "", uni, W, H, "Island Crew Music · Cabra Beats"); pt = os.path.join(tmp, "titulo.png"); tit.save(pt)
    if t0 == 0.0 or not previa: piezas.append((pt, 0.9, min(5.0, T * 0.4), "fundido", 0))
    cred = render_tarjeta("Obra original de Maximiliano Olmos Sánchez", f"Creada con Cabra Beats · Island Crew\n{e.get('numero') or ''}  {e.get('licencia') or ''}".strip(), uni, W, H, "Todos los derechos reservados · hola@islandcrew.es"); pc = os.path.join(tmp, "creditos.png"); cred.save(pc)
    if not previa: piezas.append((pc, max(6.0, T - 6.5), T - 0.4, "fundido", 0))
    lg = logo_im(int(H * 0.16)); plg = None
    if lg is not None: plg = os.path.join(tmp, "logo.png"); lg.save(plg)
    barra = int((H - W / 2.39) / 2) if (uni["barras"] and W > H) else 0
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", bg, "-ss", str(t0), "-t", str(T), "-i", audio]; fc = []
    for k, (p, a, b, an, y) in enumerate(piezas):
        cmd += ["-loop", "1", "-framerate", str(FPS), "-t", str(round(b - a + 0.1, 2)), "-i", p]
    idx0 = 2; grade = GRADES[uni["grade"]][1]
    base = f"[0:v]{grade},vignette=angle=PI/{round(3 + (1 - uni['vineta']) * 4, 1)}"
    if uni["grano"]: base += f",noise=alls={uni['grano']}:allf=t"
    if barra: base += f",drawbox=x=0:y=0:w=iw:h={barra}:color=black:t=fill,drawbox=x=0:y=ih-{barra}:w=iw:h={barra}:color=black:t=fill"
    fc.append(base + "[b0]"); prev = "[b0]"
    for k, (p, a, b, an, y) in enumerate(piezas):
        din = 0.35; dout = 0.4; dd = round(b - a, 2)
        fc.append(f"[{idx0 + k}:v]format=rgba,fade=t=in:st=0:d={din}:alpha=1,fade=t=out:st={max(0.1, round(dd - dout, 2))}:d={dout}:alpha=1,setpts=PTS+{a}/TB[p{k}]")
        ye = {"subida": f"{y}+{int(H * 0.04)}*pow(max(0,1-(t-{a})/0.45),2)", "bajada": f"{y}-{int(H * 0.04)}*pow(max(0,1-(t-{a})/0.45),2)"}.get(an, str(y))
        fc.append(f"{prev}[p{k}]overlay=x=0:y='{ye}':enable='between(t,{a},{b})':eof_action=pass[b{k + 1}]"); prev = f"[b{k + 1}]"
    if plg:
        cmd += ["-i", plg]; li = idx0 + len(piezas); fc.append(f"[{li}:v]format=rgba,colorchannelmixer=aa=0.75[lg]"); fc.append(f"{prev}[lg]overlay=x=W-w-{int(W * 0.025)}:y={barra + int(H * 0.025)}[bl]"); prev = "[bl]"
    fc.append(f"{prev}fade=t=in:st=0:d=0.8,fade=t=out:st={round(T - 1.5, 2)}:d=1.5[vf]"); fc.append(f"[1:a]afade=t=in:st=0:d=0.5,afade=t=out:st={round(T - 1.8, 2)}:d=1.8[af]")
    sc = ";".join(fc)  # directo en la orden: las ffmpeg nuevas ya no aceptan -filter_complex_script
    prog(55, "Montando el vídeo final…"); os.makedirs(os.path.dirname(salida), exist_ok=True); tmp_sal = salida + ".parte.mp4"
    _run(cmd + ["-filter_complex", sc, "-map", "[vf]", "-map", "[af]", "-t", str(T), "-c:v", "libx264", "-preset", "veryfast" if not previa else "ultrafast", "-crf", "21" if not previa else "26", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", tmp_sal], progreso=lambda p: prog(p, "Montando el vídeo final…"), total=T, base=55, ancho=44)
    os.replace(tmp_sal, salida); shutil.rmtree(tmp, ignore_errors=True); prog(100, "Videoclip listo."); return {"mundo": pr.get("mundo", ""), "tiempos": tl, "duracion": round(T, 1), "fallos": fallos, "escenas": n, "sync": sync, "aviso_sync": aviso}

def muestra(e, uni, salida, fondo=None, W=960, H=540, frase=None):
    """Imagen rápida: cómo se vería una frase de la letra con este universo (sin ffmpeg)."""
    if fondo and os.path.isfile(fondo): bg = ajustar_cover(Image.open(fondo).convert("RGB"), W, H)
    else:
        bg = Image.new("RGB", (W, H), hex_rgb(uni["paleta"][0])); d = ImageDraw.Draw(bg)
        for i in range(H): c = tuple(int(a + (b - a) * i / H) for a, b in zip(hex_rgb(uni["paleta"][0]), hex_rgb(uni["paleta"][1]))); d.line([(0, i), (W, i)], fill=c)
    bg = bg.filter(ImageFilter.GaussianBlur(0.5)).convert("RGBA"); fr = frase or next((x[1] for x in frases(e.get("letra")) if x[0] == "l"), e.get("titulo", "Tu canción")); im, bh = render_frase(fr, uni, W, H)
    barra = int((H - W / 2.39) / 2) if uni.get("barras", True) else 0
    y = {"abajo": H - bh - barra - int(H * 0.02), "centro": (H - bh) // 2, "izquierda": H - bh - barra - int(H * 0.04), "arriba": barra + int(H * 0.04)}.get(uni["pos"], H - bh - barra)
    bg.alpha_composite(im, (0, max(0, y)))
    if barra: d = ImageDraw.Draw(bg); d.rectangle([0, 0, W, barra], fill=(0, 0, 0, 255)); d.rectangle([0, H - barra, W, H], fill=(0, 0, 0, 255))
    os.makedirs(os.path.dirname(salida), exist_ok=True); bg.convert("RGB").save(salida, quality=90); return salida

if __name__ == "__main__":
    print(__doc__)
