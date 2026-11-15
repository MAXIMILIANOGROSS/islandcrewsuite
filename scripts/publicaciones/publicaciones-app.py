#!/usr/bin/env python3
"""Island Crew · Fábrica de publicaciones y calendario de crecimiento (v1, 100 % local).
Lee los platos de Carta Viva, crea un calendario, escribe los textos con la IA gratuita del cliente,
prepara las piezas por formato y entrega el paquete del día listo para subir. No publica solo: no se conecta a Meta.
Parar: --parar"""
import os, sys, json, re, io, time, base64, secrets, socket, shutil, threading, datetime, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(AQUI, "..", "suite"))
import core, marca
INFO = os.path.expanduser("~/IslandCrewAI/publicaciones-app.json"); TOKEN = secrets.token_hex(16)
BASE = os.path.join(core.carpeta_datos(), "cartas")
FUENTES = ["/System/Library/Fonts/Supplemental/Georgia.ttf", "/System/Library/Fonts/Helvetica.ttc", "C:/Windows/Fonts/georgia.ttf", "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
TIPOS = ["Plato estrella", "Ingrediente protagonista", "Para compartir", "Ven a probarlo", "Plato estrella", "Recomendación"]
FORMATOS = {"feed": (1080, 1350), "story": (1080, 1920), "cuadrado": (1080, 1080)}


def slug(s): return re.sub(r"[^a-z0-9]+", "-", (s or "").lower().encode("ascii", "ignore").decode() or "x").strip("-")
def dir_r(r): return os.path.join(BASE, slug(r))
def leer_carta(r):
    try: return json.load(open(os.path.join(dir_r(r), "carta.json"), encoding="utf8"))
    except Exception: return None
def pj(r): return os.path.join(dir_r(r), "publicaciones.json")
def leer(r):
    try: return json.load(open(pj(r), encoding="utf8"))
    except Exception: return {"posts": []}
def guardar(r, d):
    os.makedirs(dir_r(r), exist_ok=True); t = pj(r) + ".tmp"; json.dump(d, open(t, "w", encoding="utf8"), ensure_ascii=False, indent=1); os.replace(t, pj(r))
def restaurantes():
    try: return sorted(x for x in os.listdir(BASE) if os.path.exists(os.path.join(BASE, x, "carta.json")))
    except Exception: return []


# ---- IA gratis del cliente ----
def ia(prompt):
    k = core.clave("GEMINI_API_KEY"); err = []
    if k:
        cuerpo = json.dumps({"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.8, "responseMimeType": "application/json"}}).encode()
        for m in ("gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-flash-latest"):
            try:
                rq = urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/%s:generateContent" % m, cuerpo, {"Content-Type": "application/json", "x-goog-api-key": k})
                t = json.load(urllib.request.urlopen(rq, timeout=40))["candidates"][0]["content"]["parts"][0]["text"]
                return json.loads(re.sub(r"^```(?:json)?|```$", "", t.strip()).strip())
            except Exception as e: err.append(m + ":" + str(e)[:40])
    g = core.clave("GROQ_API_KEY")
    if g:
        try:
            rq = urllib.request.Request("https://api.groq.com/openai/v1/chat/completions", json.dumps({"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "response_format": {"type": "json_object"}}).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + g, "User-Agent": "IslandCrewSuite/1.0"})
            return json.loads(json.load(urllib.request.urlopen(rq, timeout=40))["choices"][0]["message"]["content"])
        except Exception as e: err.append("groq:" + str(e)[:40])
    raise RuntimeError("Sin IA ahora (" + (", ".join(err) or "falta la clave gratuita de Gemini; ponla repitiendo el asistente") + ").")


def datos_plato(p): return {"nombre": p.get("nombre", ""), "descripcion": p.get("descripcion", ""), "ingredientes": p.get("ingredientes", []), "etiquetas": p.get("etiquetas", []), "categoria": p.get("categoria", "")}


def textos(c, posts, platos):
    """Una sola llamada para todo el calendario. Solo datos reales del plato; nada de precios ni ofertas inventadas."""
    items = [{"i": i, "tipo": x["tipo"], "plato": datos_plato(platos.get(x["plato_id"], {}))} for i, x in enumerate(posts)]
    pr = ("Eres community manager de un restaurante llamado '%s' (%s). Escribe para cada elemento un texto breve de Instagram en %s, cálido, máximo 45 palabras, con 1 o 2 emojis, "
          "que invite a venir o a probarlo. REGLAS: usa SOLO los datos del plato; no inventes precios, ofertas, horarios, premios ni ingredientes; no varíes el nombre del plato. "
          "Cada texto debe ser distinto. Devuelve SOLO JSON: {\"textos\":[{\"i\":0,\"texto\":\"...\",\"hashtags\":[\"#...\",\"#...\",\"#...\"]}]} con 3 a 5 hashtags relevantes. Elementos: %s"
          % (c.get("nombre", ""), c.get("lema", ""), marca.lengua(), json.dumps(items, ensure_ascii=False)))
    r = ia(pr).get("textos", [])
    return {int(t["i"]): t for t in r if "i" in t}


def plan(r, dias, inicio, semana):
    c = leer_carta(r); platos = [p for p in c.get("platos", []) if p.get("foto") and p.get("disponible") is not False]
    if not platos: raise RuntimeError("Primero añade platos con foto en Carta Viva.")
    d0 = datetime.date.fromisoformat(inicio); sel = {3: (0, 2, 4), 4: (0, 1, 3, 5), 5: (0, 1, 2, 4, 5), 7: tuple(range(7))}.get(semana, (0, 2, 4))
    posts = []; k = 0
    for n in range(dias):
        f = d0 + datetime.timedelta(days=n)
        if f.weekday() in sel:
            p = platos[k % len(platos)]
            posts.append({"id": "p%s%d" % (f.strftime("%m%d"), k), "fecha": f.isoformat(), "tipo": TIPOS[k % len(TIPOS)], "plato_id": p["id"], "texto": "", "hashtags": [], "estado": "borrador"}); k += 1
    by = {p["id"]: p for p in platos}
    try:
        tx = textos(c, posts, by); aviso = ""
    except Exception as e:
        tx = {}; aviso = str(e)
    for i, x in enumerate(posts):
        t = tx.get(i); nom = by[x["plato_id"]]["nombre"]
        x["texto"] = (t or {}).get("texto") or "%s en %s. Ven a probarlo." % (nom, c.get("nombre", ""))
        x["hashtags"] = (t or {}).get("hashtags") or []
    d = leer(r); d["posts"] = [p for p in d["posts"] if p["estado"] == "publicado"] + posts; d["posts"].sort(key=lambda p: p["fecha"]); guardar(r, d)
    return len(posts), aviso


def _fuente(t):
    from PIL import ImageFont
    for f in FUENTES:
        try: return ImageFont.truetype(f, t)
        except Exception: pass
    return ImageFont.load_default()


def pieza(r, post, fmt):
    from PIL import Image, ImageDraw, ImageOps
    c = leer_carta(r); p = next(x for x in c["platos"] if x["id"] == post["plato_id"]); W, H = FORMATOS[fmt]
    im = ImageOps.exif_transpose(Image.open(os.path.join(dir_r(r), "fotos", p["foto"]))).convert("RGB"); s = max(W / im.width, H / im.height)
    im = im.resize((int(im.width * s) + 1, int(im.height * s) + 1), Image.LANCZOS); L, T = (im.width - W) // 2, (im.height - H) // 2; im = im.crop((L, T, L + W, T + H)).convert("RGBA")
    deg = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dd = ImageDraw.Draw(deg); alto = int(H * 0.42)
    for y in range(alto): dd.line([(0, H - alto + y), (W, H - alto + y)], fill=(0, 0, 0, int(200 * (y / alto) ** 1.4)))
    im = Image.alpha_composite(im, deg); dr = ImageDraw.Draw(im); ac = c.get("color_acento") or "#e2bd68"
    f1 = _fuente(int(W * 0.075)); f2 = _fuente(int(W * 0.036)); y = H - int(H * 0.17) - (60 if fmt == "story" else 0)
    nom = p["nombre"]
    while dr.textlength(nom, font=f1) > W * 0.86 and len(nom) > 8: nom = nom[:-2]
    dr.text((W * 0.07, y), nom, font=f1, fill="white"); dr.text((W * 0.07, y + int(W * 0.1)), (c.get("nombre") or "").upper(), font=f2, fill=ac)
    d = os.path.join(dir_r(r), "publicaciones"); os.makedirs(d, exist_ok=True); out = os.path.join(d, "%s_%s.jpg" % (post["id"], fmt)); im.convert("RGB").save(out, "JPEG", quality=90); return out


def paquete(r, fecha):
    d = leer(r); ps = [p for p in d["posts"] if p["fecha"] == fecha]
    if not ps: raise RuntimeError("No hay publicaciones ese día.")
    c = leer_carta(r); dest = os.path.join(core.carpeta_descargas(), "Paquete %s %s" % (c.get("nombre", r), fecha)); os.makedirs(dest, exist_ok=True)
    for p in ps:
        for fmt in ("feed", "story"): shutil.copyfile(pieza(r, p, fmt), os.path.join(dest, "%s_%s.jpg" % (p["id"], fmt)))
        pl = next((x for x in c["platos"] if x["id"] == p["plato_id"]), {}); vid = os.path.join(dir_r(r), "videos", pl.get("video") or "x")
        if os.path.isfile(vid): shutil.copyfile(vid, os.path.join(dest, "%s_reel.mp4" % p["id"]))
        open(os.path.join(dest, "%s_texto.txt" % p["id"]), "w", encoding="utf8").write(p["texto"] + "\n\n" + " ".join(p["hashtags"]) + "\n")
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
            b = open(os.path.join(AQUI, "publicaciones-app.html"), encoding="utf8").read().replace("__TOKEN__", TOKEN); b = marca.html(b).encode("utf8"); self.send_response(200); self.send_header("content-type", "text/html; charset=utf-8"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        if (q.get("t") or [""])[0] != TOKEN and self.headers.get("x-cv") != TOKEN: return self._j({"error": "sin permiso"}, 403)
        if u.path == "/api/estado":
            r = (q.get("r") or [""])[0]; rs = restaurantes(); r = r or (rs[0] if rs else "")
            c = leer_carta(r) if r else None
            return self._j({"restaurantes": rs, "r": r, "nombre": (c or {}).get("nombre", ""), "platos": {p["id"]: p.get("nombre", "") for p in (c or {}).get("platos", [])}, "posts": leer(r)["posts"] if r else [], "ia": core.claves_estado()})
        if u.path == "/img":
            r = (q.get("r") or [""])[0]; p = next((x for x in leer(r)["posts"] if x["id"] == (q.get("id") or [""])[0]), None)
            if not p: return self._j({"error": "no"}, 404)
            b = open(pieza(r, p, "feed"), "rb").read(); self.send_response(200); self.send_header("content-type", "image/jpeg"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        self._j({"error": "no"}, 404)
    def do_POST(self):
        marca.fijar(self.headers)
        if not self._ok() or self.headers.get("x-cv") != TOKEN: return self._j({"error": "sin permiso"}, 403)
        try: d = json.loads(self.rfile.read(int(self.headers.get("content-length") or 0)) or "{}"); r = d.get("r", "")
        except Exception: return self._j({"error": "datos"}, 400)
        try:
            if self.path == "/api/plan":
                n, aviso = plan(r, int(d.get("dias", 30)), d.get("inicio") or datetime.date.today().isoformat(), int(d.get("semana", 3))); return self._j({"ok": True, "n": n, "aviso": aviso})
            if self.path == "/api/post":
                s = leer(r); x = next(p for p in s["posts"] if p["id"] == d["id"])
                for k in ("texto", "estado", "fecha"):
                    if k in d: x[k] = d[k]
                if "hashtags" in d: x["hashtags"] = [h for h in re.split(r"\s+", d["hashtags"]) if h]
                guardar(r, s); return self._j({"ok": True})
            if self.path == "/api/texto":
                s = leer(r); i = next(k for k, p in enumerate(s["posts"]) if p["id"] == d["id"]); c = leer_carta(r); by = {p["id"]: p for p in c["platos"]}
                t = textos(c, [s["posts"][i]], by).get(0)
                if t: s["posts"][i]["texto"] = t.get("texto", s["posts"][i]["texto"]); s["posts"][i]["hashtags"] = t.get("hashtags", [])
                guardar(r, s); return self._j({"ok": True})
            if self.path == "/api/paquete": return self._j({"ok": True, "carpeta": paquete(r, d["fecha"])})
        except Exception as e: return self._j({"ok": False, "error": str(e)}, 200)
        self._j({"error": "no"}, 404)


def puerto():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def main():
    os.makedirs(os.path.dirname(INFO), exist_ok=True)
    if "--parar" in sys.argv:
        try: core.parar_proceso(json.load(open(INFO))["pid"]); print("Publicaciones parado.")
        except Exception: print("No estaba en marcha.")
        return
    try:
        i = json.load(open(INFO)); assert core.proceso_vivo(i["pid"]); urllib.request.urlopen("http://127.0.0.1:%d/" % i["port"], timeout=2); print("Ya en marcha."); return
    except Exception: pass
    pt = puerto(); srv = ThreadingHTTPServer(("127.0.0.1", pt), H); json.dump({"pid": os.getpid(), "port": pt}, open(INFO, "w"))
    print("Publicaciones en marcha (puerto %d)." % pt, flush=True); srv.serve_forever()


if __name__ == "__main__": main()
