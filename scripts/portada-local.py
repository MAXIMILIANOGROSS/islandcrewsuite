#!/usr/bin/env python3
"""PORTADAS de Cabra Beats Personal: foto → portada lista para todas las plataformas, con transformación por estilo, arte generativo,
imagen creada con IA a partir de la letra (opcional) y fusión. Usa solo Pillow (y un servicio gratuito de imágenes si lo pides; si falla, arte generativo local)."""
import os, io, re, random, hashlib, math, json, urllib.parse, urllib.request
from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageDraw, ImageFont, ImageChops

LADO = 3000
FUENTES = ["/System/Library/Fonts/Supplemental/Impact.ttf", "/System/Library/Fonts/Supplemental/Arial Black.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc", "/Library/Fonts/Arial Bold.ttf",
           "/usr/share/fonts/truetype/lato/Lato-Black.ttf", "/usr/share/fonts/truetype/lato/Lato-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
FUENTES_FINAS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/lato/Lato-Medium.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
AQUI = os.path.dirname(os.path.abspath(__file__)); FUENTES_DIR = os.path.join(AQUI, "fuentes"); LOGO = os.path.join(AQUI, "..", "public", "brand", "island-crew-logo-cv.png")
AMARILLO = (255, 212, 0)
def fmarca(nombre, tam):
    """Tipografías de la marca Island Crew (Bebas Neue, Permanent Marker, Barlow, Archivo Black)."""
    try: return ImageFont.truetype(os.path.join(FUENTES_DIR, nombre), tam)
    except Exception: return fuente(tam, nombre.startswith("Barlow"))
def fuente(tam, fina=False):
    for f in (FUENTES_FINAS if fina else FUENTES):
        if os.path.exists(f):
            try: return ImageFont.truetype(f, tam)
            except Exception: pass
    return ImageFont.load_default()

# Paleta (oscuro, medio, claro) y mirada por familia de estilo
PALETAS = {"Pop": ("#2b0a4a", "#ff4fa3", "#ffe66b"), "Rock": ("#0d0d0d", "#c1121f", "#f1f1f1"), "Urbano y hip hop": ("#0a0a14", "#7a3cff", "#ffd60a"), "Electrónica": ("#02041c", "#00e5ff", "#ff2bd6"),
           "Latino y tropical": ("#3a0d00", "#ff7a00", "#ffe14d"), "Raíces y folk": ("#2d1b0e", "#c98a3b", "#f5ecd7"), "Reggae y mundo": ("#06280f", "#f2b705", "#e63946"), "Jazz, soul y funk": ("#1b0f2e", "#c77d0a", "#f4e3c1"),
           "Cine, clásica y ambiente": ("#05060f", "#3a6ea5", "#e9eef7"), "Para negocios": ("#0f2a2e", "#2ec4b6", "#fff1d0"), "Estilos de Island Crew": ("#04101f", "#0ea5e9", "#fde047")}
MIRADA = {"Pop": "neon", "Rock": "noir", "Urbano y hip hop": "duotono", "Electrónica": "glitch", "Latino y tropical": "pop", "Raíces y folk": "vintage", "Reggae y mundo": "vintage", "Jazz, soul y funk": "vintage", "Cine, clásica y ambiente": "sueno", "Para negocios": "duotono", "Estilos de Island Crew": "duotono"}
MIRADAS = ["auto", "original", "noir", "neon", "vintage", "comic", "sueno", "glitch", "duotono", "pop"]
def hexrgb(h): h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))

def cuadrada(im, lado=LADO):
    im = ImageOps.exif_transpose(im).convert("RGB"); return ImageOps.fit(im, (lado, lado), Image.LANCZOS, centering=(0.5, 0.4))
def duotono(im, pal):
    g = ImageOps.autocontrast(ImageOps.grayscale(im)); return ImageOps.colorize(g, hexrgb(pal[0]), hexrgb(pal[2]), mid=hexrgb(pal[1]))
