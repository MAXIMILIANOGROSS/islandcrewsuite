#!/usr/bin/env python3
"""Carta Viva — fábrica de cartas de restaurante con un vídeo por plato. Todo local, coste cero.
Uso: python3 scripts/carta-viva/carta-viva-app.py   ·   Parar: --parar"""
import os, sys, json, re, time, base64, secrets, shutil, subprocess, threading, socket, io, urllib.request, urllib.error, html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote
AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
sys.path.insert(0, os.path.join(AQUI, "vendor")); sys.path.insert(0, os.path.join(AQUI, "..", "suite"))
import core
INFO = os.path.expanduser("~/IslandCrewAI/carta-viva-app.json"); TOKEN = secrets.token_hex(16)
BASE = os.path.join(core.carpeta_datos(), "cartas")
FFMPEG = core.ffmpeg()
ALERGENOS = ["gluten", "crustáceos", "huevos", "pescado", "cacahuetes", "soja", "lácteos", "frutos de cáscara", "apio", "mostaza", "sésamo", "sulfitos", "altramuces", "moluscos"]
EST = {"msg": "", "t": 0, "trabajando": False, "log": []}
LOCK = threading.Lock()

def slug(s): return re.sub(r"[^a-z0-9]+", "-", (s or "").lower().encode("ascii", "ignore").decode() or "x").strip("-") or "x"
def dir_r(r): return os.path.join(BASE, slug(r))
def leer(r):
    p = os.path.join(dir_r(r), "carta.json")
    return json.load(open(p, encoding="utf8")) if os.path.exists(p) else None
def guardar(r, c):
    os.makedirs(dir_r(r), exist_ok=True); p = os.path.join(dir_r(r), "carta.json"); tmp = p + ".tmp"
    json.dump(c, open(tmp, "w", encoding="utf8"), ensure_ascii=False, indent=1); os.replace(tmp, p)
def listar():
    os.makedirs(BASE, exist_ok=True); out = []
    for d in sorted(os.listdir(BASE)):
        c = leer(d)
        if c: out.append({"id": d, "nombre": c.get("nombre", d), "platos": len(c.get("platos", []))})
    return out
def estado(m, trabajando=None):
    EST["msg"] = m; EST["t"] = time.time()
    if trabajando is not None: EST["trabajando"] = trabajando
    EST["log"] = (EST["log"] + [m])[-12:]

# ---------- IA gratis (Gemini) ----------
def clave():
    return core.clave("GEMINI_API_KEY", RAIZ)
def gemini(prompt, foto=None):
    k = clave()
    if not k: raise RuntimeError("Falta la clave gratuita de Gemini (Ajustes > Claves de IA).")
    partes = [{"text": prompt}]
    if foto and os.path.exists(foto):
        from PIL import Image
        im = Image.open(foto).convert("RGB"); im.thumbnail((768, 768)); b = io.BytesIO(); im.save(b, "JPEG", quality=80)
        partes.append({"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(b.getvalue()).decode()}})
    cuerpo = json.dumps({"contents": [{"parts": partes}], "generationConfig": {"temperature": 0.7, "responseMimeType": "application/json"}}).encode()
    ult = []
    for modelo in ("gemini-2.5-flash", "gemini-3.1-flash-lite", "gemini-2.5-flash-lite", "gemini-flash-latest"):
        for i in range(2):
            try:
                rq = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{modelo}:generateContent", cuerpo, {"Content-Type": "application/json", "x-goog-api-key": k})
                r = json.load(urllib.request.urlopen(rq, timeout=30))
                t = r["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(re.sub(r"^```(?:json)?|```$", "", t.strip()).strip())
            except urllib.error.HTTPError as e:
                ult.append(f"{modelo}:{e.code}")
                if e.code in (429, 503) and i == 0: time.sleep(2); continue
                break
            except Exception as e: ult.append(f"{modelo}:{str(e)[:60]}"); break
    g = groq(prompt)
    if g is not None: return g
    raise RuntimeError("La IA gratis no responde ahora (" + ", ".join(ult[-4:]) + "). Prueba en un minuto.")
def groq(prompt):
    k = core.clave("GROQ_API_KEY", RAIZ)
    if not k: return None
    try:
        rq = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", json.dumps({"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}, "temperature": 0.7}).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + k, "User-Agent": "carta-viva"})
        return json.loads(json.load(urllib.request.urlopen(rq, timeout=30))["choices"][0]["message"]["content"])
    except Exception: return None
def ia_plato(p, rest, campos):
    base = f"Eres jefe de sala de un restaurante ('{rest}'). Plato: nombre='{p.get('nombre','')}', categoría='{p.get('categoria','')}', descripción actual='{p.get('descripcion','')}'. Mira la foto si hay. Responde SOLO JSON con las claves pedidas, en {__import__('marca').lengua()}, cálido, apetecible, sin inventar ingredientes que no se vean o no sean evidentes. "
    pedir = {"nombre": '"nombre": nombre corto y atractivo del plato (máx 5 palabras)', "descripcion": '"descripcion": descripción de 1-2 frases (máx 30 palabras)',
             "categoria": '"categoria": una de Entrantes, Principales, Carnes, Pescados, Arroces, Postres, Bebidas u otra corta', "alergenos": '"alergenos": lista con los alérgenos probables SOLO de esta lista: ' + ", ".join(ALERGENOS)}
    r = gemini(base + "Claves: " + "; ".join(pedir[c] for c in campos), p.get("foto_path"))
    out = {}
    for c in campos:
        if c in r:
            v = r[c]
            if c == "alergenos": v = [a for a in (v if isinstance(v, list) else []) if a in ALERGENOS]
            out[c] = v
    return out

# ---------- fotos y vídeo ----------
def guardar_foto(r, pid, b64):
    from PIL import Image, ImageOps
    d = os.path.join(dir_r(r), "fotos"); os.makedirs(d, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(io.BytesIO(base64.b64decode(b64.split(",")[-1])))).convert("RGB"); im.thumbnail((2400, 2400))
    im.save(os.path.join(d, pid + ".jpg"), "JPEG", quality=90); return pid + ".jpg"
FUENTES = ["/System/Library/Fonts/Supplemental/Didot.ttc", "/System/Library/Fonts/Supplemental/Georgia.ttf", "/System/Library/Fonts/Helvetica.ttc", "C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/times.ttf", "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
VERSION_VIDEO = "|cine9"
def marca_de(d):
    try: c = json.load(open(os.path.join(d, "carta.json"), encoding="utf8"))
    except Exception: c = {}
    ac = (c.get("color_acento") or "#e8b25c").lstrip("#")
    try: rgb = tuple(int(ac[i:i + 2], 16) for i in (0, 2, 4))
    except Exception: rgb = (232, 178, 92)
    lg = os.path.join(d, "marca", "logo.png"); fd = os.path.join(d, "marca", "fondo.jpg")
    return {"fuente": c.get("fuente_titulos") or "clasica", "acento": rgb, "hex": "#%02x%02x%02x" % rgb, "logo": lg if os.path.exists(lg) else None, "fondo": fd if os.path.exists(fd) else None}
def clave_video(p, d):
    m = marca_de(d); mk = "|".join(str(os.path.getmtime(x)) for x in (m["fondo"],) if x) + m["fuente"]
    p = dict(p); p["_m"] = mk
    return p["foto"] + str(os.path.getmtime(os.path.join(d, "fotos", p["foto"]))) + VERSION_VIDEO + "|" + "|".join(str(p.get(k, "")) for k in ("mov", "radio", "cx", "cy", "nombre", "precio", "_m", "fotos"))
def _fuente(tam, ini=0, pref=None):
    from PIL import ImageFont
    for f in (FUENTES_PIL.get(pref, []) if pref else []) + FUENTES[ini:]:
        try: return ImageFont.truetype(f, tam)
        except Exception: pass
    return ImageFont.load_default()
def quitar_blanco(im):
    """Si el logo trae fondo blanco (sin transparencia), lo vuelve transparente."""
    from PIL import Image, ImageDraw
    im = im.convert("RGBA"); a = im.getchannel("A")
    if a.getextrema()[0] < 250: return im
    rgb = im.convert("RGB"); w, h = rgb.size
    if not all(min(rgb.getpixel(p)) > 225 for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1))): return im
    for p in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)): ImageDraw.floodfill(rgb, p, (255, 0, 255), thresh=60)
    px = rgb.load(); out = im.copy(); op = out.load()
    for y in range(h):
        for x in range(w):
            if px[x, y] == (255, 0, 255): op[x, y] = (255, 255, 255, 0)
    return out
