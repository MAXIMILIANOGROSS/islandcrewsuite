"""Island Crew Marketing Suite · núcleo compartido (Windows, Mac, Linux).
Rutas de datos, claves de IA del cliente, ffmpeg, abrir carpetas y parar procesos.
Sin dependencias externas. Compatible con Python 3.9+."""
import os, sys, json, shutil, subprocess, platform

_SP = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "runtime", "site-packages"))
if os.path.isdir(_SP) and _SP not in sys.path: sys.path.append(_SP)
SISTEMA = {"Darwin": "mac", "Windows": "win"}.get(platform.system(), "linux")
# Si el programa lo arrancó la ventana nativa del Mac, aquí llega el fichero donde entregarle la dirección de su pantalla (no se hereda a procesos hijos).
FIFO = os.environ.pop("IC_FIFO", None)
APPS = {"suite": "Island Crew Suite", "carta": "Carta Viva Island Crew", "publicaciones": "Publicaciones Island Crew", "anuncios": "Anuncios Island Crew", "musica": "Cabra Beats Island Crew"}


def carpeta_datos():
    """Dónde guarda cada usuario sus datos. Se puede forzar con ICREW_DATOS."""
    f = os.environ.get("ICREW_DATOS")
    if f: return f
    if SISTEMA == "mac" and os.path.isdir("/Volumes/T5 EVO/IslandCrewAI"):  # disco del propietario (desarrollo)
        return "/Volumes/T5 EVO/IslandCrewAI"
    if SISTEMA == "win": return os.path.join(os.environ.get("APPDATA") or os.path.expanduser("~"), "IslandCrewSuite")
    if SISTEMA == "mac": return os.path.expanduser("~/Library/Application Support/IslandCrewSuite")
    return os.path.expanduser("~/.local/share/IslandCrewSuite")


def carpeta_config():
    """Claves y ajustes pequeños (siempre en el perfil del usuario, nunca en el pendrive)."""
    if SISTEMA == "win": b = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif SISTEMA == "mac": b = os.path.expanduser("~/Library/Application Support")
    else: b = os.path.expanduser("~/.config")
    d = os.path.join(b, "IslandCrewSuite"); os.makedirs(d, exist_ok=True); return d


def ruta_info(nombre):
    return os.path.join(carpeta_config(), nombre)


def carpeta_descargas():
    d = os.path.join(os.path.expanduser("~"), "Downloads")
    return d if os.path.isdir(d) else os.path.expanduser("~")


def _leer_env(path):
    out = {}
    try:
        for l in open(path, encoding="utf8"):
            l = l.strip()
            if l and not l.startswith("#") and "=" in l:
                k, v = l.split("=", 1); out[k.strip()] = v.strip().strip('"\'')
    except Exception: pass
    return out


def clave(nombre, raiz_dev=None):
    """Orden: variable de entorno > claves.json del usuario > .env.local (solo desarrollo)."""
    v = os.environ.get(nombre)
    if v: return v
    try:
        v = json.load(open(os.path.join(carpeta_config(), "claves.json"), encoding="utf8")).get(nombre)
        if v: return v
    except Exception: pass
    if raiz_dev: return _leer_env(os.path.join(raiz_dev, ".env.local")).get(nombre)
    return None


def guardar_clave(nombre, valor):
    p = os.path.join(carpeta_config(), "claves.json")
    try: d = json.load(open(p, encoding="utf8"))
    except Exception: d = {}
    if valor: d[nombre] = valor.strip()
    else: d.pop(nombre, None)
    json.dump(d, open(p, "w", encoding="utf8"))
    try: os.chmod(p, 0o600)
    except Exception: pass


def claves_estado():
    """Qué claves hay puestas, sin revelarlas."""
    return {k: bool(clave(k)) for k in ("GEMINI_API_KEY", "GROQ_API_KEY")}


