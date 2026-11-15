#!/usr/bin/env python3
"""Sube piezas APROBADAS a tu canal de YouTube como PRIVADAS (tú decides después si las haces públicas).
Uso:  python3 scripts/youtube-subir.py [--seco] [--titulo "..."] [--descripcion "..."] archivo.mp4|archivo.wav [...]
- Solo sube los archivos que le nombres: nunca recorre carpetas ni sube nada por su cuenta.
- Si el archivo es de audio, crea antes un vídeo con una imagen fija (ffmpeg).
- Guarda un registro (huella sha256) para no subir dos veces lo mismo.
- Siempre: privacyStatus=private y contenido sintético declarado.
Secretos: client_secret.json y token.json viven SOLO en ~/IslandCrewAI/youtube/ (permisos 600). Este script nunca los imprime."""
# PATH_EXTRA: el worker arranca desde launchd sin /opt/homebrew/bin; sin esto no encuentra ffmpeg ni ffprobe.
import os as _os
_os.environ["PATH"] = _os.pathsep.join([x for x in ["/opt/homebrew/bin", "/usr/local/bin", "/opt/homebrew/sbin"] if x not in _os.environ.get("PATH", "")] + [_os.environ.get("PATH", "")])

import base64, hashlib, http.server, json, os, secrets, subprocess, sys, threading, time, urllib.parse, urllib.request, urllib.error, webbrowser
DIR = os.path.expanduser(os.environ.get("YT_DIR", "~/IslandCrewAI/youtube")); SECRETO = os.path.join(DIR, "client_secret.json"); TOKEN = os.path.join(DIR, "token.json"); REGISTRO = os.path.join(DIR, "subidas.json")
IMAGEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "cabra360", "cabra-2.webp")
MAX_POR_EJECUCION = 5  # la cuota gratuita de la API da pocas subidas al día
ALCANCE = "https://www.googleapis.com/auth/youtube.upload https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/yt-analytics.readonly"  # yt-analytics: impresiones, CTR, retención y suscriptores · readonly: solo para leer vistas y me gusta de lo ya subido

def registrar_biblioteca(entrada):
    """Apunta el vídeo subido en la Biblioteca viva (necesita ISLANDCREW_URL y CRON_SECRET en tu Terminal; si faltan, no hace nada)."""
    base, tk = os.environ.get("ISLANDCREW_URL"), os.environ.get("CRON_SECRET")
    if not base or not tk: return
    try:
        r = urllib.request.urlopen(urllib.request.Request(base.rstrip("/") + "/api/oficina/biblioteca-registrar", json.dumps(entrada).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + tk}), timeout=30); print("Biblioteca:", json.load(r))
    except Exception as e: print("No se pudo registrar en la Biblioteca:", e)
def registrar_publicacion(titulo, url, estado="subida_privada", formato="short"):
    """Anota la subida en el registro real de publicaciones (cuenta para la cuota diaria de YouTube Shorts). Sin variables, no hace nada."""
    base, tk = os.environ.get("ISLANDCREW_URL"), os.environ.get("CRON_SECRET")
    if not base or not tk: return
    try: urllib.request.urlopen(urllib.request.Request(base.rstrip("/") + "/api/oficina/publicacion-registrar", json.dumps({"plataforma": "youtube", "formato": formato, "titulo": titulo, "url": url, "estado": estado, "origen": "youtube-subir"}).encode(), {"Content-Type": "application/json", "Authorization": "Bearer " + tk}), timeout=30)
    except Exception as e: print("No se pudo anotar la publicación:", e)
def huella(ruta):
    h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
def cargar(ruta, defecto):
    try: return json.load(open(ruta))
    except Exception: return defecto
def guardar_seguro(ruta, datos):
    os.makedirs(os.path.dirname(ruta), exist_ok=True); open(ruta, "w").write(json.dumps(datos, indent=2)); os.chmod(ruta, 0o600)
CREDITO = "Autoría: obra creada por la IA que Maximiliano Olmos Sánchez ha creado para la creación de música y cine · Island Crew (islandcrew.es)"
DERECHOS = "Todos los derechos reservados. Prohibida su reproducción, redistribución, modificación o uso comercial sin autorización escrita de Island Crew."
IA_LICENCIA = "Obra creada con la inteligencia artificial de Island Crew (las cabras). La licencia de esta obra, de su guion y de su montaje pertenece a Island Crew; las tomas y pistas de terceros conservan su propia licencia."
def con_credito(descripcion):
    """Toda subida lleva el crédito de autoría y «Todos los derechos reservados» (una sola vez, aunque la descripción ya los traiga)."""
    d = str(descripcion or "").strip()
    if "Maximiliano Olmos Sánchez" not in d: d = (d + "\n\n" if d else "") + "© " + CREDITO
    if "todos los derechos reservados" not in d.lower(): d = d + "\n" + DERECHOS
    if "inteligencia artificial de island crew" not in d.lower(): d = d + "\n" + IA_LICENCIA
    return d
