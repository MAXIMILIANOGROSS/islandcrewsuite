#!/usr/bin/env python3
"""Island Crew · Fábrica de anuncios (publicidad del restaurante, 100 % local).
Con los platos reales de Carta Viva crea anuncios en 4 formatos (feed, story, cuadrado, pantalla horizontal) y un vídeo vertical.
Los precios, ofertas y teléfonos los escribe el cliente; la IA nunca los inventa. Parar: --parar"""
import os, sys, json, re, time, socket, shutil, secrets, subprocess, datetime, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(AQUI, "..", "suite"))
import core, marca
INFO = os.path.expanduser("~/IslandCrewAI/anuncios-app.json"); TOKEN = secrets.token_hex(16)
BASE = os.path.join(core.carpeta_datos(), "cartas")
FUENTES = ["/System/Library/Fonts/Supplemental/Georgia.ttf", "/System/Library/Fonts/Helvetica.ttc", "C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
FUENTES_B = ["/System/Library/Fonts/Supplemental/Georgia Bold.ttf", "C:/Windows/Fonts/georgiab.ttf", "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"] + FUENTES
FORMATOS = {"feed": (1080, 1350), "story": (1080, 1920), "cuadrado": (1080, 1080), "pantalla": (1920, 1080)}
ESTILOS = {"marco": "Marco dorado", "banda": "Banda de color", "cartel": "Cartel grande"}


def slug(s): return re.sub(r"[^a-z0-9]+", "-", (s or "").lower().encode("ascii", "ignore").decode() or "x").strip("-")
def dir_r(r): return os.path.join(BASE, slug(r))
def leer_carta(r):
    try: return json.load(open(os.path.join(dir_r(r), "carta.json"), encoding="utf8"))
    except Exception: return None
def restaurantes():
    try: return sorted(x for x in os.listdir(BASE) if os.path.exists(os.path.join(BASE, x, "carta.json")))
    except Exception: return []


def _f(t, neg=False):
    from PIL import ImageFont
    for f in (FUENTES_B if neg else FUENTES):
        try: return ImageFont.truetype(f, t)
        except Exception: pass
    return ImageFont.load_default()


def _lineas(dr, txt, fuente, ancho):
    out, cur = [], ""
    for w in (txt or "").split():
        t = (cur + " " + w).strip()
        if dr.textlength(t, font=fuente) <= ancho or not cur: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out


def _hex(h, d=(226, 189, 104)):
    try: h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    except Exception: return d


def pieza(r, cfg, fmt, dest=None):
    from PIL import Image, ImageDraw, ImageOps
    c = leer_carta(r); p = next(x for x in c["platos"] if x["id"] == cfg["plato"]); W, H = FORMATOS[fmt]; est = cfg.get("estilo", "marco")
    ac = _hex(c.get("color_acento") or "#e2bd68"); foto = ImageOps.exif_transpose(Image.open(os.path.join(dir_r(r), "fotos", p["foto"]))).convert("RGB")
    def cubrir(im, w, h):
        s = max(w / im.width, h / im.height); im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS)
        L, T = (im.width - w) // 2, (im.height - h) // 2; return im.crop((L, T, L + w, T + h))
    tit = (cfg.get("titular") or p["nombre"]).strip(); sub = (cfg.get("subtitulo") or "").strip(); cta = (cfg.get("cta") or "").strip(); con = (cfg.get("contacto") or "").strip()
    nom = (c.get("nombre") or "").upper(); u = W / 1080 if W <= H else H / 1080; hor = W > H
    if est == "banda":
        fh = int(H * (0.60 if not hor else 1.0)) if not hor else H
        if hor:
            im = Image.new("RGB", (W, H), (20, 16, 12)); im.paste(cubrir(foto, int(W * 0.56), H), (0, 0)); dr = ImageDraw.Draw(im); x0 = int(W * 0.56); dr.rectangle([x0, 0, W, H], fill=ac)
            zona = (x0 + 60, 90, W - 60, H - 90)
        else:
            im = Image.new("RGB", (W, H), ac); im.paste(cubrir(foto, W, int(H * 0.58)), (0, 0)); dr = ImageDraw.Draw(im); zona = (60, int(H * 0.58) + 40, W - 60, H - 50)
        txt = (20, 14, 6); x0z, y0z, x1z, y1z = zona; y = y0z
        f1 = _f(int(74 * u), True); ls = _lineas(dr, tit, f1, x1z - x0z)[:3]
        for l in ls: dr.text((x0z, y), l, font=f1, fill=txt); y += int(84 * u)
        if sub:
            f2 = _f(int(40 * u)); y += 8
            for l in _lineas(dr, sub, f2, x1z - x0z)[:3]: dr.text((x0z, y), l, font=f2, fill=txt); y += int(50 * u)
        yb = y1z - int(60 * u)
        if cta:
            f3 = _f(int(38 * u), True); w = dr.textlength(cta, font=f3) + 56; dr.rounded_rectangle([x0z, yb - int(70 * u), x0z + w, yb - 4], 40, fill=txt); dr.text((x0z + 28, yb - int(60 * u)), cta, font=f3, fill=ac)
        f4 = _f(int(30 * u)); dr.text((x0z, yb + 6), (nom + ("  ·  " + con if con else "")), font=f4, fill=txt)
    else:
        im = cubrir(foto, W, H).convert("RGBA")
        if est == "cartel":
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 150)); im = Image.alpha_composite(im, ov)
        else:
            deg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(deg); alto = int(H * 0.55)
            for y in range(alto): dd.line([(0, H - alto + y), (W, H - alto + y)], fill=(0, 0, 0, int(225 * (y / alto) ** 1.3)))
            im = Image.alpha_composite(im, deg)
        dr = ImageDraw.Draw(im); wmax = W * (0.80 if not hor else 0.62)
        if est == "marco":
            m = int(28 * u); dr.rectangle([m, m, W - m, H - m], outline=ac + (255,), width=max(4, int(6 * u)))
        f1 = _f(int((92 if est == "cartel" else 70) * u), True); ls = _lineas(dr, tit, f1, wmax)[:4]; lh = int(f1.size * 1.12)
        fsub = _f(int(40 * u)); lsub = _lineas(dr, sub, fsub, wmax)[:3] if sub else []
        bloque = len(ls) * lh + (len(lsub) * int(50 * u) + 14 if lsub else 0) + (int(110 * u) if cta else 0) + int(60 * u)
        if est == "cartel": y = (H - bloque) // 2; x = None
        else: y = H - bloque - int(90 * u); x = int(W * 0.08)
        for l in ls:
            xx = (W - dr.textlength(l, font=f1)) / 2 if est == "cartel" else x
            dr.text((xx, y), l, font=f1, fill="white"); y += lh
        y += 8
        for l in lsub:
            xx = (W - dr.textlength(l, font=fsub)) / 2 if est == "cartel" else x
            dr.text((xx, y), l, font=fsub, fill=(240, 230, 210)); y += int(50 * u)
        y += 14
        if cta:
            f3 = _f(int(40 * u), True); w = dr.textlength(cta, font=f3) + 64; xx = (W - w) / 2 if est == "cartel" else x
            dr.rounded_rectangle([xx, y, xx + w, y + int(72 * u)], 40, fill=ac + (255,)); dr.text((xx + 32, y + int(10 * u)), cta, font=f3, fill=(20, 14, 6)); y += int(100 * u)
        f4 = _f(int(30 * u)); pie = nom + ("  ·  " + con if con else ""); xx = (W - dr.textlength(pie, font=f4)) / 2 if est == "cartel" else x
        dr.text((xx, y), pie, font=f4, fill=ac)
    out = dest or os.path.join(core.carpeta_config(), "anuncios-previa_%s.jpg" % fmt)
    im.convert("RGB").save(out, "JPEG", quality=90); return out