def ffmpeg():
    """ffmpeg propio de la suite (carpeta bin junto a la app) > el del sistema."""
    exe = "ffmpeg.exe" if SISTEMA == "win" else "ffmpeg"
    aqui = os.path.dirname(os.path.abspath(__file__))
    for d in (os.path.join(aqui, "..", "..", "bin"), os.path.join(aqui, "..", "bin"), os.path.join(aqui, "bin"), os.path.join(os.path.dirname(sys.executable), "bin")):
        p = os.path.abspath(os.path.join(d, exe))
        if os.path.isfile(p): return p
    w = shutil.which("ffmpeg")
    if w: return w
    for p in ("/opt/homebrew/bin/ffmpeg", "/usr/local/bin/ffmpeg"):
        if os.path.isfile(p): return p
    return "ffmpeg"


def abrir(ruta):
    """Abre una carpeta o archivo con el programa del sistema."""
    try:
        if SISTEMA == "win": os.startfile(ruta)  # type: ignore[attr-defined]
        elif SISTEMA == "mac": subprocess.Popen(["open", ruta])
        else: subprocess.Popen(["xdg-open", ruta])
    except Exception: pass


def proceso_vivo(pid):
    try:
        if SISTEMA == "win":
            r = subprocess.run(["tasklist", "/FI", "PID eq %d" % int(pid)], capture_output=True, text=True)
            return str(int(pid)) in r.stdout
        os.kill(int(pid), 0); return True
    except Exception: return False


def parar_proceso(pid):
    try:
        if SISTEMA == "win": subprocess.run(["taskkill", "/PID", str(int(pid)), "/F"], capture_output=True)
        else: os.kill(int(pid), 15)
        return True
    except Exception: return False


def nativo():
    """Ventana nativa del Mac (WebKit): sin Chrome ni barra de direcciones."""
    aqui = os.path.dirname(os.path.abspath(__file__))
    for x in (os.path.join(aqui, "..", "..", "bin", "ventana-mac"), os.path.join(aqui, "ventana", "ventana-mac")):
        if os.path.isfile(x) and os.access(x, os.X_OK): return os.path.abspath(x)
    return None


def abrir_app(f):
    """En Mac abre el programa como aplicación propia (su icono, su ventana) si está instalada."""
    if SISTEMA != "mac" or f not in APPS: return False
    p = os.path.expanduser("~/Applications/%s.app" % APPS[f])
    if os.path.isdir(p):
        subprocess.Popen(["open", p]); return True
    return False


def ventana(url, titulo="Island Crew", icono=""):
    """Muestra la pantalla del programa en su propia ventana: nativa en Mac; Edge/Chrome en modo aplicación en Windows; si no hay, el navegador."""
    if FIFO:
        try:
            open(FIFO + ".t", "w").write(url); os.replace(FIFO + ".t", FIFO); return True
        except Exception: pass
    if SISTEMA == "mac":
        b = nativo()
        if b:
            try: subprocess.Popen([b, "--url", url, titulo, icono], start_new_session=True); return True
            except Exception: pass
    cand = []
    if SISTEMA == "win":
        for v in ("PROGRAMFILES(X86)", "PROGRAMFILES", "LOCALAPPDATA"):
            b = os.environ.get(v)
            if b:
                cand += [os.path.join(b, "Microsoft", "Edge", "Application", "msedge.exe"), os.path.join(b, "Google", "Chrome", "Application", "chrome.exe")]
    elif SISTEMA == "mac":
        cand = ["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge", "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"]
    else:
        cand = [shutil.which(x) or "" for x in ("google-chrome", "chromium", "microsoft-edge")]
    perfil = os.path.join(carpeta_config(), "ventana")
    for c in cand:
        if c and os.path.isfile(c):
            try:
                subprocess.Popen([c, "--app=" + url, "--user-data-dir=" + perfil, "--no-first-run", "--window-size=1280,860"]); return True
            except Exception: pass
    import webbrowser; webbrowser.open(url); return False