def imagen_credito():
    """La imagen fija del vídeo con una franja de autoría («IA de Maximiliano Olmos Sánchez · Música y cine»). Si falta Pillow, usa la imagen sin franja."""
    try:
        from PIL import Image, ImageDraw, ImageFont
        import tempfile
        im = Image.open(IMAGEN).convert("RGB"); w, h = im.size; d = ImageDraw.Draw(im, "RGBA"); alto = max(36, h // 12)
        d.rectangle([0, h - alto, w, h], fill=(0, 0, 0, 170)); txt = "IA de Maximiliano Olmos Sánchez · Música y cine · Island Crew"
        try: f = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", max(14, alto // 2))
        except Exception: f = ImageFont.load_default()
        tw = d.textlength(txt, font=f); d.text(((w - tw) / 2, h - alto + (alto - max(14, alto // 2)) / 2), txt, font=f, fill=(255, 255, 255, 235))
        out = os.path.join(tempfile.mkdtemp(prefix="ic_img_"), "portada_credito.png"); im.save(out); return out
    except Exception: return IMAGEN
def metadatos(titulo, descripcion, sintetico=True, publico=False, programar=None, categoria="10", no_listado=False):
    """Cuerpo de la subida. Privado salvo que se pida público expresamente (modo autónomo con «publicar» encendido). Siempre marcado como contenido sintético."""
    d = {"snippet": {"title": titulo[:100], "description": con_credito(str(descripcion or "")[:4300])[:4900], "categoryId": categoria}, "status": {"privacyStatus": "public" if publico else "private", "selfDeclaredMadeForKids": False, "license": "youtube"}}
    if sintetico: d["status"]["containsSyntheticMedia"] = True
    if programar: d["status"]["privacyStatus"] = "private"; d["status"]["publishAt"] = programar  # YouTube lo hace público solo a esa hora (UTC, ISO 8601); hasta entonces sigue privado
    if no_listado and not publico and not programar: d["status"]["privacyStatus"] = "unlisted"
    return d
VF_BASE = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2:color=black,format=yuv420p"
_FUENTE = "/System/Library/Fonts/Supplemental/Arial.ttf"
VF_CREDITO = (",drawbox=x=0:y=ih-44:w=iw:h=44:color=black@0.55:t=fill,drawtext=fontfile=" + _FUENTE + ":text='IA de Maximiliano Olmos Sánchez · Música y cine · Island Crew':fontcolor=white@0.92:fontsize=22:x=(w-text_w)/2:y=h-33") if os.path.exists(_FUENTE) else ""
_IMG = {"arte": False}  # True cuando la imagen viene de la web (arte temático sin texto): entonces el título lo dibuja el Mac
def imagen_para(meta):
    """Imagen del vídeo adaptada a la música (isla, estilo y momento), generada por la web. Si no se puede, usa la cabra fija."""
    try:
        meta = meta or {}; base, tk = os.environ.get("ISLANDCREW_URL", "https://islandcrew.es"), os.environ.get("CRON_SECRET")
        if not tk or not meta.get("titulo"): return imagen_credito()
        import tempfile
        cuerpo = json.dumps({"titulo": meta.get("titulo"), "estilo": meta.get("estilo", ""), "etiquetas": meta.get("etiquetas", []), "imagen": meta.get("imagen") or {}, "formato": meta.get("formato", "")}).encode()
        rq = urllib.request.Request(base.rstrip("/") + "/api/oficina/youtube-imagen", cuerpo, {"Content-Type": "application/json", "Authorization": "Bearer " + tk})
        png = urllib.request.urlopen(rq, timeout=60).read()
        if len(png) < 2000: return imagen_credito()
        _IMG["arte"] = not (meta.get("imagen") or {}).get("url")
        out = os.path.join(tempfile.mkdtemp(prefix="ic_img_"), "portada_musical.png"); open(out, "wb").write(png); print("Imagen del vídeo adaptada a la música:", meta.get("titulo"), flush=True); return out
    except Exception as e:
        print("(aviso) imagen adaptada no disponible, se usa la cabra:", str(e)[:100], flush=True); return imagen_credito()
def meta_de_archivo(ruta):
    """Título y estilo a partir del nombre del archivo (p. ej. 20261104-151852_lofi_cancion_es.wav)."""
    b = os.path.splitext(os.path.basename(ruta))[0]; p = b.split("_"); return {"titulo": b, "estilo": p[1] if len(p) > 1 else "", "etiquetas": []}
def _texto_envuelto(t, ancho):
    pal, lin, act = str(t).split(), [], ""
    for w in pal:
        if act and len(act) + 1 + len(w) > ancho: lin.append(act); act = w
        else: act = (act + " " + w).strip()
    if act: lin.append(act)
    return "\n".join(lin[:4])
def _capa_texto(titulo, ancho, tam, y, carpeta, nombre):
    """Trozo de filtro drawtext con el título envuelto (usa un archivo de texto: sin problemas de comillas). Vacío si no hay fuente del sistema."""
    if not os.path.exists(_FUENTE): return ""
    tf = os.path.join(carpeta, nombre); open(tf, "w", encoding="utf8").write(_texto_envuelto(titulo, ancho))
    return ",drawtext=fontfile=" + _FUENTE + ":textfile=" + tf + f":fontcolor=white:fontsize={tam}:line_spacing=12:borderw=4:bordercolor=black@0.85:x=(w-text_w)/2:y={y}"
def hacer_short(audio, meta, titulo, salida, tmp):
    """Short vertical 1080×1920 de ~40 s: la parte central de la canción sobre su arte, con el título y tu nombre. Devuelve la ruta o None."""
    try:
        dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", audio]).decode().strip())
        largo = min(40.0, dur); ini = max(0.0, min(dur * 0.3, dur - largo)); img = imagen_para({**(meta or {}), "formato": "cuadrado"})
        txt = _capa_texto(titulo, 20, 72, 1480, tmp, "short_titulo.txt"); cred = (",drawtext=fontfile=" + _FUENTE + ":text='IA de Maximiliano Olmos Sánchez · Island Crew':fontcolor=white@0.9:fontsize=30:x=(w-text_w)/2:y=1850") if os.path.exists(_FUENTE) else ""
        fc = "[0:v]split=2[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=40:8,eq=brightness=-0.2[bg];[b]scale=1000:1000:force_original_aspect_ratio=decrease[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2-160" + txt + cred + ",format=yuv420p[v];[1:a]afade=t=in:st=0:d=0.5,afade=t=out:st=" + f"{max(largo - 1.2, 0):.2f}" + ":d=1.2[au]"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-framerate", "25", "-i", img, "-ss", f"{ini:.2f}", "-t", f"{largo:.2f}", "-i", audio, "-filter_complex", fc, "-map", "[v]", "-map", "[au]", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-c:a", "aac", "-b:a", "192k", "-shortest", "-t", f"{largo:.2f}", "-movflags", "+faststart", salida])
        if r.returncode != 0 or not os.path.exists(salida) and False: print("(el Short no se pudo montar)", flush=True); return None
        return salida if os.path.exists(salida) else None
    except Exception as e: print("(Short: fallo)", str(e)[:120], flush=True); return None
def poner_miniatura(video_id, meta, titulo, tok, tmp):
    """Miniatura 1280×720 (arte + título) para el vídeo recién subido. Mejor esfuerzo: YouTube exige canal verificado; si lo rechaza, solo lo cuenta en el log."""
    try:
        img = imagen_para(meta or {}); jpg = os.path.join(tmp, "miniatura.jpg")
        vf = "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,eq=brightness=-0.12" + _capa_texto(titulo, 24, 78, "h-text_h-70", tmp, "mini_titulo.txt") + ",format=yuvj420p"
        r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", img, "-vf", vf, "-frames:v", "1", "-q:v", "3", jpg])
        if r.returncode != 0 or not os.path.exists(jpg) or os.path.getsize(jpg) > 2_000_000: print("(miniatura no generada o demasiado grande)", flush=True); return False
        rq = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=" + video_id, open(jpg, "rb").read(), {"Authorization": "Bearer " + tok, "Content-Type": "image/jpeg"}, method="POST")
        urllib.request.urlopen(rq, timeout=60); print("Miniatura puesta en YouTube.", flush=True); return True
    except urllib.error.HTTPError as e: print("(YouTube no aceptó la miniatura:", e.code, e.read().decode(errors="ignore")[:160] + ")", flush=True); return False
    except Exception as e: print("(miniatura: fallo)", str(e)[:120], flush=True); return False
def miniatura_jpg(video_id, jpg, tok):
    """Pone como miniatura de YouTube exactamente la imagen indicada (la portada creada). Devuelve (ok, motivo)."""
    try:
        if not jpg or not os.path.isfile(jpg): return False, "no hay portada creada"
        datos = open(jpg, "rb").read()
        if len(datos) > 2_000_000: return False, "la portada pesa más de 2 MB"
        rq = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/thumbnails/set?videoId=" + video_id, datos, {"Authorization": "Bearer " + tok, "Content-Type": "image/jpeg"}, method="POST")
        urllib.request.urlopen(rq, timeout=90); return True, ""
    except urllib.error.HTTPError as e:
        t = e.read().decode(errors="ignore")
        return False, ("YouTube pide verificar tu canal por teléfono para usar miniaturas personalizadas (youtube.com/verify)" if e.code == 403 else f"YouTube respondió {e.code}: {t[:120]}")
    except Exception as e: return False, str(e)[:120]
def a_video(ruta, meta=None):
    if ruta.lower().endswith((".mp4", ".mov", ".mkv", ".webm")): return ruta
    import tempfile
    salida = os.path.join(tempfile.mkdtemp(prefix="ic_yt_"), os.path.basename(os.path.splitext(ruta)[0]) + "_yt.mp4")  # carpeta temporal: el servicio de launchd puede no tener permiso de escritura junto al audio
    _IMG["arte"] = False; img = (meta or {}).get("portada") or imagen_para(meta or meta_de_archivo(ruta)); tit = ""
    if _IMG["arte"] and os.path.exists(_FUENTE):
        try: tit = _capa_texto((meta or {}).get("titulo") or "", 22, 44, "h-232", os.path.dirname(img), "t_titulo.txt") + ",drawtext=fontfile=" + _FUENTE + ":text='ISLAND CREW':fontcolor=white@0.85:fontsize=22:borderw=2:bordercolor=black@0.8:x=(w-text_w)/2:y=h-98"
        except Exception: tit = ""
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", img, "-i", ruta, "-vf", VF_BASE + ("" if (meta or {}).get("portada") else tit + VF_CREDITO), "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "256k", "-shortest", salida]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0 and VF_CREDITO and not (meta or {}).get("portada"):  # sin drawtext en este ffmpeg: se reintenta sin la franja de autoría (la autoría va en la descripción)
        cmd[cmd.index("-vf") + 1] = VF_BASE; r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0: raise RuntimeError(f"ffmpeg falló (código {r.returncode}): {(r.stderr or '').strip()[-300:]} | audio={ruta} | imagen existe={os.path.exists(IMAGEN)}")
    return salida

def post_form(url, datos):
    r = urllib.request.Request(url, urllib.parse.urlencode(datos).encode(), {"Content-Type": "application/x-www-form-urlencoded"})
    return json.load(urllib.request.urlopen(r, timeout=60))
_WEB = {"t": 0, "tok": ""}
def _token_web():
    """Token fresco pedido a la web (YouTube conectado con el botón «Conectar YouTube»). Si no está conectado o falla, devuelve None y se usa el método local."""
    base, tk = os.environ.get("ISLANDCREW_URL"), os.environ.get("CRON_SECRET")
    if not base or not tk: return None
    if _WEB["tok"] and _WEB["t"] > time.time(): return _WEB["tok"]
    try:
        r = json.load(urllib.request.urlopen(urllib.request.Request(base.rstrip("/") + "/api/oficina/youtube-token", b"{}", {"Content-Type": "application/json", "Authorization": "Bearer " + tk}), timeout=30))
        if r.get("ok") and r.get("access_token"): _WEB.update(tok=r["access_token"], t=time.time() + min(int(r.get("expires_in", 3000)), 3000) - 120); return _WEB["tok"]
    except Exception: pass
    return None
def token_valido(interactivo=True, forzar=False):
    if not forzar:
        w = _token_web()
        if w: return w
    s = cargar(SECRETO, None)
    if not s: sys.exit(f"Falta {SECRETO}. Sigue docs/YOUTUBE_SUBIDA_PRIVADA.md para crearlo (es gratis).")
    c = s.get("installed") or s.get("web") or {}; t = cargar(TOKEN, None)
    if t and not forzar and t.get("expira", 0) > time.time() + 60: return t["access_token"]
    if t and t.get("refresh_token") and not forzar:
        try:
            n = post_form(c["token_uri"], {"client_id": c["client_id"], "client_secret": c["client_secret"], "refresh_token": t["refresh_token"], "grant_type": "refresh_token"})
            t.update(access_token=n["access_token"], expira=time.time() + n.get("expires_in", 3000)); guardar_seguro(TOKEN, t); return t["access_token"]
        except urllib.error.HTTPError:
            if not interactivo: sys.exit("El permiso de YouTube caducó: ejecuta a mano scripts/youtube-subir.py una vez para reautorizar.")
            print("El permiso caducó: toca autorizar otra vez en el navegador.")
    if not interactivo: sys.exit("Falta autorizar YouTube: ejecuta a mano scripts/youtube-subir.py una vez.")
    verificador = base64.urlsafe_b64encode(secrets.token_bytes(48)).rstrip(b"=").decode(); reto = base64.urlsafe_b64encode(hashlib.sha256(verificador.encode()).digest()).rstrip(b"=").decode(); estado = secrets.token_urlsafe(16); recibido = {}
    class H(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query); recibido.update({k: v[0] for k, v in q.items()})
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers(); self.wfile.write("<h2>Listo. Puedes cerrar esta pestaña y volver al Terminal.</h2>".encode())
        def log_message(self, *a): pass
    srv = http.server.HTTPServer(("127.0.0.1", 0), H); puerto = srv.server_address[1]; redir = f"http://127.0.0.1:{puerto}"
    url = c["auth_uri"] + "?" + urllib.parse.urlencode({"client_id": c["client_id"], "redirect_uri": redir, "response_type": "code", "scope": ALCANCE, "code_challenge": reto, "code_challenge_method": "S256", "state": estado, "access_type": "offline", "prompt": "consent"})
    print("Se abre el navegador para que autorices SOLO la subida de vídeos a tu canal…"); webbrowser.open(url); threading.Thread(target=srv.handle_request).start()
    for _ in range(300):
        if recibido: break
        time.sleep(1)
    srv.server_close()
    if recibido.get("state") != estado or "code" not in recibido: sys.exit("No se completó la autorización.")
    n = post_form(c["token_uri"], {"client_id": c["client_id"], "client_secret": c["client_secret"], "code": recibido["code"], "code_verifier": verificador, "redirect_uri": redir, "grant_type": "authorization_code"})
    guardar_seguro(TOKEN, {"access_token": n["access_token"], "refresh_token": n.get("refresh_token"), "expira": time.time() + n.get("expires_in", 3000)}); return n["access_token"]

def subir(ruta, titulo, descripcion, tok, publico=False, programar=None, categoria="10", no_listado=False):
    cuerpo = json.dumps(metadatos(titulo, descripcion, True, categoria=categoria)).encode()
    for intento in (True, False):
        r = urllib.request.Request("https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable&part=snippet,status", json.dumps(metadatos(titulo, descripcion, intento, publico, programar, categoria, no_listado)).encode(), {"Authorization": f"Bearer {tok}", "Content-Type": "application/json; charset=UTF-8", "X-Upload-Content-Type": "video/*", "X-Upload-Content-Length": str(os.path.getsize(ruta))})
        try: loc = urllib.request.urlopen(r, timeout=60).headers["Location"]; break
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")
            if intento and e.code == 400 and "containsSyntheticMedia" in msg: print("AVISO: la API no acepta el campo de contenido sintético; márcalo a mano en YouTube Studio."); continue
            sys.exit(f"YouTube rechazó la subida ({e.code}): {msg[:300]}")
    datos = open(ruta, "rb").read(); r = urllib.request.Request(loc, datos, {"Content-Type": "video/*", "Content-Length": str(len(datos))}, method="PUT")
    try: return json.load(urllib.request.urlopen(r, timeout=3600))
    except urllib.error.HTTPError as e: sys.exit(f"Fallo al enviar el vídeo ({e.code}): {e.read().decode(errors='ignore')[:300]}")

def estado_permiso():
    """ok / caducado / sin_autorizar, sin abrir nada. Intenta renovar el permiso en silencio."""
    if not cargar(SECRETO, None) or not cargar(TOKEN, None): return "sin_autorizar"
    try: token_valido(False); return "ok"
    except SystemExit: return "caducado"
    except Exception: return "ok"  # fallo de red: no se declara caducado
def subir_autonomo(ruta, titulo, publico, max_dia=6):
    """Para el trabajador del Mac. Devuelve (url, estado) o (None, motivo). Respeta un tope diario local y no repite archivos. Si YouTube deja el vídeo privado (proyecto de API sin auditar), lo registra como privado: nunca finge que es público."""
    reg = cargar(REGISTRO, {}); hoy = time.strftime("%Y-%m-%d")
    if sum(1 for v in reg.values() if str(v.get("fecha", "")).startswith(hoy)) >= max_dia: return None, "tope diario de subidas alcanzado"
    h = huella(ruta)
    if h in reg: return reg[h]["url"], "ya subido"
    d = "Pieza creada con Island Crew · Cabra Beats. Contenido generado con IA (música sintética)."
    v = a_video(ruta)
    try: r = subir(v, titulo, d, token_valido(False), publico)
    finally:
        if v != ruta and os.path.basename(v).endswith("_yt.mp4"):
            try: os.remove(v)  # el vídeo intermedio ya no hace falta: libera espacio
            except OSError: pass
    real = (r.get("status") or {}).get("privacyStatus", "private"); real_prog = (r.get("status") or {}).get("publishAt") or ""; url = f"https://studio.youtube.com/video/{r['id']}/edit"
    reg[h] = {"archivo": os.path.basename(ruta), "id": r["id"], "url": url, "fecha": time.strftime("%Y-%m-%d %H:%M"), "privacidad": real, "programado_para": real_prog}; guardar_seguro(REGISTRO, reg)
    est = "publicada" if real == "public" else "subida_privada"; registrar_publicacion(titulo, url, est, "video")
    registrar_biblioteca({"tipo": "video", "titulo": titulo[:120], "descripcion": "Subido a YouTube (" + real + ")", "origen": "enlace", "url": url, "ruta_local": ruta, "etiquetas": ["youtube"]})
    return url, est
def medir_youtube(dias=30):
    """Cifras reales de lo ya subido (vistas, me gusta, comentarios) de los últimos `dias` días. Devuelve (lista, aviso). Si el permiso no incluye lectura, avisa de que hay que reautorizar; nunca inventa cifras."""
    reg = cargar(REGISTRO, {}); lim = time.strftime("%Y-%m-%d", time.localtime(time.time() - dias * 86400))
    ids = [v["id"] for v in reg.values() if v.get("id") and str(v.get("fecha", ""))[:10] >= lim][:50]
    if not ids: return [], ""
    try: tok = token_valido(False)
    except SystemExit: return [], "permiso de YouTube caducado"
    try:
        r = urllib.request.Request("https://www.googleapis.com/youtube/v3/videos?part=statistics&id=" + ",".join(ids), headers={"Authorization": f"Bearer {tok}"}); d = json.load(urllib.request.urlopen(r, timeout=30))
    except urllib.error.HTTPError as e:
        return [], ("falta el permiso de lectura: Acciones → Reautorizar YouTube en el Mac" if e.code in (401, 403) else f"YouTube respondió {e.code}")
    except Exception as e: return [], "sin red para medir YouTube"
    return [{"ref": x["id"], "vistas": int(x.get("statistics", {}).get("viewCount", 0)), "me_gusta": int(x.get("statistics", {}).get("likeCount", 0)), "comentarios": int(x.get("statistics", {}).get("commentCount", 0))} for x in d.get("items", [])], ""
def reintentar_liberar_web(fm_web):
    """Red de seguridad: si la liberación inmediata falló (sin red, web caída...), se repite aquí hasta que el servidor la confirme. El servidor es idempotente y sigue protegiendo lo que es producto de clientes."""
    reg = cargar(REGISTRO, {}); hechos = 0; cambio = False
    for k, v in list(reg.items()):
        if not k.startswith("pedido-") or v.get("web_liberada") is not False or not v.get("web_ids"): continue
        try:
            rl = fm_web("/api/oficina/biblioteca-liberar", {"ids": v["web_ids"], "video": v["id"]})
            if (rl or {}).get("ok"): v["web_liberada"] = True; cambio = True; hechos += int(rl.get("borrados", 0))
        except Exception: pass
    if cambio: guardar_seguro(REGISTRO, reg)
    return hechos
def liberar_subidos(carpeta, dias):
    """Borra del disco los audios ya subidos a YouTube (comprobado por huella en subidas.json) con más de `dias` días. Con dias<0 no borra nada; con 0 borra en cuanto está subido. Solo toca archivos de audio dentro de `carpeta`. Devuelve (archivos, GB liberados)."""
    if dias < 0 or not os.path.isdir(carpeta): return 0, 0.0
    reg = cargar(REGISTRO, {}); n = 0; b = 0; limite = time.time() - dias * 86400
    for nombre in os.listdir(carpeta):
        r = os.path.join(carpeta, nombre)
        if not nombre.lower().endswith((".mp3", ".wav", ".flac", ".ogg", "_yt.mp4")) or not os.path.isfile(r) or os.path.getmtime(r) > limite: continue
        if nombre.endswith("_yt.mp4") or huella(r) in reg:
            try: b += os.path.getsize(r); os.remove(r); n += 1
            except OSError: pass
    return n, round(b / 1e9, 2)
if __name__ == "__main__":
    if "--reautorizar" in sys.argv: token_valido(True, True); print("Permiso de YouTube renovado."); sys.exit(0)
    a = sys.argv[1:]; seco = "--seco" in a; titulo = descripcion = None; archivos = []; i = 0
    while i < len(a):
        if a[i] == "--seco": pass
        elif a[i] == "--titulo": i += 1; titulo = a[i]
        elif a[i] == "--descripcion": i += 1; descripcion = a[i]
        else: archivos.append(a[i])
        i += 1
    if not archivos: sys.exit(__doc__)
    if len(archivos) > MAX_POR_EJECUCION: sys.exit(f"Máximo {MAX_POR_EJECUCION} archivos por ejecución (cuota diaria de la API).")
    reg = cargar(REGISTRO, {}); tok = None
    for ruta in archivos:
        ruta = os.path.abspath(os.path.expanduser(ruta))
        if not os.path.isfile(ruta): print("No existe:", ruta); continue
        h = huella(ruta)
        if h in reg: print("Ya subido antes, lo salto:", os.path.basename(ruta), "→", reg[h]["url"]); continue
        t = titulo or os.path.splitext(os.path.basename(ruta))[0].replace("_", " "); d = descripcion or "Pieza creada con Island Crew · Cabra Beats. Contenido generado con IA (música sintética)."
        if seco: print("[SECO] subiría", os.path.basename(ruta), "como PRIVADO con título:", t, "| cuerpo:", json.dumps(metadatos(t, d))); continue
        tok = tok or token_valido(); v = a_video(ruta); print("Subiendo", os.path.basename(v), "como PRIVADO…", flush=True); r = subir(v, t, d, tok)
        url = f"https://studio.youtube.com/video/{r['id']}/edit"; reg[h] = {"archivo": os.path.basename(ruta), "id": r["id"], "url": url, "fecha": time.strftime("%Y-%m-%d %H:%M")}; guardar_seguro(REGISTRO, reg); print("OK (privado):", url); registrar_publicacion(t, url); registrar_biblioteca({"tipo": "video", "titulo": t[:120], "descripcion": "Subido a YouTube como privado", "origen": "enlace", "url": url, "ruta_local": ruta, "etiquetas": ["youtube"]})

def _dur(ruta):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", ruta]).decode().strip())
def _marca(seg):
    seg = int(seg); h, r = divmod(seg, 3600); m, s2 = divmod(r, 60)
    return f"{h}:{m:02d}:{s2:02d}" if h else f"{m}:{s2:02d}"
def subir_pedido(fm_web, peticion, carpeta):
    """Subida pedida desde la web: una canción sola o un disco (todas las pistas en un solo vídeo, con capítulos). Devuelve la URL. Lanza una excepción con el motivo si falla."""
    import tempfile, shutil
    pedidas = peticion.get("piezas", [])
    # Canciones que solo viven en tu disco (sin copia en la web): se usa el archivo local directamente.
    locales = {x["id"]: os.path.expanduser(x["ruta"]) for x in pedidas if x.get("ruta") and os.path.isfile(os.path.expanduser(x["ruta"]))}
    resto = [x["id"] for x in pedidas if x["id"] not in locales]
    web = {}
    if resto:
        pz = fm_web("/api/oficina/youtube-piezas", {"ids": resto}); web = {x["id"]: x for x in ((pz or {}).get("piezas") or [])}
    lista = []
    for x in pedidas:
        if x["id"] in locales: lista.append({"id": x["id"], "titulo": x["titulo"], "local": locales[x["id"]], "ext": os.path.splitext(locales[x["id"]])[1].lstrip(".").lower() or "wav"})
        elif x["id"] in web: lista.append(web[x["id"]])
    if not lista or len(lista) != len(pedidas): raise RuntimeError("No se encontró el audio de todas las canciones (ni en la web ni en tu disco: ¿está conectado el T5 EVO?).")
    tmp = tempfile.mkdtemp(prefix="yt-")  # disco INTERNO: el servicio de launchd puede leer la canción del T5 con Python, pero ffmpeg (otro programa) no puede leer el T5
    try:
        pistas = []
        for i, x in enumerate(lista, 1):
            d = os.path.join(tmp, f"{i:02d}.{x.get('ext', 'mp3')}")
            if x.get("local"): shutil.copyfile(x["local"], d)
            else:
                with urllib.request.urlopen(x["url"], timeout=300) as r, open(d, "wb") as f: shutil.copyfileobj(r, f)
            pistas.append((x["titulo"], d))
        titulo = (peticion.get("titulo") or pistas[0][0])[:100]
        if len(pistas) == 1:
            audio = pistas[0][1]; desc = peticion.get("descripcion") or "Pieza creada con Island Crew · Cabra Beats. Contenido generado con IA (música sintética)."
        else:
            lis = os.path.join(tmp, "lista.txt"); capitulos = []; t = 0.0
            with open(lis, "w") as f:
                for i_p, (n, d) in enumerate(pistas, 1): f.write("file '" + d.replace("'", "'\\''") + "'\n"); capitulos.append(f"{_marca(t)} {i_p:02d} · {n}"); t += _dur(d)
            audio = os.path.join(tmp, "disco.m4a")
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lis, "-c:a", "aac", "-b:a", "192k", audio], check=True)
            desc = titulo + " · Disco de Island Crew\n\n" + "\n".join(capitulos) + "\n\n" + (peticion.get("descripcion") or "Contenido generado con IA (música sintética). Creado con Island Crew · Cabra Beats.")
        if peticion.get("modo") == "lirico":
            import importlib.util; sp2 = importlib.util.spec_from_file_location("vl", os.path.join(os.path.dirname(os.path.abspath(__file__)), "video-lirico.py")); vl = importlib.util.module_from_spec(sp2); sp2.loader.exec_module(vl)
            base = (pistas[0][0] or "").strip(); sal = os.environ.get("MUSICA_DIR", "/Volumes/T5 EVO/IslandCrewAI/musica")
            try: letras = json.load(open(os.path.join(sal, "letras.json"), encoding="utf8"))
            except Exception: letras = {}
            letra = letras.get(base) or ""
            try: audio = vl.crear(audio, letra, base, imagen_para({"titulo": base, "estilo": (lista[0].get("estilo") or ""), "etiquetas": (lista[0].get("etiquetas") or []), "imagen": peticion.get("imagen") or {}}), os.path.join(tmp, "lirico.mp4"), VF_CREDITO)
            except SystemExit as x:
                # Un «vídeo lírico» sin letra sería engañoso: no se sube nada falso; el trabajo falla con el motivo exacto.
                sys.exit("No se creó el vídeo lírico de «" + base + "»: " + str(x))
        if peticion.get("modo") == "cine":
            import importlib.util; sp3 = importlib.util.spec_from_file_location("vc", os.path.join(os.path.dirname(os.path.abspath(__file__)), "video-cine.py")); vc = importlib.util.module_from_spec(sp3); sp3.loader.exec_module(vc)
            base = (pistas[0][0] or "").strip(); sal = os.environ.get("MUSICA_DIR", "/Volumes/T5 EVO/IslandCrewAI/musica")
            try: letras = json.load(open(os.path.join(sal, "letras.json"), encoding="utf8"))
            except Exception: letras = {}
            try: audio = vc.crear(audio, letras.get(base) or "", base, (lista[0].get("estilo") or ""), os.path.join(tmp, "cine.mp4"), VF_CREDITO, tmp)
            except SystemExit as x: print("No se pudo hacer el vídeo cine de «" + base + "»; se sube con la imagen adaptada.", str(x)[:120], flush=True)
        meta_pieza = {"titulo": pistas[0][0], "estilo": (lista[0].get("estilo") or ""), "etiquetas": (lista[0].get("etiquetas") or []), "imagen": peticion.get("imagen") or {}}
        v = a_video(audio, meta_pieza)
        if peticion.get("modo") == "short":
            sh = hacer_short(audio, meta_pieza, pistas[0][0], os.path.join(tmp, "short.mp4"), tmp)
            if sh: v = sh; titulo = (titulo if "#shorts" in titulo.lower() else (titulo[:90] + " #Shorts")); desc = (desc + "\n\n#Shorts #IslandCrew")[:4900]
            else: sys.exit("No se pudo montar el Short (¿falta ffmpeg o la fuente del sistema?).")
        if peticion.get("con_marca") is not False:  # marca Island Crew (entradilla + cierre con firma sonora) en TODO vídeo; si falla, se sube el original
            try:
                import importlib.util; sm = importlib.util.spec_from_file_location("vm", os.path.join(os.path.dirname(os.path.abspath(__file__)), "video-marca.py")); vm = importlib.util.module_from_spec(sm); sm.loader.exec_module(vm)
                v = vm.con_marca(v, os.path.join(tmp, "marca.mp4"), pistas[0][0])
            except Exception as ex: print("Marca no aplicada:", str(ex)[:120], flush=True)
        # Ficha de obra de sello discográfico: nº de pieza y de licencia + créditos + contacto. Sin número no se publica (se reintenta; si no hay forma, falla con el motivo).
        ficha = ""
        for intento in range(3):
            try:
                rf = fm_web("/api/oficina/obra-ficha", {"ids": [x["id"] for x in pedidas], "modo": peticion.get("modo") or "cancion", "titulo": titulo})
                ficha = str((rf or {}).get("ficha") or "")
                if ficha: break
            except Exception as ex: print("Ficha de obra: intento", intento + 1, "falló:", str(ex)[:120], flush=True)
            time.sleep(3)
        if not ficha: raise RuntimeError("No se pudo obtener el número de pieza/licencia de la web; no se publica sin ficha de obra (se reintentará).")
        desc = (str(desc)[:3300] + "\n\n" + ficha)
        prog = peticion.get("programar_en") or None
        r = subir(v, titulo, desc, token_valido(False), bool(peticion.get("publico")), prog, no_listado=bool(peticion.get("no_listado")) and not peticion.get("publico"))
        if peticion.get("modo") != "short": poner_miniatura(r["id"], meta_pieza, pistas[0][0] if len(pistas) == 1 else titulo, token_valido(False), tmp)
        real = (r.get("status") or {}).get("privacyStatus", "private"); url = f"https://studio.youtube.com/video/{r['id']}/edit"
        reg = cargar(REGISTRO, {}); reg["pedido-" + r["id"]] = {"archivo": titulo, "id": r["id"], "url": url, "fecha": time.strftime("%Y-%m-%d %H:%M"), "privacidad": real, "web_ids": [x["id"] for x in pedidas if x["id"] in web], "web_liberada": False}; guardar_seguro(REGISTRO, reg)
        registrar_publicacion(titulo, url, "publicada" if real == "public" else "subida_privada", "video")
        registrar_biblioteca({"tipo": "video", "titulo": titulo[:120], "descripcion": ("Disco" if len(pistas) > 1 else "Canción") + " subido a YouTube (" + real + ")", "origen": "enlace", "url": url, "etiquetas": ["youtube", "disco" if len(pistas) > 1 else "cancion", "ytm:" + str(peticion.get("modo") or "cancion")] + (["ytv:" + real] if real != "private" else []) + ["ytp:" + str(q.get("id")) for q in (peticion.get("piezas") or []) if q.get("id")][:12]})
        try:  # subida confirmada: borra de la web el audio ya publicado (nunca producto de clientes; lo decide el servidor)
            ids_web = [x["id"] for x in pedidas if x["id"] in web]
            if ids_web and peticion.get("liberar_web") is not False:
                rl = fm_web("/api/oficina/biblioteca-liberar", {"ids": ids_web, "video": r["id"]}); print("Liberado de la web:", (rl or {}).get("borrados", 0), "audios", flush=True)
                if (rl or {}).get("ok"): reg2 = cargar(REGISTRO, {}); (reg2.get("pedido-" + r["id"]) or {})["web_liberada"] = True; guardar_seguro(REGISTRO, reg2)
        except Exception as ex: print("No se pudo liberar el audio de la web (no es grave):", str(ex)[:120], flush=True)
        if prog: print("Programado en YouTube para:", real_prog or "(YouTube no devolvió la hora: compruébalo en Studio)", flush=True)
        return url
    finally: shutil.rmtree(tmp, ignore_errors=True)