def look(im, nombre, pal, r):
    if nombre == "original": return im
    if nombre == "noir":
        g = ImageOps.autocontrast(ImageOps.grayscale(im), cutoff=2); g = ImageEnhance.Contrast(g).enhance(1.5); out = ImageOps.colorize(g, (5, 5, 8), (245, 245, 240), mid=(110, 110, 112)); return out.filter(ImageFilter.UnsharpMask(8, 120, 3))
    if nombre == "neon":
        base = ImageEnhance.Color(im).enhance(1.8); base = ImageEnhance.Contrast(base).enhance(1.25); d = duotono(im, pal); out = Image.blend(base, d, 0.45)
        glow = out.filter(ImageFilter.GaussianBlur(LADO // 60)); return ImageChops.screen(out, ImageEnhance.Brightness(glow).enhance(0.8))
    if nombre == "vintage":
        s = ImageEnhance.Color(im).enhance(0.6); s = ImageEnhance.Contrast(s).enhance(0.9); tinte = Image.new("RGB", im.size, (214, 160, 98)); out = Image.blend(s, tinte, 0.28)
        ru = Image.effect_noise(im.size, 38).convert("RGB"); out = Image.blend(out, ru, 0.07); return out
    if nombre == "comic":
        p = ImageOps.posterize(ImageEnhance.Color(im).enhance(1.6), 3); b = ImageOps.grayscale(im).filter(ImageFilter.FIND_EDGES); b = ImageOps.invert(ImageOps.autocontrast(b)).point(lambda v: 0 if v < 190 else 255).convert("RGB"); return ImageChops.multiply(p, b)
    if nombre == "sueno":
        d = im.filter(ImageFilter.GaussianBlur(LADO // 45)); out = Image.blend(ImageEnhance.Color(im).enhance(1.25), d, 0.55); return ImageEnhance.Brightness(out).enhance(1.08)
    if nombre == "glitch":
        rr, gg, bb = im.split(); d = LADO // 70; rr = ImageChops.offset(rr, -d, 0); bb = ImageChops.offset(bb, d, d // 2); out = Image.merge("RGB", (rr, gg, bb)); out = ImageEnhance.Contrast(out).enhance(1.3)
        dr = ImageDraw.Draw(out)
        for _ in range(26): y = r.randint(0, LADO - 40); h = r.randint(10, 90); dx = r.randint(-250, 250); out.paste(ImageChops.offset(out.crop((0, y, LADO, y + h)), dx, 0), (0, y))
        return out
    if nombre == "pop":
        out = ImageEnhance.Color(im).enhance(2.2); out = ImageOps.posterize(out, 4); return ImageEnhance.Contrast(out).enhance(1.3)
    return duotono(im, pal)  # duotono

def arte_generativo(titulo, pal, semilla):
    """Arte propio, siempre distinto: degradado + formas grandes + grano. Nunca falla (no necesita internet)."""
    r = random.Random(semilla); a, m, c = (hexrgb(x) for x in pal); W = LADO
    fondo = Image.new("RGB", (W, W)); px = ImageDraw.Draw(fondo)
    for y in range(0, W, 6): t = y / W; col = tuple(int(a[i] * (1 - t) + m[i] * t) for i in range(3)); px.rectangle([0, y, W, y + 6], fill=col)
    capa = Image.new("RGBA", (W, W), (0, 0, 0, 0)); d = ImageDraw.Draw(capa)
    for _ in range(r.randint(7, 12)):
        col = r.choice([m, c, a]) + (r.randint(55, 150),); x, y, s = r.randint(-300, W), r.randint(-300, W), r.randint(300, 1400); forma = r.choice(["o", "o", "r", "t"])
        if forma == "o": d.ellipse([x, y, x + s, y + s], fill=col)
        elif forma == "r": d.rounded_rectangle([x, y, x + s, y + int(s * r.uniform(.3, 1))], radius=r.randint(20, 300), fill=col)
        else: d.polygon([(x, y + s), (x + s // 2, y), (x + s, y + s)], fill=col)
    out = Image.alpha_composite(fondo.convert("RGBA"), capa.filter(ImageFilter.GaussianBlur(r.randint(4, 40)))).convert("RGB")
    sol = Image.new("RGBA", (W, W), (0, 0, 0, 0)); ds = ImageDraw.Draw(sol); cx, cy, rr = r.randint(W // 4, 3 * W // 4), r.randint(W // 5, W // 2), r.randint(380, 620); ds.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=c + (230,))
    out = Image.alpha_composite(out.convert("RGBA"), sol.filter(ImageFilter.GaussianBlur(6))).convert("RGB")
    return Image.blend(out, Image.effect_noise((W, W), 30).convert("RGB"), 0.06)

def imagen_ia(prompt, semilla, timeout=100):
    """Imagen creada por IA gratuita a partir del texto (servicio en internet). Devuelve None si no hay conexión o falla."""
    try:
        q = urllib.parse.quote(prompt[:900]); url = f"https://image.pollinations.ai/prompt/{q}?width=1024&height=1024&nologo=true&seed={semilla}"
        datos = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "CabraBeats/1.0"}), timeout=timeout).read()
        im = Image.open(io.BytesIO(datos)); im.load(); im = im.crop((0, 0, im.width, int(im.height * 0.93))); return cuadrada(im)  # se recorta la franja inferior donde el servicio pone su marca
    except Exception: return None

def fusionar(base, otra, fuerza):
    """Mezcla suave: la imagen de IA entra por tono y luz, sin borrar la cara/objeto de la foto."""
    f = max(0.0, min(1.0, fuerza)); suave = Image.blend(base, otra, f * 0.75)
    return Image.blend(suave, ImageChops.soft_light(base, otra), min(1.0, f))
def viñeta(im, fuerza=0.55):
    W = im.size[0]; m = Image.radial_gradient("L").resize((W, W)); m = ImageOps.invert(m).point(lambda v: int(v * fuerza)); neg = Image.new("RGB", im.size, (0, 0, 0)); return Image.composite(neg, im, m)

def ajustar(draw, texto, ancho_max, tam, fina=False, minimo=80):
    f = fuente(tam, fina)
    while tam > minimo and draw.textlength(texto, font=f) > ancho_max: tam -= 20; f = fuente(tam, fina)
    return f, tam
def con_texto(im, titulo, artista, pal, numero=None):
    """Diseño de sello Island Crew: logo de la cabra arriba, título en Bebas Neue, artista en Permanent Marker amarillo, pie con el nº de registro."""
    W = im.size[0]; out = im.copy().convert("RGBA"); marg = int(W * .06)
    deg = Image.new("RGBA", (W, W), (0, 0, 0, 0)); dd = ImageDraw.Draw(deg)
    for y in range(int(W * .50), W): t = (y - W * .50) / (W * .50); dd.line([(0, y), (W, y)], fill=(0, 0, 0, int(225 * t ** 1.3)))
    for y in range(0, int(W * .22)): dd.line([(0, y), (W, y)], fill=(0, 0, 0, int(120 * (1 - y / (W * .22)))))
    out = Image.alpha_composite(out, deg); d = ImageDraw.Draw(out); ancho = W - 2 * marg
    # logo de la cabra (esquina superior izquierda) con sombra
    try:
        lg = Image.open(LOGO).convert("RGBA"); lg = lg.crop(lg.getbbox()); lado = int(W * .20); lg = lg.resize((lado, int(lado * lg.height / lg.width)), Image.LANCZOS)
        sh = Image.new("RGBA", out.size, (0, 0, 0, 0)); sh.paste((0, 0, 0, 150), (marg + 10, marg + 14), lg.split()[3]); out = Image.alpha_composite(out, sh.filter(ImageFilter.GaussianBlur(14))); out.alpha_composite(lg, (marg, marg)); d = ImageDraw.Draw(out)
    except Exception: pass
    # sello superior derecho
    f_tag = fmarca("Barlow-SemiBold.ttf", int(W * .028)); tag = "ISLAND CREW MUSIC"; tw = d.textlength(tag, font=f_tag); d.text((W - marg - tw + 4, marg + 6), tag, font=f_tag, fill=(0, 0, 0, 170)); d.text((W - marg - tw, marg), tag, font=f_tag, fill=AMARILLO + (255,))
    y = W - marg
    if numero: f_n = fmarca("Barlow-SemiBold.ttf", int(W * .024)); bb = d.textbbox((0, 0), numero, font=f_n); y -= (bb[3] - bb[1]); d.text((marg, y), numero, font=f_n, fill=(255, 255, 255, 190)); y -= int(W * .03)
    if artista:
        f_a = fmarca("PermanentMarker-Regular.ttf", int(W * .075)); t_a = artista.strip()
        while d.textlength(t_a, font=f_a) > ancho and f_a.size > int(W * .04): f_a = fmarca("PermanentMarker-Regular.ttf", f_a.size - 8)
        bb = d.textbbox((0, 0), t_a, font=f_a); y -= (bb[3] - bb[1]); d.text((marg + 7, y + 7), t_a, font=f_a, fill=(0, 0, 0, 200)); d.text((marg, y), t_a, font=f_a, fill=AMARILLO + (255,)); y -= int(W * .03)
    t = (titulo or "").upper().strip(); tam = int(W * .17); lineas = [t]
    f = fmarca("BebasNeue-Regular.ttf", tam)
    while d.textlength(t, font=f) > ancho and tam > int(W * .10): tam -= 14; f = fmarca("BebasNeue-Regular.ttf", tam)
    if d.textlength(t, font=f) > ancho and " " in t:
        pal_ = t.split(); mitad = len(pal_) // 2 or 1; lineas = [" ".join(pal_[:mitad]), " ".join(pal_[mitad:])]; tam = int(W * .13); f = fmarca("BebasNeue-Regular.ttf", tam)
        while max(d.textlength(l, font=f) for l in lineas) > ancho and tam > int(W * .05): tam -= 10; f = fmarca("BebasNeue-Regular.ttf", tam)
    for l in reversed(lineas):
        bb = d.textbbox((0, 0), l, font=f); h = bb[3] - bb[1]; y -= h; d.text((marg + 9, y + 9), l, font=f, fill=(0, 0, 0, 200)); d.text((marg, y), l, font=f, fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255)); y -= int(W * .012)
    return out.convert("RGB")

def crear(carpeta, titulo, artista, familia, estilo_nombre, foto=None, mirada="auto", otra_imagen=None, fuerza=0.4, semilla=None, numero=None):
    """Devuelve {nombre: ruta}. foto: ruta o None. otra_imagen: PIL (p. ej. de la IA) para fusionar. Salida lista para todas las plataformas."""
    os.makedirs(carpeta, exist_ok=True); sem = semilla if semilla is not None else int(hashlib.md5((titulo + str(random.random())).encode()).hexdigest()[:8], 16); r = random.Random(sem)
    pal = PALETAS.get(familia) or PALETAS["Pop"]; mir = MIRADA.get(familia, "duotono") if mirada in ("", "auto", None) else mirada
    if foto and os.path.exists(foto): base = look(cuadrada(Image.open(foto)), mir, pal, r)
    else: base = arte_generativo(titulo, pal, sem)
    if otra_imagen is not None: base = fusionar(base, otra_imagen, fuerza) if (foto and os.path.exists(foto)) else Image.blend(base, otra_imagen, 0.7)
    base = viñeta(ImageEnhance.Contrast(base).enhance(1.05), .5); sin = base.copy(); con = con_texto(base, titulo, artista, pal, numero); res = {}
    def g(n, im, **kw): p = os.path.join(carpeta, n); im.save(p, **kw); res[n] = p
    g("portada-3000-con-texto.jpg", con, quality=95, subsampling=0, dpi=(300, 300)); g("portada-3000-sin-texto.jpg", sin, quality=95, subsampling=0, dpi=(300, 300))
    g("portada-1400-spotify.jpg", con.resize((1400, 1400), Image.LANCZOS), quality=92)
    yt = Image.new("RGB", (1280, 720), (0, 0, 0)); fondo = ImageOps.fit(sin, (1280, 720), Image.LANCZOS).filter(ImageFilter.GaussianBlur(26)); yt.paste(ImageEnhance.Brightness(fondo).enhance(.55), (0, 0)); yt.paste(con.resize((720, 720), Image.LANCZOS), (280, 0)); g("youtube-1280x720.jpg", yt, quality=92)
    hist = Image.new("RGB", (1080, 1920), (0, 0, 0)); fh = ImageOps.fit(sin, (1080, 1920), Image.LANCZOS).filter(ImageFilter.GaussianBlur(30)); hist.paste(ImageEnhance.Brightness(fh).enhance(.5), (0, 0)); hist.paste(con.resize((1000, 1000), Image.LANCZOS), (40, 460)); g("historia-1080x1920.jpg", hist, quality=92)
    g("instagram-1080x1350.jpg", ImageOps.fit(con, (1080, 1350), Image.LANCZOS, centering=(0.5, 0.5)), quality=92)
    return res
