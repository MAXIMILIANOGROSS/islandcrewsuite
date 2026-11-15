#!/usr/bin/env python3
"""Island Crew Marketing Suite · lanzador. Un icono: asistente la primera vez, después abre la fábrica.
Uso:  suite.py --abrir carta|publicaciones|anuncios|musica   abre ese programa por su cuenta
      suite.py            abre la suite (asistente si es la primera vez)
      suite.py --asistente repite el asistente
      suite.py --parar     para las fábricas en marcha"""
import os, sys, json, time, platform, shutil, subprocess, threading, socket, urllib.request, urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import core, lic
import marca
RAIZ = os.path.abspath(os.path.join(AQUI, "..", ".."))
CFG = os.path.join(core.carpeta_config(), "config.json")
CV = os.path.join(AQUI, "..", "carta-viva", "carta-viva-app.py")
INFO_CV = os.path.expanduser("~/IslandCrewAI/carta-viva-app.json")
PB = os.path.join(AQUI, "..", "publicaciones", "publicaciones-app.py")
AN = os.path.join(AQUI, "..", "anuncios", "anuncios-app.py")
INFO_PB = os.path.expanduser("~/IslandCrewAI/publicaciones-app.json")
INFO_AN = os.path.expanduser("~/IslandCrewAI/anuncios-app.json")
INFO_MU = os.path.expanduser("~/IslandCrewAI/cabra-beats-app.json")
HUB = os.path.join(core.carpeta_config(), "hub.json")
NOMBRES = {"mac": "macOS", "win": "Windows", "linux": "Linux"}
FIN = threading.Event()


def cargar():
    try: return json.load(open(CFG, encoding="utf8"))
    except Exception: return {}


def hw():
    s, m = core.SISTEMA, platform.machine().lower()
    if s == "mac": return "Apple Silicon: este Mac puede crear música." if m in ("arm64", "aarch64") else "Mac con Intel: la música local no está disponible; las demás fábricas sí."
    if s == "win":
        if shutil.which("nvidia-smi"): return "Tarjeta NVIDIA detectada: este equipo puede crear música."
        return "No se detecta tarjeta NVIDIA: la música local no está disponible; las demás fábricas sí."
    return "Sistema no oficial."


