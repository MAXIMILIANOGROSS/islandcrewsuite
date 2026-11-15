"""Conexiones con redes sociales y YouTube. Las claves se guardan SOLO en la carpeta de configuración del usuario (claves.json, permisos 600): nunca dentro del paquete."""
import os, json, urllib.request, urllib.parse
import core

REDES = {
    "meta": {"campos": ["META_FB_PAGE_ID", "META_FB_PAGE_TOKEN", "META_IG_USER_ID"], "color": "#4aa8ff"},
}
YT_DIR = os.path.expanduser(os.environ.get("YT_DIR", "~/IslandCrewAI/youtube"))
_YT = {}


def _yt():
    """El mismo motor de subida que usa Cabra Beats (youtube-subir.py): mismos permisos, mismo registro, mismo tope diario."""
    if "m" not in _YT:
        import importlib.util
        aqui = os.path.dirname(os.path.abspath(__file__))
        for p in (os.path.join(aqui, "youtube-subir.py"), os.path.join(aqui, "..", "youtube-subir.py")):
            if os.path.isfile(p):
                os.environ.setdefault("YT_DIR", YT_DIR)
                sp = importlib.util.spec_from_file_location("yt", p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); _YT["m"] = m; break
        else: _YT["m"] = None
    return _YT["m"]


def yt_estado():
    sec = os.path.isfile(os.path.join(YT_DIR, "client_secret.json")); tok = os.path.isfile(os.path.join(YT_DIR, "token.json")); m = _yt(); permiso = "sin_autorizar"
    if sec and tok and m:
        try: permiso = m.estado_permiso()
        except BaseException: permiso = "caducado"
    return {"ok": permiso == "ok", "campos": {"client_secret.json": sec, "token": tok}, "permiso": permiso, "motor": bool(m)}


def yt_guardar_secreto(txt):
    try: d = json.loads(txt)
    except Exception: return False, "Eso no es un archivo JSON válido."
    c = d.get("installed") or d.get("web") or {}
    if not c.get("client_id") or not c.get("client_secret"): return False, "Ese archivo no es de tipo «Aplicación de escritorio». Descarga el JSON del cliente OAuth."
    os.makedirs(YT_DIR, exist_ok=True); p = os.path.join(YT_DIR, "client_secret.json"); open(p, "w", encoding="utf8").write(json.dumps(d))
    try: os.chmod(p, 0o600)
    except Exception: pass
    return True, "Archivo guardado. Ahora pulsa «Conectar YouTube»."


def yt_conectar():
    import threading
    m = _yt()
    if not m: return False, "Falta el motor de subida en esta instalación."
    if not os.path.isfile(os.path.join(YT_DIR, "client_secret.json")): return False, "Primero pega el archivo del paso 3."
    def con():
        try: m.token_valido(True, True)
        except BaseException: pass
    threading.Thread(target=con, daemon=True).start(); return True, "Se abre el navegador: elige tu canal y acepta el permiso."



def estado():
    r = {k: {"ok": all(bool(core.clave(c)) for c in v["campos"]), "campos": {c: bool(core.clave(c)) for c in v["campos"]}} for k, v in REDES.items()}
    r["youtube"] = yt_estado(); return r


def _get(u):
    try:
        r = urllib.request.urlopen(urllib.request.Request(u, headers={"User-Agent": "IslandCrew"}), timeout=15)
        return json.loads(r.read().decode("utf8"))
    except urllib.error.HTTPError as e:
        try: return json.loads(e.read().decode("utf8"))
        except Exception: return {"error": {"message": "HTTP %d" % e.code}}
    except Exception as e: return {"error": {"message": str(e)[:120]}}


def probar(red):
    if red == "meta":
        tk, pg, ig = core.clave("META_FB_PAGE_TOKEN"), core.clave("META_FB_PAGE_ID"), core.clave("META_IG_USER_ID")
        if not (tk and pg and ig): return False, "Faltan datos."
        a = _get("https://graph.facebook.com/v19.0/%s?fields=name&access_token=%s" % (urllib.parse.quote(pg), urllib.parse.quote(tk)))
        b = _get("https://graph.facebook.com/v19.0/%s?fields=username&access_token=%s" % (urllib.parse.quote(ig), urllib.parse.quote(tk)))
        if "error" in a: return False, "Facebook: " + a["error"].get("message", "error")
        if "error" in b: return False, "Instagram: " + b["error"].get("message", "error")
        return True, "Facebook: %s · Instagram: @%s" % (a.get("name", "?"), b.get("username", "?"))
    if red == "youtube":
        e = yt_estado()
        return e["ok"], {"ok": "YouTube conectado: la suite puede subir vídeos a tu canal.", "caducado": "El permiso caducó: pulsa «Conectar YouTube».", "sin_autorizar": "Todavía no está autorizado."}.get(e["permiso"], "")
    return False, ""


def guardar(red, d):
    if red not in REDES: return
    for c in REDES[red]["campos"]:
        if d.get(c): core.guardar_clave(c, d[c])


def borrar(red):
    if red == "youtube":
        try: os.remove(os.path.join(YT_DIR, "token.json"))
        except Exception: pass
    for c in REDES.get(red, {}).get("campos", []): core.guardar_clave(c, "")


def importar_dev():
    """Solo para quien desarrolla la web: copia las claves del .env.local de islandcrew.es a su configuración local."""
    raiz = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    env = core._leer_env(os.path.join(raiz, ".env.local")); n = 0
    for c in ("META_FB_PAGE_ID", "META_FB_PAGE_TOKEN", "META_IG_USER_ID"):
        if env.get(c): core.guardar_clave(c, env[c]); n += 1
    return n


def hay_dev():
    raiz = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    return os.path.isfile(os.path.join(raiz, ".env.local"))