def video(r, cfg, ruta):
    img = pieza(r, cfg, "story", os.path.join(core.carpeta_config(), "anuncio-video.jpg"))
    cmd = [core.ffmpeg(), "-y", "-loglevel", "error", "-loop", "1", "-i", img, "-t", "8", "-vf",
           "zoompan=z='min(zoom+0.0007,1.12)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=200:s=1080x1920:fps=25,format=yuv420p", "-c:v", "libx264", "-movflags", "+faststart", ruta]
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode or not os.path.isfile(ruta): raise RuntimeError("No se pudo crear el vídeo: " + (p.stderr or "")[-160:])


def sugerir(r, cfg):
    c = leer_carta(r); p = next(x for x in c["platos"] if x["id"] == cfg["plato"])
    dato = {"nombre": p.get("nombre", ""), "descripcion": p.get("descripcion", ""), "ingredientes": p.get("ingredientes", []), "etiquetas": p.get("etiquetas", [])}
    objetivo = cfg.get("objetivo") or "que vengan a probarlo"
    pr = ("Eres publicista de un restaurante llamado '%s'. Escribe un anuncio en %s. Objetivo: %s. Usa SOLO estos datos reales del plato: %s. "
          "REGLAS: no inventes precios, ofertas, horarios, premios ni ingredientes. Titular: máximo 6 palabras, directo. Subtítulo: máximo 14 palabras. Llamada a la acción: máximo 3 palabras. "
          "Devuelve SOLO JSON: {\"titular\":\"...\",\"subtitulo\":\"...\",\"cta\":\"...\"}" % (c.get("nombre", ""), marca.lengua(), objetivo, json.dumps(dato, ensure_ascii=False)))
    try:
        j = marca.ia_json(pr); return {"titular": j.get("titular", ""), "subtitulo": j.get("subtitulo", ""), "cta": j.get("cta", ""), "ia": True}
    except Exception as e:
        d = (p.get("descripcion") or "").split(".")[0][:80]
        return {"titular": p.get("nombre", ""), "subtitulo": d, "cta": "Ven a probarlo", "ia": False, "aviso": str(e)}