def probar(url, cab):
    rq = urllib.request.Request(url, headers=dict({"User-Agent": "IslandCrewSuite/1.0"}, **cab))
    try: urllib.request.urlopen(rq, timeout=12); return True, "Clave correcta."
    except urllib.error.HTTPError as e: return False, "No la acepta (código %d). Revisa que esté copiada entera." % e.code
    except Exception: return False, "No se pudo comprobar (¿hay internet?)."


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _j(self, o, c=200):
        b = json.dumps(o, ensure_ascii=False).encode("utf8"); self.send_response(c); self.send_header("content-type", "application/json"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path.startswith("/api/estado"):
            c = cargar(); return self._j({"sistema": core.SISTEMA, "sistema_nombre": NOMBRES.get(core.SISTEMA, "?") + " " + platform.machine(), "datos_defecto": c.get("datos") or core.carpeta_datos(), "musica": hw(), "musica_ok": bool(musica_lanzador()), "config": {"negocio": c.get("negocio", ""), "ciudad": c.get("ciudad", "")}})
        b = marca.html(open(os.path.join(AQUI, "asistente.html"), encoding="utf8").read()).encode("utf8"); self.send_response(200); self.send_header("content-type", "text/html; charset=utf-8"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        try: d = json.loads(self.rfile.read(int(self.headers.get("content-length") or 0)) or "{}")
        except Exception: return self._j({"ok": False, "mensaje": "Datos no válidos."}, 400)
        if self.path == "/api/licencia":
            ok, j = lic.comprobar(d.get("licencia", ""))
            if ok and not j.get("fabricas"): ok, j = False, "Esta licencia no incluye ninguna fábrica."
            return self._j({"ok": ok, "mensaje": "" if ok else j})
        if self.path == "/api/claves":
            r = []
            if d.get("gemini"): r.append(dict(zip(("ok", "mensaje"), probar("https://generativelanguage.googleapis.com/v1beta/models?key=" + d["gemini"], {})))); r[-1]["mensaje"] = "Gemini: " + r[-1]["mensaje"]
            if d.get("groq"): r.append(dict(zip(("ok", "mensaje"), probar("https://api.groq.com/openai/v1/models", {"Authorization": "Bearer " + d["groq"]})))); r[-1]["mensaje"] = "Groq: " + r[-1]["mensaje"]
            return self._j(r or [{"ok": False, "mensaje": "Pega al menos una clave."}])
        if self.path == "/api/guardar":
            ok, j = lic.comprobar(d.get("licencia", ""))
            if not ok or not j.get("fabricas"): return self._j({"ok": False, "mensaje": "Licencia no válida. Vuelve al paso 3."})
            if not d.get("acepta"): return self._j({"ok": False, "mensaje": "Falta aceptar las condiciones."})
            try: os.makedirs(d["datos"], exist_ok=True)
            except Exception: return self._j({"ok": False, "mensaje": "No se puede usar esa carpeta de datos. Elige otra en el paso 2."})
            for k, n in (("gemini", "GEMINI_API_KEY"), ("groq", "GROQ_API_KEY")):
                if d.get(k): core.guardar_clave(n, d[k])
            json.dump({"datos": d["datos"], "licencia": d["licencia"], "negocio": d.get("negocio", ""), "ciudad": d.get("ciudad", ""), "idioma": d.get("idioma", "es"), "publicacion": d.get("publicacion", "cloudflare"), "instalado": time.strftime("%Y-%m-%d")}, open(CFG, "w", encoding="utf8"), ensure_ascii=False)
            self._j({"ok": True}); threading.Timer(1.5, FIN.set).start(); return
        self._j({"error": "no"}, 404)


def puerto():
    s = socket.socket(); s.bind(("127.0.0.1", 0)); p = s.getsockname()[1]; s.close(); return p


def asistente():
    FIN.clear(); pt = puerto(); srv = ThreadingHTTPServer(("127.0.0.1", pt), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
    core.ventana("http://127.0.0.1:%d/" % pt); FIN.wait(); srv.shutdown()


def musica_lanzador():
    """Cabra Beats se activa solo si este equipo ya tiene su motor instalado (lanzador propio)."""
    c = cargar()
    for x in (c.get("musica_lanzador"), os.path.join(RAIZ, "musica", "cabra-beats-lanzar.sh"), os.path.expanduser("~/Downloads/island-crew-web/scripts/cabra-beats-lanzar.sh")):
        if x and os.path.isfile(x): return x
    return None


def evolucion():
    """Resumen de lo que ha hecho cada programa (lee sus propias carpetas; no depende de que estén abiertos)."""
    import glob
    d = core.carpeta_datos(); base = os.path.join(d, "cartas"); r = {}
    platos = vids = nr = 0; tot = lis = pub = 0
    for c in glob.glob(os.path.join(base, "*", "carta.json")):
        nr += 1; rd_ = os.path.dirname(c)
        try: platos += len(json.load(open(c, encoding="utf8")).get("platos", []))
        except Exception: pass
        vids += len([f for f in glob.glob(os.path.join(rd_, "videos", "*.mp4")) if not os.path.basename(f).startswith("_")])
        try:
            ps = json.load(open(os.path.join(rd_, "publicaciones.json"), encoding="utf8")).get("posts", [])
            tot += len(ps); lis += len([p for p in ps if p.get("estado") == "listo"]); pub += len([p for p in ps if p.get("estado") == "publicado"])
        except Exception: pass
    r["carta"] = [["Restaurantes", nr], ["Platos", platos], ["Vídeos creados", vids]]
    r["publicaciones"] = [["Publicaciones planificadas", tot], ["Listas", lis], ["Publicadas", pub]]
    try: an = len(json.load(open(os.path.join(core.carpeta_config(), "anuncios-historial.json"), encoding="utf8")))
    except Exception: an = 0
    r["anuncios"] = [["Anuncios creados", an]]
    canc = len(glob.glob(os.path.join(d, "musica", "**", "*.mp3"), recursive=True))
    r["musica"] = [["Canciones y jingles", canc]]
    return r


_EV = {"t": 0, "v": None}


def ultimas():
    """Cuándo hizo algo cada programa por última vez (fecha de sus propios ficheros)."""
    import glob
    d = core.carpeta_datos(); u = {}
    def mx(fs):
        t = 0
        for f in fs:
            try: t = max(t, os.path.getmtime(f))
            except Exception: pass
        return int(t)
    u["carta"] = max(mx(glob.glob(os.path.join(d, "cartas", "*", "carta.json"))), mx(glob.glob(os.path.join(d, "cartas", "*", "videos", "*.mp4"))))
    u["publicaciones"] = mx(glob.glob(os.path.join(d, "cartas", "*", "publicaciones.json")))
    u["anuncios"] = mx([os.path.join(core.carpeta_config(), "anuncios-historial.json")])
    u["musica"] = mx(glob.glob(os.path.join(d, "musica", "**", "*.mp3"), recursive=True))
    return u


def actividad():
    """Monitor de los 4 programas: contadores, última actividad y si están en marcha ahora."""
    if time.time() - _EV["t"] > 8: _EV.update(t=time.time(), v=(evolucion(), ultimas()))
    ev, ult = _EV["v"]
    act = {k: bool(en_marcha(i)) for k, i in (("carta", INFO_CV), ("publicaciones", INFO_PB), ("anuncios", INFO_AN), ("musica", INFO_MU))}
    return ev, ult, act


def abrir_fabrica(f, c):
    """Abre un programa por su cuenta (sin pasar por el inicio)."""
    ok, j = lic.comprobar(c.get("licencia", ""))
    if not ok or f not in j.get("fabricas", []): return False, "Tu licencia no incluye este programa."
    if f == "musica":
        ml = musica_lanzador()
        if not ml: return False, "Este equipo no tiene instalado el motor de música."
        subprocess.Popen(["bash", ml], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); return True, ""
    tabla = {"carta": (CV, INFO_CV), "publicaciones": (PB, INFO_PB), "anuncios": (AN, INFO_AN)}
    pt = lanzar(tabla[f][0], tabla[f][1], c)
    if not pt: return False, "No se pudo arrancar."
    core.ventana("http://127.0.0.1:%d/" % pt); return True, ""


def en_marcha(info):
    try:
        i = json.load(open(info))
        if core.proceso_vivo(i["pid"]): urllib.request.urlopen("http://127.0.0.1:%d/" % i["port"], timeout=2); return i["port"]
    except Exception: pass
    return None


def carta_en_marcha(): return en_marcha(INFO_CV)


def lanzar(script, info, c):
    pt = en_marcha(info)
    if pt: return pt
    env = dict(os.environ); env["ICREW_DATOS"] = c.get("datos") or core.carpeta_datos()
    log = open(os.path.join(core.carpeta_config(), os.path.basename(script) + ".log"), "ab")
    kw = {"creationflags": 0x08000000} if core.SISTEMA == "win" else {"start_new_session": True}
    subprocess.Popen([sys.executable, script], env=env, stdout=log, stderr=log, cwd=os.path.dirname(script), **kw)
    for _ in range(80):
        time.sleep(0.25); pt = en_marcha(info)
        if pt: return pt
    return None


def lanzar_carta(c): return lanzar(CV, INFO_CV, c)


def centro_post(d):
    import centro
    a = d.get("a")
    if a == "alerta": centro.alerta_marcar(str(d.get("id")), d.get("estado", "nueva")); return {"ok": True}
    if a == "fin_add":
        l = centro.finanzas_leer()
        try: imp = float(d.get("importe"))
        except Exception: return {"ok": False}
        l.append({"fecha": str(d.get("fecha"))[:10], "tipo": "ingreso" if d.get("tipo") == "ingreso" else "gasto", "unidad": d.get("unidad"), "categoria": str(d.get("categoria") or "")[:40], "importe": imp, "moneda": str(d.get("moneda") or "EUR")[:4]})
        centro.finanzas_guardar(l); return {"ok": True}
    if a == "fin_borrar":
        l = centro.finanzas_leer()
        try: l.pop(int(d.get("i")))
        except Exception: pass
        centro.finanzas_guardar(l); return {"ok": True}
    if a == "objetivos": centro.objetivos(d); return {"ok": True}
    if a == "resumen":
        try:
            c = centro.calcular("30d", activos={}); r = centro.resumen_ia(c, centro.analista(c))
            return {"ok": bool(r), "texto": r, "mensaje": "" if r else centro.t("No se pudo generar el resumen (falta la clave gratuita de IA).")}
        except Exception as e: return {"ok": False, "mensaje": str(e)}
    if a == "informe":
        try: r = centro.informe(d.get("k", "mensual"), d.get("p", "30d"), d.get("d1"), d.get("d2"), actividad()[2]); return {"ok": True, "mensaje": centro.t("Informe creado en Descargas:") + " " + os.path.basename(r)}
        except Exception as e: return {"ok": False, "mensaje": str(e)}
    return {"ok": False}


class Hub(H):
    def do_GET(self):
        if self.path.startswith("/api/estado"):
            c = cargar(); ok, j = lic.comprobar(c.get("licencia", ""))
            return self._j({"negocio": c.get("negocio", ""), "fabricas": j.get("fabricas", []) if ok else [], "musica": hw(), "musica_ok": bool(musica_lanzador()), "sistema": core.SISTEMA, "evolucion": actividad()[0], "ultima": actividad()[1], "activos": actividad()[2], "ahora": int(time.time())})
        if self.path.startswith("/api/centro"):
            import centro, urllib.parse
            q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            g = lambda k, d=None: (q.get(k) or [d])[0]
            try: return self._j(centro.api(g("p", "30d"), g("d1"), g("d2"), actividad()[2]))
            except Exception as e: return self._j({"error": str(e)})
        if self.path.startswith("/centro"):
            b = marca.html(open(os.path.join(AQUI, "centro.html"), encoding="utf8").read()).encode("utf8"); self.send_response(200); self.send_header("content-type", "text/html; charset=utf-8"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        b = open(os.path.join(AQUI, "inicio.html"), encoding="utf8").read(); b = marca.html(b).encode("utf8"); self.send_response(200); self.send_header("content-type", "text/html; charset=utf-8"); self.send_header("content-length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        d = json.loads(self.rfile.read(int(self.headers.get("content-length") or 0)) or "{}"); c = cargar(); ok, j = lic.comprobar(c.get("licencia", ""))
        if d.get("a"): return self._j(centro_post(d))
        f = d.get("f")
        if f == "musica":
            ml = musica_lanzador()
            if not ok or "musica" not in j.get("fabricas", []): return self._j({"ok": False, "mensaje": "Tu licencia no incluye la música."})
            if not ml: return self._j({"ok": False, "mensaje": "Este equipo no tiene instalado el motor de música."})
            subprocess.Popen(["bash", ml], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL); return self._j({"ok": True})
        tabla = {"carta": (CV, INFO_CV), "publicaciones": (PB, INFO_PB), "anuncios": (AN, INFO_AN)}
        if not ok or f not in tabla or f not in j.get("fabricas", []): return self._j({"ok": False, "mensaje": "Tu licencia no incluye esta fábrica."})
        if core.abrir_app(f): return self._j({"ok": True})
        pt = lanzar(tabla[f][0], tabla[f][1], c)
        if not pt: return self._j({"ok": False, "mensaje": "No se pudo arrancar. Mira la carpeta de registros."})
        core.ventana("http://127.0.0.1:%d/" % pt); return self._j({"ok": True})


def servir_hub():
    pt = puerto(); srv = ThreadingHTTPServer(("127.0.0.1", pt), Hub); json.dump({"pid": os.getpid(), "port": pt}, open(HUB, "w")); srv.serve_forever()


def abrir_hub():
    pt = en_marcha(HUB)
    if not pt:
        kw = {"creationflags": 0x08000000} if core.SISTEMA == "win" else {"start_new_session": True}
        log = open(os.path.join(core.carpeta_config(), "inicio.log"), "ab")
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "--hub"], stdout=log, stderr=log, **kw)
        for _ in range(60):
            time.sleep(0.25); pt = en_marcha(HUB)
            if pt: break
    if pt: core.ventana("http://127.0.0.1:%d/" % pt)
    else: print("No se pudo abrir el inicio. Mira", os.path.join(core.carpeta_config(), "inicio.log"))


def main():
    if "--hub" in sys.argv: servir_hub(); return
    if "--parar" in sys.argv:
        for x in (CV, PB, AN): subprocess.run([sys.executable, x, "--parar"])
        try: core.parar_proceso(json.load(open(HUB))["pid"])
        except Exception: pass
        return
    c = cargar()
    if "--abrir" in sys.argv:
        f = sys.argv[sys.argv.index("--abrir") + 1]
        if not c.get("licencia"):
            asistente(); c = cargar()
            if not c.get("licencia"): return
        ok, m = abrir_fabrica(f, c)
        if not ok: print(m); abrir_hub()
        return
    if "--asistente" in sys.argv or not c.get("licencia"):
        asistente(); c = cargar()
        if not c.get("licencia"): return
    else:
        ok, j = lic.comprobar(c["licencia"])
        if not ok:
            c["licencia"] = ""; json.dump(c, open(CFG, "w", encoding="utf8")); asistente(); c = cargar()
            if not c.get("licencia"): return
    abrir_hub()


if __name__ == "__main__": main()