def hacer_video(r, p, idx=0):
    """Foto → vídeo de cine vertical 9:16 de 8 s, sin sonido: separa plato y fondo (paralaje), cámara lenta,
    desenfoque que se enfoca, color de película, brillo suave, grano, viñeta y rótulo final con nombre y precio. Gratis con ffmpeg."""
    from PIL import Image, ImageDraw, ImageFilter
    d = dir_r(r); foto = os.path.join(d, "fotos", p["foto"]); vd = os.path.join(d, "videos"); os.makedirs(vd, exist_ok=True)
    W, H = 1080, 1920; K = 1.3; CW, CH = int(W * K), int(H * K)
    im = Image.open(foto).convert("RGB"); im0 = im; s = max(CW / im.width, CH / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
    L, T = (im.width - CW) // 2, (im.height - CH) // 2; im = im.crop((L, T, L + CW, T + CH))
    mk_ = marca_de(d); AC = (226, 189, 104, 255); tid = p["id"]; f_bg = os.path.join(vd, "_bg_" + tid + ".jpg"); f_fg = os.path.join(vd, "_fg_" + tid + ".png"); f_tx = os.path.join(vd, "_tx_" + tid + ".png")
    im.filter(ImageFilter.GaussianBlur(26)).point(lambda v: int(v * 0.8)).save(f_bg, "JPEG", quality=90)
    m = Image.new("L", (CW, CH), 0); ImageDraw.Draw(m).ellipse((CW * 0.12, CH * 0.27, CW * 0.88, CH * 0.73), fill=255)
    fg = im.convert("RGBA"); fg.putalpha(m.filter(ImageFilter.GaussianBlur(90))); fg.save(f_fg)
    tx = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(tx)
    for y in range(H - 640, H):
        dr.line((0, y, W, y), fill=(0, 0, 0, int(215 * ((y - (H - 640)) / 640) ** 1.6)))
    nombre = (p.get("nombre") or "").upper(); fn = _fuente(76, 0, mk_["fuente"])
    while dr.textlength(nombre, font=fn) > W - 140 and fn.size > 36: fn = _fuente(fn.size - 4, 0, mk_["fuente"])
    dr.text((W / 2, H - 300), nombre, font=fn, fill=(246, 236, 220, 255), anchor="mm")
    dr.line((W / 2 - 70, H - 245, W / 2 + 70, H - 245), fill=AC, width=3)
    pr = str(p.get("precio") or "").strip()
    if pr: dr.text((W / 2, H - 190), pr + ("" if pr.endswith("€") else " €"), font=_fuente(60, 1), fill=AC, anchor="mm")
    tx.save(f_tx)
    F = 200
    fts = [x for x in (p.get("fotos") or []) if os.path.exists(os.path.join(d, "fotos", x))]
    if len(fts) >= 3 and (p.get("mov") or "orbita") == "orbita":
        N = len(fts) + 1; xd = 0.5; cl = (8 + (N - 1) * xd) / N; fr = max(int(cl * 25) + 2, 20); ent = []; fcs = []
        for k, fn in enumerate(fts + [fts[0]]):
            im3 = Image.open(os.path.join(d, "fotos", fn)).convert("RGB"); s3 = max(W * 1.15 / im3.width, H * 1.15 / im3.height)
            im3 = im3.resize((int(im3.width * s3) + 1, int(im3.height * s3) + 1), Image.LANCZOS); l3, t3 = (im3.width - int(W * 1.15)) // 2, (im3.height - int(H * 1.15)) // 2
            im3 = im3.crop((l3, t3, l3 + int(W * 1.15), t3 + int(H * 1.15))); fp = os.path.join(vd, f"_o{k}_{tid}.jpg"); im3.save(fp, "JPEG", quality=92); ent.append(fp)
            fcs.append(f"[{k}:v]format=yuv420p,zoompan=z='1.0+0.0':x='(iw-iw/zoom)*(1-on/{fr})':y='ih/2-(ih/zoom/2)':d={fr}:s={W}x{H}:fps=25,setsar=1[z{k}]")
        cad = "[z0]"; off = 0.0
        for k in range(1, N):
            off += cl - xd; sal = f"[x{k}]"; fcs.append(f"{cad}[z{k}]xfade=transition=smoothleft:duration={xd}:offset={off:.3f}{sal}"); cad = sal
        fcs.append(f"{cad}eq=contrast=1.1:saturation=1.18:brightness=-0.02,colorbalance=rs=0.06:bs=0.08:gs=-0.02:rh=0.08:bh=-0.07,split[a][c];[c]gblur=sigma=28,eq=brightness=-0.1[c2];[a][c2]blend=all_mode=screen:all_opacity=0.2,vignette=PI/4.2,noise=alls=9:allf=t,format=yuv420p[v1];[{N}:v]format=rgba,fade=t=in:st=0.3:d=0.7:alpha=1[t];[v1][t]overlay=format=auto,format=yuv420p")
        cmd = [FFMPEG, "-y", "-loglevel", "error"]
        for fp in ent: cmd += ["-framerate", "25", "-loop", "1", "-t", f"{cl + 0.2:.2f}", "-i", fp]
        cmd += ["-framerate", "25", "-loop", "1", "-t", "9", "-i", f_tx, "-filter_complex", ";".join(fcs), "-t", "8", "-r", "25", "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", os.path.join(vd, tid + ".mp4")]
        c = subprocess.run(cmd, capture_output=True, text=True)
        for x in ent + [f_bg, f_fg, f_tx]:
            try: os.remove(x)
            except Exception: pass
        if c.returncode: raise RuntimeError("ffmpeg: " + (c.stderr or "")[-300:])
        pd = os.path.join(d, "fotos"); pi = Image.open(foto).convert("RGB"); pi.thumbnail((540, 960)); pi.save(os.path.join(pd, "p_" + tid + ".jpg"), "JPEG", quality=70)
        return tid + ".mp4"
    if (p.get("mov") or "giro") == "giro":
        R = int(W * float(p.get("radio") or 38) / 100); cx = min(max(int(W * float(p.get("cx") or 50) / 100), R), W - R); cy = min(max(int(H * float(p.get("cy") or 50) / 100), R), H - R)
        ss = max(W / im0.width, H / im0.height); i2 = im0.resize((int(im0.width * ss) + 1, int(im0.height * ss) + 1), Image.LANCZOS)
        l2, t2 = (i2.width - W) // 2, (i2.height - H) // 2; i2 = i2.crop((l2, t2, l2 + W, t2 + H))
        if mk_["fondo"]:
            fb = Image.open(mk_["fondo"]).convert("RGB"); sf = max(W / fb.width, H / fb.height); fb = fb.resize((int(fb.width * sf) + 1, int(fb.height * sf) + 1), Image.LANCZOS)
            lf, tf = (fb.width - W) // 2, (fb.height - H) // 2; fb.crop((lf, tf, lf + W, tf + H)).point(lambda v: int(v * 0.85)).save(f_bg, "JPEG", quality=90)
        else: i2.filter(ImageFilter.GaussianBlur(16)).point(lambda v: int(v * 0.72)).save(f_bg, "JPEG", quality=90)
        disco = i2.crop((cx - R, cy - R, cx + R, cy + R)).convert("RGBA"); mk = Image.new("L", (2 * R, 2 * R), 0); ImageDraw.Draw(mk).ellipse((R * 0.06, R * 0.06, R * 1.94, R * 1.94), fill=255)
        disco.putalpha(mk.filter(ImageFilter.GaussianBlur(R * 0.07))); disco.save(f_fg)
        fc = (f"[0:v]format=yuv420p,zoompan=z='min(1.0+0.0006*on,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={F}:s={W}x{H}:fps=25[b];"
              f"[1:v]format=rgba,rotate=a='2*PI*t/8':ow={2*R}:oh={2*R}:c=0x00000000,scale=w='{2*R}*(1+0.05*t/8)':h=-1:eval=frame[f];"
              f"[b][f]overlay=x='{cx}-w/2':y='{cy}-h/2':format=auto,format=yuv420p,eq=contrast=1.1:saturation=1.18:brightness=-0.02,"
              f"colorbalance=rs=0.06:bs=0.08:gs=-0.02:rh=0.08:bh=-0.07,split[a][c];[c]gblur=sigma=28,eq=brightness=-0.1[c2];"
              f"[a][c2]blend=all_mode=screen:all_opacity=0.2,vignette=PI/4.2,noise=alls=9:allf=t,"
              f"{'' if mk_['fondo'] else 'fade=t=in:st=0:d=0.8,fade=t=out:st=7.5:d=0.5,'}format=yuv420p[v1];"
              f"[2:v]format=rgba,fade=t=in:st=0.3:d=0.7:alpha=1[t];[v1][t]overlay=format=auto,format=yuv420p")
        out = os.path.join(vd, tid + ".mp4")
        c = subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-framerate", "25", "-loop", "1", "-i", f_bg, "-framerate", "25", "-loop", "1", "-i", f_fg, "-framerate", "25", "-loop", "1", "-i", f_tx, "-filter_complex", fc, "-frames:v", str(F), "-r", "25", "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", out], capture_output=True, text=True)
        for x in (f_bg, f_fg, f_tx):
            try: os.remove(x)
            except Exception: pass
        if c.returncode or not os.path.exists(out): raise RuntimeError("ffmpeg: " + (c.stderr or "")[-300:])
        pd = os.path.join(d, "fotos"); pi = Image.open(foto).convert("RGB"); pi.thumbnail((540, 960)); pi.save(os.path.join(pd, "p_" + tid + ".jpg"), "JPEG", quality=70)
        return tid + ".mp4"
    mv = idx % 3
    zb = ["min(1.0+0.0007*on,1.14)", "max(1.14-0.0007*on,1.0)", "min(1.04+0.0005*on,1.14)"][mv]; zf = ["min(1.0+0.0013*on,1.26)", "max(1.26-0.0013*on,1.0)", "min(1.06+0.001*on,1.26)"][mv]
    xb = ["iw/2-(iw/zoom/2)", f"(iw-iw/zoom)*(1-on/{F})", f"(iw-iw/zoom)*on/{F}"][mv]; xf = ["iw/2-(iw/zoom/2)", f"(iw-iw/zoom)*on/{F}", f"(iw-iw/zoom)*(1-on/{F})"][mv]
    y = "ih/2-(ih/zoom/2)"
    fc = (f"[0:v]format=yuv420p,zoompan=z='{zb}':x='{xb}':y='{y}':d={F}:s={W}x{H}:fps=25[b];"
          f"[1:v]format=rgba,zoompan=z='{zf}':x='{xf}':y='{y}':d={F}:s={W}x{H}:fps=25[f];"
          f"[b][f]overlay=format=auto,format=yuv420p,eq=contrast=1.1:saturation=1.18:brightness=-0.02,"
          f"colorbalance=rs=0.06:bs=0.08:gs=-0.02:rh=0.08:bh=-0.07,split[a][c];[c]gblur=sigma=28,eq=brightness=-0.1[c2];"
          f"[a][c2]blend=all_mode=screen:all_opacity=0.22,vignette=PI/4.2,noise=alls=9:allf=t,"
          f"fade=t=in:st=0:d=0.8,fade=t=out:st=7.5:d=0.5,format=yuv420p[v1];"
          f"[2:v]format=rgba,fade=t=in:st=0.3:d=0.7:alpha=1[t];[v1][t]overlay=format=auto,format=yuv420p")
    out = os.path.join(vd, tid + ".mp4")
    c = subprocess.run([FFMPEG, "-y", "-loglevel", "error", "-loop", "1", "-i", f_bg, "-loop", "1", "-i", f_fg, "-loop", "1", "-i", f_tx, "-filter_complex", fc, "-frames:v", str(F), "-r", "25", "-c:v", "libx264", "-preset", "medium", "-crf", "24", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", out], capture_output=True, text=True)
    for x in (f_bg, f_fg, f_tx):
        try: os.remove(x)
        except Exception: pass
    if c.returncode or not os.path.exists(out): raise RuntimeError("ffmpeg: " + (c.stderr or "")[-300:])
    pd = os.path.join(d, "fotos"); pi = Image.open(foto).convert("RGB"); pi.thumbnail((540, 960)); pi.save(os.path.join(pd, "p_" + tid + ".jpg"), "JPEG", quality=70)
    return tid + ".mp4"

# ---------- carta web + QR ----------
CSS = """*{box-sizing:border-box;margin:0}body{background:#0f0d0b;color:#f4efe8;font:16px/1.5 system-ui,-apple-system,sans-serif}header{padding:28px 18px 12px;text-align:center}h1{font:700 30px Georgia,serif;letter-spacing:.5px}.sub{opacity:.6;font-size:14px;margin-top:4px}nav{position:sticky;top:0;z-index:5;background:#0f0d0bee;backdrop-filter:blur(8px);display:flex;gap:8px;overflow-x:auto;padding:10px 14px}nav a{flex:none;color:#f4efe8;text-decoration:none;border:1px solid #ffffff30;border-radius:99px;padding:6px 14px;font-size:14px}main{max-width:520px;margin:0 auto;padding:6px 14px 60px}h2{font:700 22px Georgia,serif;margin:26px 0 12px;color:#e8b25c}.plato{margin-bottom:26px;border-radius:18px;overflow:hidden;background:#1a1612}.vid{position:relative;aspect-ratio:9/16;background:#000}.vid video,.vid img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.info{padding:14px 16px 18px}.fila{display:flex;justify-content:space-between;gap:12px;align-items:baseline}.nom{font:700 19px Georgia,serif}.pre{font-weight:700;color:#e8b25c;white-space:nowrap}.desc{opacity:.8;margin-top:6px;font-size:15px}.al{opacity:.55;font-size:12px;margin-top:8px}footer{text-align:center;opacity:.4;font-size:12px;padding:24px}"""
JS = """const o=new IntersectionObserver(es=>es.forEach(e=>{const v=e.target;if(e.isIntersecting){if(!v.src)v.src=v.dataset.src;v.play().catch(()=>{})}else v.pause()}),{threshold:.55});document.querySelectorAll('video').forEach(v=>o.observe(v));"""
def esc(s): return html.escape(str(s or ""))
ICONOS = {"gluten": "🌾", "crustáceos": "🦐", "huevos": "🥚", "pescado": "🐟", "cacahuetes": "🥜", "soja": "🫘", "lácteos": "🥛", "frutos de cáscara": "🌰", "apio": "🥬", "mostaza": "🟡", "sésamo": "⚪", "sulfitos": "🍷", "altramuces": "🌼", "moluscos": "🐚"}
CSS2 = """*{box-sizing:border-box;margin:0;-webkit-tap-highlight-color:transparent}html{scroll-behavior:smooth}body{background:#0f0d0b;color:#f4efe8;font:16px/1.5 system-ui,-apple-system,sans-serif}
.hero{text-align:center;padding:38px 18px 18px}.lg{max-width:190px;max-height:100px;margin-bottom:12px}h1{font:700 clamp(28px,6vw,44px) Georgia,serif;letter-spacing:.5px}.hero p{opacity:.65;margin-top:6px}
nav{position:sticky;top:0;z-index:5;background:#0f0d0bec;backdrop-filter:blur(10px);display:flex;gap:8px;overflow-x:auto;padding:10px 14px;scrollbar-width:none;justify-content:safe center}nav::-webkit-scrollbar{display:none}
nav a{flex:none;color:#f4efe8;text-decoration:none;border:1px solid #ffffff30;border-radius:99px;padding:7px 16px;font-size:14px;transition:.2s}nav a.on{background:__AC__;border-color:__AC__;color:#17110a;font-weight:700}
main{max-width:1040px;margin:0 auto;padding:4px 14px 40px}section{scroll-margin-top:62px}h2{font:700 24px Georgia,serif;margin:28px 2px 14px;color:__AC__;display:flex;align-items:center;gap:12px}h2:after{content:"";flex:1;height:1px;background:__AC__55}
.g{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}@media(min-width:640px){.g{grid-template-columns:repeat(3,1fr)}}@media(min-width:960px){.g{grid-template-columns:repeat(4,1fr)}}
.card{all:unset;cursor:pointer;display:block;background:#1a1612ee;border-radius:16px;overflow:hidden;transition:transform .2s,box-shadow .2s}.card:hover{transform:translateY(-3px);box-shadow:0 10px 30px #0008}.card:focus-visible{outline:2px solid __AC__}
.v{position:relative;aspect-ratio:9/16;background:#000}.v video,.v img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.v i{position:absolute;right:8px;top:8px;background:#000a;border-radius:99px;font:normal 11px system-ui;padding:3px 9px}
.t{padding:10px 12px 12px}.d{font-size:13px;opacity:.75;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;min-height:2.9em}.al{margin-top:6px;font-size:15px;letter-spacing:2px}
footer{text-align:center;opacity:.4;font-size:12px;padding:22px}
#vw{position:fixed;inset:0;z-index:20;background:#050403f2;display:none;flex-direction:column;align-items:center}#vw.on{display:flex}
#vw .st{position:relative;flex:1;min-height:0;aspect-ratio:9/16;max-width:100%;margin-top:10px;border-radius:16px;overflow:hidden;background:#000}#vw video{width:100%;height:100%;object-fit:cover}
#vw .in{width:min(560px,100%);padding:12px 20px 18px;text-align:center}#vw .nm{font:700 22px Georgia,serif}#vw .pr{color:__AC__;font-weight:700}#vw .ds{opacity:.85;margin:6px 0}#vw .ax{font-size:13px;opacity:.75}
#vw button{position:absolute;background:#000a;color:#fff;border:0;border-radius:99px;width:46px;height:46px;font-size:22px;cursor:pointer;z-index:2}#x{top:14px;right:14px}#pv{left:max(10px,calc(50% - 330px));top:45%}#nx{right:max(10px,calc(50% - 330px));top:45%}#ct{position:absolute;top:22px;left:50%;transform:translateX(-50%);font-size:13px;opacity:.7;z-index:2}"""
JS2 = """const V=document.querySelectorAll('.card video');const o=new IntersectionObserver(es=>es.forEach(e=>{const v=e.target;if(e.isIntersecting){if(!v.src)v.src=v.dataset.src;v.play().catch(()=>{})}else v.pause()}),{threshold:.5});V.forEach(v=>o.observe(v));
const nv=document.querySelectorAll('nav a');nv.forEach(a=>a.onclick=ev=>{ev.preventDefault();const t=document.getElementById(vista+'-'+a.dataset.k);t&&t.scrollIntoView({behavior:'smooth'})});const tp=document.getElementById('tp'),tg=document.getElementById('tg');function ver(v){vista=v;document.getElementById('pp').hidden=v!='p';document.getElementById('gv').hidden=v!='g';document.getElementById('hr').hidden=v!='g';tp.classList.toggle('on',v=='p');tg.classList.toggle('on',v=='g');scrollTo(0,0)}tp.onclick=()=>ver('p');tg.onclick=()=>ver('g');const ZZ=0,sc=[...document.querySelectorAll('section')];const so=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){nv.forEach(a=>a.classList.toggle('on',a.dataset.k==e.target.id.slice(2)));const a=document.querySelector('nav a.on');a&&a.scrollIntoView({inline:'center',block:'nearest'})}}),{rootMargin:'-20% 0px -70% 0px'});sc.forEach(s=>so.observe(s));
let k=0;const w=document.getElementById('vw'),vv=document.getElementById('vv');
function show(i){k=(i+D.length)%D.length;const p=D[k];document.getElementById('ct').textContent=(k+1)+' / '+D.length;document.getElementById('nm').textContent=p.n;document.getElementById('pr').textContent=p.p;document.getElementById('ds').textContent=p.d;document.getElementById('ax').textContent=p.a;if(p.v){vv.poster=p.f;vv.src=p.v;vv.play().catch(()=>{})}else{vv.removeAttribute('src');vv.poster=p.f}}
function open_(i){w.classList.add('on');document.body.style.overflow='hidden';show(i)}function close_(){w.classList.remove('on');vv.pause();document.body.style.overflow=''}
document.querySelectorAll('.card').forEach(c=>c.onclick=()=>open_(+c.dataset.i));document.getElementById('x').onclick=close_;document.getElementById('pv').onclick=()=>show(k-1);document.getElementById('nx').onclick=()=>show(k+1);
addEventListener('keydown',e=>{if(!w.classList.contains('on'))return;if(e.key=='Escape')close_();if(e.key=='ArrowRight')show(k+1);if(e.key=='ArrowLeft')show(k-1)});
let x0=null;w.addEventListener('touchstart',e=>x0=e.touches[0].clientX,{passive:true});w.addEventListener('touchend',e=>{if(x0===null)return;const dx=e.changedTouches[0].clientX-x0;if(Math.abs(dx)>50)show(k+(dx<0?1:-1));x0=null});"""
CSS3 = """body{background:radial-gradient(120% 90% at 50% 0%,#33241a 0%,#17110c 55%,#0b0806 100%) fixed}
.tb{display:flex;justify-content:center;gap:8px;padding:6px 14px 12px}.tb button{all:unset;cursor:pointer;border:1px solid #d4a94f66;border-radius:99px;padding:8px 20px;font:14px Georgia,serif;letter-spacing:1px;color:#ecd9a8}.tb button.on{background:linear-gradient(#e2bd68,#c4983f);border-color:#e2bd68;color:#2a1c0c;font-weight:700}
nav a{border-color:#d4a94f55!important;font-family:Georgia,serif}nav a.on{background:linear-gradient(#e2bd68,#c4983f)!important;border-color:#e2bd68!important;color:#2a1c0c!important}
#pp{max-width:1000px;margin:0 auto;padding:6px 12px 40px}
.libro{display:flex;align-items:stretch;border-radius:10px;box-shadow:0 20px 70px #000c,0 0 0 1px #d4a94f88,0 0 0 5px #1b1410,0 0 0 6px #d4a94f55}
.hoja{position:relative;flex:1;min-width:0;border-radius:10px 0 0 10px;background:#f5ecd8 url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='200' height='200'><filter id='n'><feTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='2'/><feColorMatrix values='0 0 0 0 .35 0 0 0 0 .25 0 0 0 0 .1 0 0 0 .09 0'/></filter><rect width='200' height='200' filter='url(%23n)'/></svg>");color:#2b2118;padding:34px 24px 34px;box-shadow:inset 0 0 70px #b0905033;font-family:Georgia,'Times New Roman',serif}
.hoja:before{content:"";position:absolute;inset:10px;border:1px solid #b8924a99;pointer-events:none;border-radius:3px}.hoja:after{content:"";position:absolute;inset:14px;border:1px solid #b8924a44;pointer-events:none;border-radius:2px}
.calado{height:14px;margin:-8px -4px 16px;background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='28' height='14'><path d='M14 1 L25 7 L14 13 L3 7Z' fill='none' stroke='%23b8743a' stroke-width='1.2'/><path d='M14 4.5 L19.5 7 L14 9.5 L8.5 7Z' fill='%23b8924a'/></svg>") repeat-x center}
.hoja .cab{text-align:center;margin-bottom:8px}.hoja .cab img{max-width:150px;max-height:80px;margin-bottom:6px}.hoja h1{font:700 clamp(24px,5vw,38px) Georgia,serif;letter-spacing:3px;text-transform:uppercase;color:#2b2118}.hoja .lm{font-style:italic;opacity:.7;margin-top:2px}
.orn{display:flex;align-items:center;gap:10px;margin:14px 0 2px}.orn:before,.orn:after{content:"";flex:1;height:1px;background:linear-gradient(90deg,transparent,#b8924a)}.orn:after{transform:scaleX(-1)}.orn svg{width:26px;height:26px}
.hoja h2{font:700 19px Georgia,serif;letter-spacing:4px;text-transform:uppercase;color:__AD__;text-align:center;margin:26px 0 8px;display:block}.hoja h2:after{display:none}.hoja h2:before{content:"✦ ";color:#b8743a;font-size:12px}
.et{display:inline-block;font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;border:1px solid currentColor;border-radius:99px;padding:1px 8px;margin-right:6px;opacity:.85}.ig{font-size:.8rem;opacity:.7;font-style:italic;margin-top:2px}.pl{padding:9px 8px 9px 12px;border-radius:4px;cursor:pointer;border-left:3px solid transparent;transition:background .25s,border-color .25s}.pl.on{background:#c4983f22;border-left-color:#b8743a}
.pl .f1{display:flex;align-items:baseline;gap:6px}.pl .n{font-weight:700;font-size:16px}.pl .pt{flex:1;border-bottom:2px dotted #2b211855;transform:translateY(-4px);min-width:10px}.pl .pr{font-weight:700;color:__AD__;white-space:nowrap}.pl .ds{font-size:13.5px;font-style:italic;opacity:.78;margin-top:2px}.pl .ic{font-size:13px;letter-spacing:2px;margin-top:2px}.hoja .pie{text-align:center;font-size:11px;letter-spacing:1px;opacity:.6;margin-top:22px;font-style:italic}
.pv2{border-radius:0 10px 10px 0;flex:none;width:min(clamp(130px,40vw,380px),calc((100dvh - 110px)*9/16));background:#150f0a;border-left:1px solid #d4a94faa;padding:0;position:relative}.pv2 .in2{position:sticky;top:60px}.pv2 .mk{position:relative;aspect-ratio:9/16;width:100%;border-radius:0 10px 0 0;overflow:hidden;background:#000}.pv2 video,.pv2 img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover}.pv2 p{display:none}
@media(max-width:520px){.hoja{padding:26px 12px 26px}.pl .n{font-size:14px}.pl .ds{font-size:12px}.pv2{padding:0}.hoja:before{inset:6px}.hoja:after{inset:9px}}"""
PALMA = '<svg viewBox="0 0 32 32" fill="none" stroke="#b8743a" stroke-width="1.6" stroke-linecap="round"><path d="M16 29 C16 22 17 17 16 11"/><path d="M16 11 C11 7 6 8 3 12"/><path d="M16 11 C21 7 26 8 29 12"/><path d="M16 11 C12 4 8 3 5 4"/><path d="M16 11 C20 4 24 3 27 4"/><path d="M16 11 C16 6 16 4 16 2"/></svg>'
PAPEL_JS = """const PL=[...document.querySelectorAll('.pl')],pvv=document.getElementById('pvv'),pvi=document.getElementById('pvi'),pvc=document.getElementById('pvc');let act=-1;
function sel(i){if(i===act||!D[i])return;act=i;PL.forEach(x=>x.classList.toggle('on',+x.dataset.i===i));const p=D[i];pvc.textContent=p.n;if(p.v){pvi.style.display='none';pvv.style.display='block';pvv.poster=p.f;if(pvv.getAttribute('src')!==p.v)pvv.src=p.v;pvv.play().catch(()=>{})}else{pvv.pause();pvv.style.display='none';pvi.style.display='block';pvi.src=p.f}}
PL.forEach(x=>{x.addEventListener('pointerenter',e=>{if(e.pointerType=='mouse')sel(+x.dataset.i)});x.addEventListener('pointermove',e=>{if(e.pointerType=='mouse')sel(+x.dataset.i)});x.addEventListener('click',()=>sel(+x.dataset.i))});
const po=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting&&vista=='p')sel(+e.target.dataset.i)}),{rootMargin:'-38% 0px -50% 0px'});PL.forEach(x=>po.observe(x));
let tt=null;document.getElementById('pp').addEventListener('touchmove',e=>{const t=e.touches[0],el=document.elementFromPoint(t.clientX,t.clientY),l=el&&el.closest&&el.closest('.pl');if(l)sel(+l.dataset.i)},{passive:true});
if(PL.length)sel(0);"""
TEMAS = {
 "canario": {"papel": "#f5ecd8", "tinta": "#2b2118", "marco": "#d4a94f", "acento": "#a8561f", "panel": "#150f0a"},
 "marino": {"papel": "#f4f7fa", "tinta": "#12263a", "marco": "#c7a35a", "acento": "#0b4f8a", "panel": "#0b1620"},
 "chiringuito": {"papel": "#fff6e0", "tinta": "#3a2a1a", "marco": "#e07a3a", "acento": "#d9532b", "panel": "#1d1410"},
 "oscuro": {"papel": "#1e1b18", "tinta": "#efe6d6", "marco": "#c9a24d", "acento": "#e2bd68", "panel": "#0c0a09"},
 "rustico": {"papel": "#efe3cc", "tinta": "#3b2a1c", "marco": "#8a6a3b", "acento": "#7a3b1e", "panel": "#1f1710"}}
FUENTES_WEB = {"clasica": "Georgia,'Times New Roman',serif", "elegante": "Didot,'Bodoni 72','Bodoni MT','Playfair Display',Georgia,serif", "moderna": "'Helvetica Neue',Helvetica,Arial,sans-serif", "rustica": "Palatino,'Palatino Linotype','Book Antiqua',Georgia,serif", "manuscrita": "'Snell Roundhand','Brush Script MT','Segoe Script',cursive"}
FUENTES_PIL = {"clasica": ["/System/Library/Fonts/Supplemental/Georgia.ttf", "C:/Windows/Fonts/georgia.ttf"], "elegante": ["/System/Library/Fonts/Supplemental/Didot.ttc", "C:/Windows/Fonts/BOD_R.TTF", "C:/Windows/Fonts/times.ttf"], "moderna": ["/System/Library/Fonts/HelveticaNeue.ttc", "/System/Library/Fonts/Helvetica.ttc", "C:/Windows/Fonts/SegoeUI.ttf", "C:/Windows/Fonts/arial.ttf"], "rustica": ["/System/Library/Fonts/Palatino.ttc", "C:/Windows/Fonts/pala.ttf", "C:/Windows/Fonts/georgia.ttf"], "manuscrita": ["/System/Library/Fonts/Supplemental/SnellRoundhand.ttc", "/System/Library/Fonts/Supplemental/Zapfino.ttf", "C:/Windows/Fonts/SCRIPTBL.TTF", "C:/Windows/Fonts/gabriola.ttf"]}
def _hx(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def _c(t): return "#%02x%02x%02x" % tuple(max(0, min(255, int(v))) for v in t)
def _mez(a, b, k): return _c(tuple(x * (1 - k) + y * k for x, y in zip(_hx(a), _hx(b))))
def estilo(c):
    t = dict(TEMAS.get(c.get("tema") or "canario", TEMAS["canario"]))
    for k in ("papel", "tinta", "marco", "acento", "panel"):
        v = c.get("color_" + k) or (c.get("color_acento") if False else None)
        if v and re.match(r"^#[0-9a-fA-F]{6}$", v): t[k] = v
    lum = sum(_hx(t["papel"])) / 3
    t["ad"] = t["acento"] if lum < 110 else _mez(t["acento"], "#000000", 0.45)
    t["tit"] = FUENTES_WEB.get(c.get("fuente_titulos") or "clasica", FUENTES_WEB["clasica"]); t["txt"] = FUENTES_WEB.get(c.get("fuente_texto") or "clasica", FUENTES_WEB["clasica"])
    return t
def aplicar_estilo(css, t):
    for a, b in (("#f5ecd8", t["papel"]), ("#2b2118", t["tinta"]), ("#d4a94f", t["marco"]), ("#b8924a", t["marco"]), ("#e2bd68", _mez(t["marco"], "#ffffff", .28)), ("#c4983f", _mez(t["marco"], "#000000", .12)), ("#b8743a", _mez(t["marco"], "#000000", .35)),
                 ("#150f0a", t["panel"]), ("#2a1d14", _mez(t["panel"], "#ffffff", .1)), ("#33241a", _mez(t["panel"], "#ffffff", .12)), ("#17110c", t["panel"]), ("#0b0806", _mez(t["panel"], "#000000", .5)), ("#1b1410", t["panel"]), ("#ecd9a8", _mez(t["marco"], "#ffffff", .6)),
                 ("font-family:Georgia,'Times New Roman',serif", "font-family:" + t["txt"]), ("Georgia,serif", t["tit"])):
        css = css.replace(a, b)
    return css

# ---------- idiomas de la carta pública (ES · EN · IT · DE) ----------
IDI = {"en": "English", "it": "italiano", "de": "Deutsch"}
UI_WEB = {
 "es": {"carta": "📜 Carta", "vid": "🎬 Vídeos", "ver": "▶ Ver", "al": "Alérgenos: ", "pie": "Cocina canaria · Desliza por la carta y mira cada plato", "cerrar": "Cerrar", "ant": "Anterior", "sig": "Siguiente"},
 "en": {"carta": "📜 Menu", "vid": "🎬 Videos", "ver": "▶ Watch", "al": "Allergens: ", "pie": "Canarian cuisine · Scroll through the menu and watch every dish", "cerrar": "Close", "ant": "Previous", "sig": "Next"},
 "it": {"carta": "📜 Menù", "vid": "🎬 Video", "ver": "▶ Guarda", "al": "Allergeni: ", "pie": "Cucina canaria · Scorri il menù e guarda ogni piatto", "cerrar": "Chiudi", "ant": "Precedente", "sig": "Successivo"},
 "de": {"carta": "📜 Speisekarte", "vid": "🎬 Videos", "ver": "▶ Ansehen", "al": "Allergene: ", "pie": "Kanarische Küche · Blättere durch die Karte und sieh dir jedes Gericht an", "cerrar": "Schließen", "ant": "Zurück", "sig": "Weiter"}}
ALERG_TR = {"gluten": ("Gluten", "Glutine", "Gluten"), "crustáceos": ("Crustaceans", "Crostacei", "Krebstiere"), "huevos": ("Eggs", "Uova", "Eier"), "pescado": ("Fish", "Pesce", "Fisch"), "cacahuetes": ("Peanuts", "Arachidi", "Erdnüsse"), "soja": ("Soy", "Soia", "Soja"),
 "lácteos": ("Dairy", "Latticini", "Milch"), "frutos de cáscara": ("Tree nuts", "Frutta a guscio", "Schalenfrüchte"), "apio": ("Celery", "Sedano", "Sellerie"), "mostaza": ("Mustard", "Senape", "Senf"), "sésamo": ("Sesame", "Sesamo", "Sesam"),
 "sulfitos": ("Sulphites", "Solfiti", "Sulfite"), "altramuces": ("Lupin", "Lupini", "Lupinen"), "moluscos": ("Molluscs", "Molluschi", "Weichtiere")}
def _md5(o):
    import hashlib
    return hashlib.md5(json.dumps(o, ensure_ascii=False, sort_keys=True).encode()).hexdigest()[:10]
def _hplato(p): return _md5([p.get("nombre"), p.get("descripcion"), p.get("ingredientes"), p.get("maridaje"), p.get("etiquetas")])
def _cats(c):
    cats = []
    for p in c["platos"]:
        k = p.get("categoria") or "Carta"
        if k not in cats: cats.append(k)
    return cats
def _prompt_tr(entrada, forma):
    return ("Eres traductor profesional de cartas de restaurante. Traduce este contenido (escrito en español o en el idioma que sea) a inglés (en), italiano (it) y alemán (de). Mantén sin traducir los nombres propios y los platos típicos canarios que se conocen por su nombre (mojo, gofio, papas arrugadas, vieja, sancocho…); si ayuda puedes añadir una explicación corta entre paréntesis. No inventes ingredientes, precios ni datos. Cada lista debe tener el mismo número y el mismo orden de elementos que la entrada. "
            + forma + " Responde SOLO JSON con las claves en, it y de. Entrada: " + json.dumps(entrada, ensure_ascii=False))
def traducir_carta(r, c):
    """Traduce platos, categorías y lema a EN/IT/DE con la IA gratis y lo guarda en la carta (solo lo que cambió). Devuelve un aviso si algo falla."""
    try:
        pend = [p for p in c["platos"] if (p.get("tr") or {}).get("h") != _hplato(p)]
        for i in range(0, len(pend), 10):
            lote = pend[i:i + 10]
            ent = [{"n": p.get("nombre") or "", "d": p.get("descripcion") or "", "i": p.get("ingredientes") or [], "m": p.get("maridaje") or "", "e": p.get("etiquetas") or []} for p in lote]
            res = gemini(_prompt_tr(ent, 'Cada elemento es {"n": nombre, "d": descripción, "i": lista de ingredientes, "m": maridaje, "e": lista de etiquetas}; devuelve para cada idioma una lista de elementos con esas mismas claves.'))
            for l in IDI:
                if not isinstance(res.get(l), list) or len(res[l]) != len(lote) or not all(isinstance(x, dict) for x in res[l]): raise RuntimeError("la IA devolvió la traducción incompleta")
            for j, p in enumerate(lote):
                t = {"h": _hplato(p)}
                for l in IDI:
                    x = res[l][j]; t[l] = {"n": str(x.get("n") or p.get("nombre") or ""), "d": str(x.get("d") or ""), "i": [str(v) for v in (x.get("i") or [])][:len(p.get("ingredientes") or [])] if isinstance(x.get("i"), list) else [], "m": str(x.get("m") or ""), "e": [str(v) for v in (x.get("e") or [])] if isinstance(x.get("e"), list) else []}
                p["tr"] = t
        cats = _cats(c); ent = {"cats": cats, "lema": c.get("lema") or ""}; h = _md5(ent)
        if (c.get("tr") or {}).get("h") != h:
            res = gemini(_prompt_tr(ent, 'La entrada es {"cats": lista de categorías de la carta, "lema": frase del restaurante}; devuelve para cada idioma {"cats": lista con las categorías traducidas en el mismo orden, "lema": frase traducida (vacía si la entrada está vacía)}.'))
            tr = {"h": h}
            for l in IDI:
                x = res.get(l) or {}
                if not isinstance(x.get("cats"), list) or len(x["cats"]) != len(cats): raise RuntimeError("la IA devolvió las categorías incompletas")
                tr[l] = {"cats": {k: str(v) for k, v in zip(cats, x["cats"])}, "lema": str(x.get("lema") or "")}
            c["tr"] = tr
        guardar(r, c); return ""
    except Exception as e:
        return str(e)[:160]
def tr_web(c, plist, cats):
    """Datos de traducción que lleva la página pública. Solo se ofrecen los idiomas con la carta entera traducida."""
    def orig(p):
        return {"n": p.get("nombre") or "", "d": p.get("descripcion") or "", "i": ", ".join(p.get("ingredientes", [])), "m": p.get("maridaje") or "", "e": list(p.get("etiquetas", []))}
    out = {"es": {"ui": UI_WEB["es"], "al": {a: a.capitalize() for a in ALERGENOS}, "cats": {k: k for k in cats}, "lema": c.get("lema") or "", "p": [orig(p) for p in plist]}}
    ct = c.get("tr") or {}
    for n, l in enumerate(IDI):
        if not ct.get("h") or ct.get("h") != _md5({"cats": cats, "lema": c.get("lema") or ""}): break
        if not all((p.get("tr") or {}).get("h") == _hplato(p) and isinstance((p.get("tr") or {}).get(l), dict) for p in plist): continue
        ps = []
        for p in plist:
            t = p["tr"][l]; o = orig(p)
            ps.append({"n": t["n"] or o["n"], "d": t["d"] or o["d"], "i": ", ".join(t["i"]) if t["i"] else o["i"], "m": t["m"] or o["m"], "e": [(t["e"][k] if k < len(t["e"]) and t["e"][k] else o["e"][k]) for k in range(len(o["e"]))]})
        out[l] = {"ui": UI_WEB[l], "al": {a: v[n] for a, v in ALERG_TR.items()}, "cats": ct[l]["cats"], "lema": ct[l]["lema"], "p": ps}
    return out
IDI_JS = r"""(function(){
function ap(l){const T=TR[l]||TR.es;document.documentElement.lang=l;
document.getElementById('tp').textContent=T.ui.carta;document.getElementById('tg').textContent=T.ui.vid;
document.querySelectorAll('.v i').forEach(e=>e.textContent=T.ui.ver);
const pie=document.querySelector('.pie');if(pie)pie.textContent=T.ui.pie;
document.getElementById('x').setAttribute('aria-label',T.ui.cerrar);document.getElementById('pv').setAttribute('aria-label',T.ui.ant);document.getElementById('nx').setAttribute('aria-label',T.ui.sig);
document.querySelectorAll('[data-c]').forEach(e=>{e.textContent=T.cats[e.dataset.c]||e.dataset.c});
document.querySelectorAll('[data-t="lema"]').forEach(e=>{e.textContent=T.lema||TR.es.lema});
document.querySelectorAll('.card').forEach(c=>{const P=T.p[+c.dataset.i];if(!P)return;c.setAttribute('aria-label',P.n);const d=c.querySelector('[data-t=d]');if(d)d.textContent=P.d});
document.querySelectorAll('.pl').forEach(x=>{const P=T.p[+x.dataset.i];if(!P)return;x.querySelector('.n').textContent=P.n;x.querySelector('.ds').textContent=P.d;const i=x.querySelector('[data-t=i]');if(i)i.textContent=P.i;const m=x.querySelector('[data-t=m]');if(m)m.textContent='🍷 '+P.m;x.querySelectorAll('.et').forEach(e=>{const v=P.e[+e.dataset.e];if(v)e.textContent=v});x.querySelectorAll('[data-a]').forEach(s=>{s.title=T.al[s.dataset.a]||s.dataset.a})});
D.forEach((x,i)=>{const P=T.p[i];if(!P)return;x.n=P.n;x.d=P.d;x.a=x.ak.length?T.ui.al+x.ak.map(z=>T.al[z]||z).join(', '):''});
if(act>=0&&D[act])pvc.textContent=D[act].n;
if(w.classList.contains('on'))show(k)}
const ls=Object.keys(TR),NM={es:'Español',en:'English',it:'Italiano',de:'Deutsch'},ss=document.createElement('select');ss.id='il';ss.setAttribute('aria-label','Language / Idioma');
ls.forEach(l=>{const o=document.createElement('option');o.value=l;o.textContent='🌐 '+NM[l];ss.appendChild(o)});
ss.style.cssText='border:1px solid #d4a94f66;background:#00000066;color:#ecd9a8;border-radius:99px;padding:8px 14px;font:14px Georgia,serif;cursor:pointer;color-scheme:dark';
if(ls.length>1)document.querySelector('.tb').appendChild(ss);
let l0='';try{l0=localStorage.getItem('cvl')||''}catch(e){}
const q=new URLSearchParams(location.search).get('l');if(q)l0=q;
if(!TR[l0]){l0=(navigator.language||'es').slice(0,2).toLowerCase();if(!TR[l0])l0='es'}
ss.value=l0;ss.onchange=()=>{try{localStorage.setItem('cvl',ss.value)}catch(e){}ap(ss.value)};
if(l0!=='es')ap(l0)})();"""
def generar_web(r, c):
    d = dir_r(r); w = os.path.join(d, "web"); shutil.rmtree(w, ignore_errors=True); os.makedirs(os.path.join(w, "videos")); os.makedirs(os.path.join(w, "fotos")); mk = marca_de(d)
    if os.path.isdir(os.path.join(d, "marca")): shutil.copytree(os.path.join(d, "marca"), os.path.join(w, "marca"), copy_function=shutil.copyfile)
    est = estilo(c)
    css = aplicar_estilo((CSS2 + CSS3).replace("__AD__", est["ad"]).replace("__AC__", est["acento"]), est) + (".fx{position:fixed;inset:0;z-index:-1;background:#0f0d0b url(marca/fondo.jpg?v=__V__) center/cover}.fx:after{content:'';position:absolute;inset:0;background:#0f0d0b99}body{background:transparent}" if mk["fondo"] else "")
    css = css.replace("__V__", str(int(os.path.getmtime(mk["fondo"]))) if mk["fondo"] else "0")
    cats = []
    for p in c["platos"]:
        k = p.get("categoria") or "Carta"
        if k not in cats: cats.append(k)
    cuerpo = ""; datos = []; plist = []; n = 0; papel = ""
    for k in cats:
        cuerpo += f'<section id="g-{slug(k)}"><h2 data-c="{esc(k)}">{esc(k)}</h2><div class="g">'; papel += f'<section id="p-{slug(k)}"><h2 data-c="{esc(k)}">{esc(k)}</h2>'
        for p in [x for x in c["platos"] if (x.get("categoria") or "Carta") == k and x.get("disponible") is not False]:
            vid = p.get("video"); poster = "p_" + p["id"] + ".jpg"
            if vid and os.path.exists(os.path.join(d, "videos", vid)): shutil.copyfile(os.path.join(d, "videos", vid), os.path.join(w, "videos", vid))
            if os.path.exists(os.path.join(d, "fotos", poster)): shutil.copyfile(os.path.join(d, "fotos", poster), os.path.join(w, "fotos", poster))
            tiene_v = bool(vid) and os.path.exists(os.path.join(w, "videos", vid or "x"))
            media = f'<video muted loop playsinline preload="none" poster="fotos/{poster}" data-src="videos/{vid}"></video>' if tiene_v else f'<img src="fotos/{poster}" alt="{esc(p.get("nombre"))}">'
            als = p.get("alergenos", []); pre = str(p.get("precio") or "").strip(); pre = pre + (" €" if pre and not pre.endswith("€") else "")
            iconos = "".join(f'<span title="{esc(a)}" data-a="{esc(a)}">{ICONOS.get(a, "•")}</span>' for a in als)
            ets = "".join(f'<b class="et" data-e="{ei}">{esc(t)}</b>' for ei, t in enumerate(p.get("etiquetas", [])))
            ingr = ", ".join(p.get("ingredientes", [])); mar = p.get("maridaje") or ""
            extra = (f'<div class="ig" data-t="i">{esc(ingr)}</div>' if ingr else "") + (f'<div class="ig" data-t="m">🍷 {esc(mar)}</div>' if mar else "")
            cuerpo += f'<button class="card" data-i="{n}" aria-label="{esc(p.get("nombre"))}"><div class="v">{media}<i>▶ Ver</i></div><div class="t"><p class="d" data-t="d">{esc(p.get("descripcion"))}</p><div class="al">{iconos}</div></div></button>'
            papel += f'<div class="pl" data-i="{n}"><div class="f1"><span class="n">{esc(p.get("nombre"))}</span><span class="pt"></span><span class="pr">{esc(pre)}</span></div><div class="ds">{esc(p.get("descripcion"))}</div>{extra}<div class="ic">{ets}{iconos}</div></div>'
            datos.append({"n": p.get("nombre") or "", "p": pre, "d": p.get("descripcion") or "", "a": ("Alérgenos: " + ", ".join(als)) if als else "", "v": ("videos/" + vid) if tiene_v else "", "f": "fotos/" + poster, "ak": list(als)}); plist.append(p); n += 1
        cuerpo += "</div></section>"; papel += "</section>"
    nav = "".join(f'<a href="#" data-k="{slug(k)}" data-c="{esc(k)}">{esc(k)}</a>' for k in cats)
    logo_html = '<img class="lg" src="marca/logo.png" alt="">' if mk["logo"] else ""
    visor = '<div id="vw"><span id="ct"></span><button id="x" aria-label="Cerrar">✕</button><button id="pv" aria-label="Anterior">‹</button><button id="nx" aria-label="Siguiente">›</button><div class="st"><video id="vv" muted loop playsinline></video></div><div class="in"><div><span class="nm" id="nm"></span> · <span class="pr" id="pr"></span></div><p class="ds" id="ds"></p><p class="ax" id="ax"></p></div></div>'
    dj = json.dumps(datos, ensure_ascii=False).replace("</", "<\\/"); trj = json.dumps(tr_web(c, plist, cats), ensure_ascii=False).replace("</", "<\\/")
    pg = f'<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"><meta name="theme-color" content="#0f0d0b"><title>{esc(c["nombre"])} · Carta</title><style>{css}</style></head><body><div class="fx"></div><header class="hero" id="hr" hidden>{logo_html}<h1>{esc(c["nombre"])}</h1><p data-t="lema">{esc(c.get("lema", ""))}</p></header><div class="tb"><button id="tp" class="on">📜 Carta</button><button id="tg">🎬 Vídeos</button></div><nav>{nav}</nav><div id="pp"><div class="libro"><div class="hoja"><div class="calado"></div><div class="cab">{logo_html}<h1>{esc(c["nombre"])}</h1><div class="lm" data-t="lema">{esc(c.get("lema", ""))}</div><div class="orn">{PALMA}</div></div>{papel}<div class="calado" style="margin-top:26px"></div><div class="pie">Cocina canaria · Desliza por la carta y mira cada plato</div></div><aside class="pv2"><div class="in2"><div class="mk"><video id="pvv" muted loop playsinline></video><img id="pvi" alt="" style="display:none"></div><p id="pvc"></p></div></aside></div></div><main id="gv" hidden>{cuerpo}</main><footer>Carta Viva · Island Crew</footer>{visor}<script>const D={dj},TR={trj};let vista="p";{JS2}{PAPEL_JS}{IDI_JS}</script></body></html>'
    open(os.path.join(w, "index.html"), "w", encoding="utf8").write(pg)
    url = (c.get("url_publica") or "").strip()
    if url: hacer_qr(r, c, url, mk)
    return w, bool(url)
def hacer_qr(r, c, url, mk):
    import segno
    from PIL import Image, ImageDraw
    d = dir_r(r); q = segno.make(url, error="h"); png = os.path.join(d, "QR-carta.png"); q.save(png, scale=16, border=3); q.save(os.path.join(d, "QR-carta.svg"), scale=16, border=3)
    qi = Image.open(png).convert("RGB")
    if mk["logo"]:
        lg = Image.open(mk["logo"]).convert("RGBA"); lg.thumbnail((int(qi.width * .2), int(qi.width * .2))); bx = Image.new("RGBA", (lg.width + 24, lg.height + 24), (255, 255, 255, 255)); bx.alpha_composite(lg, (12, 12)); qi.paste(bx, ((qi.width - bx.width) // 2, (qi.height - bx.height) // 2))
    qi.save(png); qi.save(os.path.join(d, "web", "qr.png"))
    P = Image.new("RGB", (1240, 1754), (15, 13, 11)); dr = ImageDraw.Draw(P); ac = mk["acento"]
    if mk["fondo"]:
        fb = Image.open(mk["fondo"]).convert("RGB"); sf = max(1240 / fb.width, 1754 / fb.height); fb = fb.resize((int(fb.width * sf) + 1, int(fb.height * sf) + 1)); P.paste(fb.point(lambda v: int(v * 0.35)), (-(fb.width - 1240) // 2, -(fb.height - 1754) // 2))
    y = 130
    if mk["logo"]:
        lg = Image.open(mk["logo"]).convert("RGBA"); lg.thumbnail((520, 240)); P.paste(lg, ((1240 - lg.width) // 2, y), lg); y += lg.height + 40
    fn = _fuente(96); nom = (c.get("nombre") or "").upper()
    while dr.textlength(nom, font=fn) > 1100 and fn.size > 40: fn = _fuente(fn.size - 6)
    dr.text((620, y + 60), nom, font=fn, fill=(246, 236, 220), anchor="mm"); dr.line((520, y + 140, 720, y + 140), fill=ac, width=4)
    dr.text((620, y + 215), "Mira nuestros platos en vídeo", font=_fuente(52), fill=ac, anchor="mm")
    qs = 760; qq = qi.resize((qs, qs)); bw = qs + 70; bx = (1240 - bw) // 2; by = 1754 - 220 - bw
    dr.rounded_rectangle((bx, by, bx + bw, by + bw), 36, fill=(255, 255, 255)); P.paste(qq, (bx + 35, by + 35))
    dr.text((620, 1754 - 140), _fl(2), font=_fuente(44), fill=(246, 236, 220), anchor="mm")
    P.save(os.path.join(d, "QR-cartel.png"))
def _wrap(dr, txt, fn, ancho):
    out = []; l = ""
    for w in (txt or "").split():
        t = (l + " " + w).strip()
        if dr.textlength(t, font=fn) <= ancho or not l: l = t
        else: out.append(l); l = w
    if l: out.append(l)
    return out
def _fnt(tam, pref, ini=0):
    return _fuente(tam, ini, pref)
def _fondo_img(W, H, est, mk):
    from PIL import Image, ImageDraw
    if mk["fondo"]:
        fb = Image.open(mk["fondo"]).convert("RGB"); sf = max(W / fb.width, H / fb.height); fb = fb.resize((int(fb.width * sf) + 1, int(fb.height * sf) + 1), Image.LANCZOS)
        l, t = (fb.width - W) // 2, (fb.height - H) // 2; P = fb.crop((l, t, l + W, t + H)).point(lambda v: int(v * 0.3))
    else:
        P = Image.new("RGB", (W, H), _hx(est["panel"])); dg = ImageDraw.Draw(P); top = _hx(_mez(est["panel"], "#ffffff", .12)); bot = _hx(est["panel"])
        for y in range(H): k = y / H; dg.line((0, y, W, y), fill=tuple(int(top[i] * (1 - k) + bot[i] * k) for i in range(3)))
    return P
def _calado(dr, x0, x1, y, col, paso=34):
    x = x0
    while x + paso <= x1:
        cx = x + paso / 2; dr.polygon([(cx, y - 7), (cx + 13, y), (cx, y + 7), (cx - 13, y)], outline=col, width=2); dr.polygon([(cx, y - 3), (cx + 6, y), (cx, y + 3), (cx - 6, y)], fill=col); x += paso
FLYER_TXT = {"es": ("MENÚ EN VÍDEO", "Mira cada plato antes de pedirlo", "Escanea con la cámara de tu móvil", "Escanea el QR con tu móvil"),
 "en": ("VIDEO MENU", "Watch every dish before you order", "Scan with your phone camera", "Scan the QR code with your phone"),
 "it": ("MENÙ IN VIDEO", "Guarda ogni piatto prima di ordinare", "Inquadra con la fotocamera del telefono", "Inquadra il QR con il telefono"),
 "de": ("VIDEO-SPEISEKARTE", "Sieh dir jedes Gericht vor dem Bestellen an", "Scanne mit deiner Handykamera", "Scanne den QR-Code mit deinem Handy")}
def _fl(i): return FLYER_TXT.get(__import__('marca').codigo(), FLYER_TXT["es"])[i]
def hacer_flyer(r, c, formato):
    """formato: a4 (1240x1754), story (1080x1920), banner (1920x640). Usa el estilo, logo y fondo del local + el QR."""
    from PIL import Image, ImageDraw
    d = dir_r(r); mk = marca_de(d); est = estilo(c); pref = c.get("fuente_titulos") or "clasica"; pref_t = c.get("fuente_texto") or "clasica"
    qrp = os.path.join(d, "QR-carta.png")
    if not os.path.exists(qrp): raise RuntimeError("Primero pon la dirección web y pulsa «Crear vídeos y carta».")
    qi = Image.open(qrp).convert("RGB"); marco = _hx(est["marco"]); claro = _hx(_mez(est["marco"], "#ffffff", .35)); blanco = (246, 238, 224)
    tit = (c.get("flyer_titulo") or _fl(0)).upper(); sub = c.get("flyer_sub") or _fl(1); pie = c.get("flyer_pie") or ""; nom = (c.get("nombre") or "").upper()
    W, H = {"a4": (1240, 1754), "story": (1080, 1920), "banner": (1920, 640)}[formato]
    P = _fondo_img(W, H, est, mk); dr = ImageDraw.Draw(P); m = 38 if formato != "banner" else 26
    dr.rectangle((m, m, W - m, H - m), outline=marco, width=3); dr.rectangle((m + 12, m + 12, W - m - 12, H - m - 12), outline=_hx(_mez(est["marco"], est["panel"], .55)), width=1)
    def centrado(txt, y, tam, col, p=pref, ini=0, ancho=None, sep=1.25):
        fn = _fnt(tam, p, ini); ancho = ancho or W - 200; ls = _wrap(dr, txt, fn, ancho)
        while len(ls) > 2 and fn.size > 28: fn = _fnt(fn.size - 4, p, ini); ls = _wrap(dr, txt, fn, ancho)
        for ln in ls: dr.text((W / 2, y), ln, font=fn, fill=col, anchor="mm"); y += int(fn.size * sep)
        return y
    if formato != "banner":
        esc = W / 1240; y = int(H * 0.07)
        _calado(dr, m + 30, W - m - 30, y, marco); y += int(70 * esc)
        if mk["logo"]:
            lg = Image.open(mk["logo"]).convert("RGBA"); lg.thumbnail((int(460 * esc), int(210 * esc))); P.paste(lg, ((W - lg.width) // 2, y), lg); y += lg.height + int(30 * esc)
        y = centrado(tit, y + int(40 * esc), int(56 * esc), marco, pref_t, 0) + int(12 * esc)
        y = centrado(nom, y + int(40 * esc), int(104 * esc), blanco, pref) + int(2 * esc)
        dr.line((W / 2 - 90 * esc, y, W / 2 + 90 * esc, y), fill=marco, width=3); y += int(46 * esc)
        y = centrado(sub, y, int(50 * esc), claro, pref_t, 0, sep=1.3)
        by = y + int(30 * esc); qs = int(min(W * 0.56, H - by - int(330 * esc) - int(60 * esc))); bw = qs + int(60 * esc); bx = (W - bw) // 2
        dr.rounded_rectangle((bx, by, bx + bw, by + bw), int(34 * esc), fill=(255, 255, 255), outline=marco, width=4); P.paste(qi.resize((qs, qs), Image.LANCZOS), (bx + int(30 * esc), by + int(30 * esc)))
        yy = by + bw + int(55 * esc); yy = centrado(_fl(2), yy, int(44 * esc), blanco, pref_t, 0)
        if pie: centrado(pie, yy + int(24 * esc), int(38 * esc), claro, pref_t, 0)
        _calado(dr, m + 30, W - m - 30, H - m - int(34 * esc), marco)
    else:
        qs = 470; bw = qs + 40; bx = W - m - bw - 40; by = (H - bw) // 2
        dr.rounded_rectangle((bx, by, bx + bw, by + bw), 26, fill=(255, 255, 255), outline=marco, width=4); P.paste(qi.resize((qs, qs), Image.LANCZOS), (bx + 20, by + 20))
        x0 = m + 50
        if mk["logo"]:
            lg = Image.open(mk["logo"]).convert("RGBA"); lg.thumbnail((170, 120)); P.paste(lg, (x0, 55), lg); x0b = x0 + lg.width + 30
        else: x0b = x0
        dr.text((x0b, 105), tit, font=_fnt(44, pref_t), fill=marco, anchor="lm")
        fn = _fnt(112, pref); 
        while dr.textlength(nom, font=fn) > bx - x0 - 60 and fn.size > 40: fn = _fnt(fn.size - 6, pref)
        dr.text((x0, 290), nom, font=fn, fill=blanco, anchor="lm"); dr.line((x0, 360, x0 + 180, 360), fill=marco, width=3)
        ls = _wrap(dr, sub, _fnt(46, pref_t), bx - x0 - 60); yy = 420
        for ln in ls[:2]: dr.text((x0, yy), ln, font=_fnt(46, pref_t), fill=claro, anchor="lm"); yy += 58
        dr.text((x0, H - 90), pie or _fl(3), font=_fnt(36, pref_t), fill=blanco, anchor="lm")
    return P
def exportar_promo(r, c):
    d = dir_r(r); url = (c.get("url_publica") or "").strip()
    if not url: raise RuntimeError("Pon primero la dirección web de la carta (campo del QR).")
    os.makedirs(os.path.join(d, "web"), exist_ok=True); hacer_qr(r, c, url, marca_de(d))
    pd = os.path.join(d, "promo"); os.makedirs(pd, exist_ok=True); sl = slug(c.get("nombre") or r); dest = os.path.join(core.carpeta_descargas(), "Carta Viva - " + (c.get("nombre") or r)); os.makedirs(dest, exist_ok=True)
    salida = {}
    for f, nombre in (("a4", "Flyer-A4"), ("story", "Story-Instagram-WhatsApp"), ("banner", "Banner-web")):
        im = hacer_flyer(r, c, f); p1 = os.path.join(pd, f + ".png"); im.save(p1); shutil.copyfile(p1, os.path.join(dest, f"{nombre}-{sl}.png")); salida[f] = f + ".png"
        if f == "a4": im.save(os.path.join(dest, f"Flyer-A4-{sl}.pdf"), "PDF", resolution=150)
    shutil.copyfile(os.path.join(d, "QR-carta.png"), os.path.join(dest, f"QR-{sl}.png")); shutil.copyfile(os.path.join(d, "QR-carta.svg"), os.path.join(dest, f"QR-{sl}.svg"))
    return dest, salida
def ia_flyer(c):
    pr = f"Eres publicista de restaurantes. Restaurante: '{c.get('nombre','')}', lema: '{c.get('lema','')}'. Crea los textos de un flyer con código QR que lleva a su carta de platos en vídeo. Responde SOLO JSON con: \"titulo\" (máx 4 palabras, en mayúsculas, ej. MENÚ EN VÍDEO), \"sub\" (frase de máx 12 palabras que invite a escanear y ver los platos), \"pie\" (una línea corta; si no conoces dirección ni teléfono NO los inventes y pon algo como 'Buen provecho'). Escribe en {__import__('marca').lengua()}, cálido, toque canario si encaja."
    return gemini(pr)
def tam(p):
    if os.path.isfile(p): return os.path.getsize(p)
    t = 0
    for rr, _, fs in os.walk(p):
        for f in fs:
            try: t += os.path.getsize(os.path.join(rr, f))
            except Exception: pass
    return t
def ruta_desc(r):
    c = leer(r) or {}; return os.path.join(core.carpeta_descargas(), "Carta Viva - " + (c.get("nombre") or r))
def espacio(r):
    d = dir_r(r); fo = os.path.join(d, "fotos"); pos = sum(os.path.getsize(os.path.join(fo, f)) for f in os.listdir(fo) if f.startswith("p_")) if os.path.isdir(fo) else 0
    return {"carpeta": d, "videos": tam(os.path.join(d, "videos")) + pos, "web": tam(os.path.join(d, "web")), "promo": tam(os.path.join(d, "promo")) + sum(tam(os.path.join(d, x)) for x in ("QR-carta.png", "QR-carta.svg", "QR-cartel.png") if os.path.exists(os.path.join(d, x))),
            "descargas": tam(ruta_desc(r)) if os.path.isdir(ruta_desc(r)) else 0, "fotos": tam(fo) - pos, "marca": tam(os.path.join(d, "marca")), "desc_ruta": ruta_desc(r), "total": tam(d)}
def liberar(r, que):
    antes = espacio(r); d = dir_r(r)
    if "web" in que: shutil.rmtree(os.path.join(d, "web"), ignore_errors=True)
    if "promo" in que:
        shutil.rmtree(os.path.join(d, "promo"), ignore_errors=True)
        for x in ("QR-carta.png", "QR-carta.svg", "QR-cartel.png"):
            try: os.remove(os.path.join(d, x))
            except Exception: pass
    if "descargas" in que: shutil.rmtree(ruta_desc(r), ignore_errors=True)
    if "videos" in que:
        shutil.rmtree(os.path.join(d, "videos"), ignore_errors=True); fo = os.path.join(d, "fotos")
        if os.path.isdir(fo):
            for f in os.listdir(fo):
                if f.startswith("p_"):
                    try: os.remove(os.path.join(fo, f))
                    except Exception: pass
        c = leer(r)
        if c:
            for p in c.get("platos", []): p.pop("video", None); p.pop("video_de", None)
            guardar(r, c)
    return antes["total"] + antes["descargas"] - espacio(r)["total"] - espacio(r)["descargas"]
def pipeline(r):
    try:
        c = leer(r); estado("Preparando la carta…", True); n = 0
        for i, p in enumerate(c["platos"]):
            vp = os.path.join(dir_r(r), "videos", p.get("video") or "x")
            if p.get("foto") and not (p.get("video") and os.path.exists(vp) and p.get("video_de") == clave_video(p, dir_r(r))):
                estado(f"Creando el vídeo de «{p.get('nombre')}» ({i+1}/{len(c['platos'])})…")
                p["video"] = hacer_video(r, p, i); p["video_de"] = clave_video(p, dir_r(r)); n += 1; guardar(r, c)
        estado("Traduciendo la carta a inglés, italiano y alemán…"); av = traducir_carta(r, c)
        estado("Montando la página de la carta…"); w, qr = generar_web(r, c)
        estado(f"✔ Carta lista ({n} vídeos nuevos). " + ("QR creado." if qr else "Pon la dirección pública para crear el QR.") + (" Sin traducir ahora (" + av + "): la carta sale solo en su idioma." if av else " Con selector de idioma: ES · EN · IT · DE."), False)
    except Exception as e: estado("✖ " + str(e)[:300], False)

# ---------- servidor ----------
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _ok(self): return (self.headers.get("Host") or "").split(":")[0] in ("127.0.0.1", "localhost")
    def _j(self, d, c=200):
        b = json.dumps(d, ensure_ascii=False).encode(); self.send_response(c); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def _f(self, ruta, tipo):
        tam = os.path.getsize(ruta); rg = self.headers.get("Range"); a, b, c = 0, tam - 1, 200
        if rg and rg.startswith("bytes="):
            x, _, z = rg[6:].partition("-"); a = int(x) if x else 0; b = min(int(z) if z else tam - 1, tam - 1); c = 206
        self.send_response(c); self.send_header("Content-Type", tipo); self.send_header("Accept-Ranges", "bytes"); self.send_header("Content-Length", str(b - a + 1))
        if c == 206: self.send_header("Content-Range", f"bytes {a}-{b}/{tam}")
        self.end_headers()
        with open(ruta, "rb") as f:
            f.seek(a); resto = b - a + 1
            while resto > 0:
                bl = f.read(min(65536, resto))
                if not bl: break
                try: self.wfile.write(bl)
                except Exception: break
                resto -= len(bl)
    def do_GET(self):
        if not self._ok(): return self._j({"error": "no"}, 403)
        u = urlparse(self.path); q = parse_qs(u.query)
        if u.path == "/":
            b = open(os.path.join(AQUI, "carta-viva-app.html"), encoding="utf8").read().replace("__TOKEN__", TOKEN).replace("__ALERGENOS__", json.dumps(ALERGENOS, ensure_ascii=False)); b = __import__("marca").html(b).encode()
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); return self.wfile.write(b)
        if (q.get("t") or [""])[0] != TOKEN and self.headers.get("x-cv") != TOKEN: return self._j({"error": "sin permiso"}, 403)
        if u.path == "/api/restaurantes": return self._j(listar())
        if u.path == "/api/carta": return self._j(leer((q.get("r") or [""])[0]) or {})
        if u.path == "/api/estado": return self._j(EST)
        if u.path == "/api/espacio": return self._j(espacio((q.get("r") or [""])[0]))
        if u.path.startswith("/media/"):
            _, _, r, sub, fn = u.path.split("/")[:5]
            p = os.path.join(dir_r(r), sub, os.path.basename(unquote(fn)))
            if sub in ("fotos", "videos", "marca", "web", "promo") and os.path.exists(p): return self._f(p, "video/mp4" if p.endswith(".mp4") else ("image/png" if p.endswith(".png") else "image/jpeg"))
            return self._j({}, 404)
        self._j({}, 404)
    def do_POST(self):
        __import__('marca').fijar(self.headers)
        if not self._ok() or self.headers.get("x-cv") != TOKEN: return self._j({"error": "sin permiso"}, 403)
        try:
            d = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}"); u = self.path; r = d.get("r", "")
            if u == "/api/crear":
                n = (d.get("nombre") or "").strip()
                if not n: return self._j({"error": "Pon el nombre del restaurante."}, 400)
                if not leer(n): guardar(n, {"nombre": n, "lema": "", "url_publica": "", "platos": []})
                return self._j({"id": slug(n)})
            if u == "/api/guardar": guardar(r, d["carta"]); return self._j({"ok": True})
            if u == "/api/foto": return self._j({"foto": guardar_foto(r, d["pid"], d["datos"])})
            if u == "/api/marca":
                from PIL import Image, ImageOps
                md = os.path.join(dir_r(r), "marca"); os.makedirs(md, exist_ok=True); t = d["tipo"]
                if d.get("quitar"):
                    try: os.remove(os.path.join(md, "logo.png" if t == "logo" else "fondo.jpg"))
                    except Exception: pass
                    return self._j({"ok": True})
                im = ImageOps.exif_transpose(Image.open(io.BytesIO(base64.b64decode(d["datos"].split(",")[-1]))))
                if t == "logo": im = quitar_blanco(im); im.thumbnail((900, 900)); im.save(os.path.join(md, "logo.png"))
                else: im = im.convert("RGB"); im.thumbnail((2000, 2000)); im.save(os.path.join(md, "fondo.jpg"), "JPEG", quality=88)
                return self._j({"ok": True})
            if u == "/api/liberar":
                if EST["trabajando"]: return self._j({"error": "Espera a que termine de crear los vídeos."}, 409)
                return self._j({"liberado": liberar(r, d.get("que", []))})
            if u == "/api/promo":
                c = leer(r) or {}; dest, sal = exportar_promo(r, c); core.abrir(dest); return self._j({"ok": True, "carpeta": dest})
            if u == "/api/ia-flyer": return self._j(ia_flyer(leer(r) or {}))
            if u == "/api/ia":
                p = d["plato"]; c = leer(r) or {}
                if p.get("foto"): p["foto_path"] = os.path.join(dir_r(r), "fotos", p["foto"])
                return self._j(ia_plato(p, c.get("nombre", ""), d["campos"]))
            if u == "/api/generar":
                if EST["trabajando"]: return self._j({"error": "Ya está trabajando."}, 409)
                EST["trabajando"] = True; threading.Thread(target=pipeline, args=(r,), daemon=True).start(); return self._j({"ok": True})
            if u == "/api/abrir": subprocess.Popen(["open", dir_r(r)]); return self._j({"ok": True})
            if u == "/api/ver":
                if d.get("que") == "cartel":
                    cp = os.path.join(dir_r(r), "QR-cartel.png")
                    if os.path.exists(cp): subprocess.Popen(["open", cp]); return self._j({"ok": True})
                    return self._j({"error": "Primero pon la dirección pública y pulsa «Crear vídeos y carta»."}, 400)
                w = os.path.join(dir_r(r), "web", "index.html")
                if os.path.exists(w):
                    v = os.path.join(dir_r(r), "web", "_vista.html")  # abre la carta en el idioma que tienes elegido en la app
                    open(v, "w", encoding="utf8").write("<!doctype html><meta charset=utf-8><script>location.replace('index.html?l=%s')</script>" % __import__('marca').codigo()); subprocess.Popen(["open", v]); return self._j({"ok": True})
                return self._j({"error": "Aún no has generado la carta."}, 400)
            self._j({}, 404)
        except Exception as e: self._j({"error": str(e)[:400]}, 500)

def puerto_libre():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p
def main():
    os.makedirs(os.path.dirname(INFO), exist_ok=True); os.makedirs(BASE, exist_ok=True)
    if "--parar" in sys.argv:
        try: core.parar_proceso(json.load(open(INFO))["pid"]); print("Carta Viva parado.")
        except Exception: print("No estaba en marcha.")
        return
    try:
        i = json.load(open(INFO)); assert core.proceso_vivo(i["pid"]); urllib.request.urlopen(f"http://127.0.0.1:{i['port']}/", timeout=2); print("Ya en marcha."); return
    except Exception: pass
    pt = puerto_libre(); srv = ThreadingHTTPServer(("127.0.0.1", pt), H)
    json.dump({"pid": os.getpid(), "port": pt}, open(INFO, "w")); (os.name != "nt") and os.chmod(INFO, 0o600)
    print(f"Carta Viva en marcha (puerto {pt}). Datos en {BASE}", flush=True); srv.serve_forever()
if __name__ == "__main__": main()