def guardar(r, cfg):
    c = leer_carta(r); dest = os.path.join(core.carpeta_descargas(), "Anuncio %s %s" % (c.get("nombre", r), datetime.datetime.now().strftime("%Y-%m-%d %H%M%S"))); os.makedirs(dest, exist_ok=True)
    for f in FORMATOS: pieza(r, cfg, f, os.path.join(dest, "anuncio_%s.jpg" % f))
    open(os.path.join(dest, "anuncio_texto.txt"), "w", encoding="utf8").write("%s\n%s\n%s\n%s\n" % (cfg.get("titular", ""), cfg.get("subtitulo", ""), cfg.get("cta", ""), cfg.get("contacto", "")))
    if cfg.get("video"): video(r, cfg, os.path.join(dest, "anuncio_video.mp4"))
    try:
        hp = os.path.join(core.carpeta_config(), "anuncios-historial.json")
        h = json.load(open(hp, encoding="utf8")) if os.path.exists(hp) else []
        h.append({"fecha": datetime.datetime.now().isoformat(timespec="seconds"), "restaurante": r, "titular": cfg.get("titular", ""), "carpeta": dest}); json.dump(h, open(hp, "w", encoding="utf8"), ensure_ascii=False)
    except Exception: pass
    core.abrir(dest); return dest


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _j(self, o, c=200):
        b = json.dumps(o, ensure_ascii=False).encode("utf8"); self.send_response(c); self.send_header("content-type", "application/json"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def _ok(self): return (self.headers.get("Host") or "").split(":")[0] in ("127.0.0.1", "localhost")
    def do_GET(self):
        if not self._ok(): return self._j({"error": "no"}, 403)
        u = urlparse(self.path); q = parse_qs(u.query)
        if u.path == "/":
            b = marca.html(open(os.path.join(AQUI, "anuncios-app.html"), encoding="utf8").read()).replace("__TOKEN__", TOKEN).replace("__ESTILOS__", json.dumps(ESTILOS, ensure_ascii=False)).encode("utf8")
            self.send_response(200); self.send_header("content-type", "text/html; charset=utf-8"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        if (q.get("t") or [""])[0] != TOKEN and self.headers.get("x-cv") != TOKEN: return self._j({"error": "sin permiso"}, 403)
        if u.path == "/api/estado":
            r = (q.get("r") or [""])[0]; rs = restaurantes(); r = r or (rs[0] if rs else ""); c = leer_carta(r) if r else None
            return self._j({"restaurantes": rs, "r": r, "nombre": (c or {}).get("nombre", ""), "platos": [{"id": p["id"], "nombre": p.get("nombre", "")} for p in (c or {}).get("platos", []) if p.get("foto")], "ia": core.claves_estado()})
        if u.path == "/img":
            g = lambda k: (q.get(k) or [""])[0]; r = g("r"); cfg = {k: g(k) for k in ("plato", "estilo", "titular", "subtitulo", "cta", "contacto")}
            try: f = g("f") if g("f") in FORMATOS else "feed"; b = open(pieza(r, cfg, f), "rb").read()
            except Exception as e: return self._j({"error": str(e)}, 500)
            self.send_response(200); self.send_header("content-type", "image/jpeg"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        self._j({"error": "no"}, 404)
    def do_POST(self):
        marca.fijar(self.headers)
        if not self._ok() or self.headers.get("x-cv") != TOKEN: return self._j({"error": "sin permiso"}, 403)
        try: d = json.loads(self.rfile.read(int(self.headers.get("content-length") or 0)) or "{}"); r = d.get("r", "")
        except Exception: return self._j({"error": "datos"}, 400)
        try:
            if self.path == "/api/sugerir": return self._j(dict(sugerir(r, d), ok=True))
            if self.path == "/api/guardar": return self._j({"ok": True, "carpeta": guardar(r, d)})
        except Exception as e: return self._j({"ok": False, "error": str(e)})
        self._j({"error": "no"}, 404)


def puerto():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def main():
    os.makedirs(os.path.dirname(INFO), exist_ok=True)
    if "--parar" in sys.argv:
        try: core.parar_proceso(json.load(open(INFO))["pid"]); print("Anuncios parado.")
        except Exception: print("No estaba en marcha.")
        return
    try:
        i = json.load(open(INFO)); assert core.proceso_vivo(i["pid"]); urllib.request.urlopen("http://127.0.0.1:%d/" % i["port"], timeout=2); print("Ya en marcha."); return
    except Exception: pass
    pt = puerto(); srv = ThreadingHTTPServer(("127.0.0.1", pt), H); json.dump({"pid": os.getpid(), "port": pt}, open(INFO, "w"))
    print("Anuncios en marcha (puerto %d)." % pt, flush=True); srv.serve_forever()


if __name__ == "__main__": main()
