#!/usr/bin/env python3
"""CABRA BEATS PERSONAL · programa propio para crear música en tu Mac, sin la web, sin Vercel y sin abrir direcciones.
Motor de música (ACE-Step) + letras con IA local (Ollama) + biblioteca + subida a YouTube desde el Mac. Se abre en su propia ventana.
Uso: python3 scripts/cabra-beats-app.py   ·   Parar: python3 scripts/cabra-beats-app.py --parar"""
import tempfile, datetime, glob, hashlib, os, sys, json, time, threading, random, re, shutil, subprocess, importlib.util, secrets, socket
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import urllib.request as ur

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.normpath(os.path.join(AQUI, ".."))
INFO = os.path.expanduser("~/IslandCrewAI/cabra-beats-app.json"); TOKEN = secrets.token_hex(16)
def _cargar(nombre, fichero):
    spec = importlib.util.spec_from_file_location(nombre, os.path.join(AQUI, fichero)); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m
cl = _cargar("cl", "cancion-local.py")     # modo local: quita las claves de la web del entorno
fm = _cargar("fm", "fabrica-musica.py")    # motor de música (ACE-Step)
pt = _cargar("pt", "portada-local.py"); vc = _cargar("vc", "video-clip.py")
RVC = os.environ.get("RVC_DIR") or "/Volumes/T5 EVO/IslandCrewAI/herramientas/RVC-WebUI-MacOS"
VOZ_PY = os.path.join(RVC, ".venv", "bin", "python"); VOZ_SCRIPT = os.path.join(AQUI, "voz-clonada.py")
def voz_estado():
    if not os.path.isfile(VOZ_PY): return {"rvc": False, "modelos_ok": False, "voces": [], "demucs": False, "msg": "La herramienta de voz no está instalada en el disco T5 EVO."}
    try:
        r = subprocess.run([VOZ_PY, VOZ_SCRIPT, "estado"], capture_output=True, text=True, timeout=60, env={**os.environ, "RVC_DIR": RVC}); return json.loads(r.stdout.strip().splitlines()[-1])
    except Exception as e: return {"rvc": False, "modelos_ok": False, "voces": [], "demucs": False, "msg": "No pude consultar la herramienta de voz: " + str(e)[:150]}
def nombre_voz(x): return re.sub(r"[^A-Za-z0-9_-]", "", str(x or "mivoz"))[:30] or "mivoz"
def trabajo_voz(j, p):
    try:
        orden = p.get("orden"); cmd = None; salida_final = None
        if not os.path.isfile(VOZ_PY): raise RuntimeError("La herramienta de voz no está instalada en el disco T5 EVO (carpeta herramientas/RVC-WebUI-MacOS).")
        if orden == "modelos": cmd = [VOZ_PY, VOZ_SCRIPT, "modelos"]
        elif orden == "demucs": cmd = [VOZ_PY, "-m", "pip", "install", "demucs", "soundfile"]
        elif orden == "entrenar":
            if not p.get("permiso"): raise RuntimeError("Marca la casilla de permiso: solo se clona tu voz o la de quien te lo haya autorizado.")
            nom = nombre_voz(p.get("nombre")); carp = os.path.join(SALIDA, "voces", nom, "audios")
            if not os.path.isdir(carp) or not os.listdir(carp): raise RuntimeError("Primero sube tus grabaciones (botón «Subir grabaciones»).")
            cmd = [VOZ_PY, VOZ_SCRIPT, "entrenar", "--nombre", nom, "--audios", carp, "--epocas", str(int(p.get("epocas") or 120))]
        elif orden == "mejorar":
            if not p.get("permiso"): raise RuntimeError("Marca la casilla de permiso: solo se mejora tu voz o la de quien te lo haya autorizado.")
            nom = nombre_voz(p.get("nombre")); carp = os.path.join(SALIDA, "voces", nom, "audios")
            if not os.path.isdir(carp) or not os.listdir(carp): raise RuntimeError("Esa voz no tiene grabaciones. Sube más audios con el mismo nombre de voz.")
            cmd = [VOZ_PY, VOZ_SCRIPT, "mejorar", "--nombre", nom, "--audios", carp, "--epocas", str(min(300, max(2, int(p.get("epocas") or 60))))]
        elif orden == "cantar":
            arch = os.path.basename(p.get("archivo") or ""); ent = os.path.join(SALIDA, arch); nom = nombre_voz(p.get("voz"))
            if not os.path.isfile(ent): raise RuntimeError("No encuentro esa canción.")
            salida_final = os.path.join(SALIDA, os.path.splitext(arch)[0] + f"-voz-{nom}.mp3")
            cmd = [VOZ_PY, VOZ_SCRIPT, "cantar", "--voz", nom, "--entrada", ent, "--salida", salida_final, "--tono", str(int(p.get("tono") or 0))]
        else: raise RuntimeError("Orden desconocida.")
        upd(j, fase="voz", pc=3, msg="Empezando…")
        pr = subprocess.Popen(cmd, cwd=RVC, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, env={**os.environ, "RVC_DIR": RVC, "PYTORCH_ENABLE_MPS_FALLBACK": "1", "COPYFILE_DISABLE": "1", "TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD": "1"}); ult = []
        for linea in pr.stdout:
            l = linea.strip(); ult = (ult + [l])[-12:]
            m = re.search(r"PASO (\d)/(\d)", l)
            if m: upd(j, pc=int(8 + 85 * (int(m.group(1)) - 1) / int(m.group(2))), msg=l)
            elif re.search(r"\d+ ?%", l): upd(j, msg=l[-90:])
            elif re.search(r"Epoch|epoch", l): upd(j, msg="Entrenando… " + l[-80:])
            j["log"] = ult
        rc = pr.wait()
        try: subprocess.run([VOZ_PY, VOZ_SCRIPT, "limpiar"], capture_output=True, timeout=120, env={**os.environ, "RVC_DIR": RVC})
        except Exception: pass
        if rc != 0: raise RuntimeError("Falló: " + " | ".join(x for x in ult if x)[-300:])
        if orden == "cantar" and salida_final and os.path.isfile(salida_final):
            d = lib_leer(); base = next((x for x in d if x.get("archivo") == arch), {"titulo": os.path.splitext(arch)[0], "estilo": "", "idioma": ""}); e = {k: v for k, v in base.items() if k not in ("youtube", "portada", "portada_yt", "portada_ok", "portada_v", "numero", "licencia", "pieza", "sha256", "duracion_seg")}
            e.update(archivo=os.path.basename(salida_final), titulo=(base.get("titulo") or "") + f" (voz {nombre_voz(p.get('voz'))})", creada=time.strftime("%Y-%m-%d %H:%M"), youtube=None); completar_registro(e); d.insert(0, e); lib_guardar(d)
        upd(j, fase="listo", pc=100, ok=True, msg={"modelos": "Modelos de voz descargados.", "demucs": "Separador de voz instalado.", "entrenar": "¡Tu voz está creada! Ya puedes cantar con ella.", "cantar": "Listo: canción con tu voz en la biblioteca."}.get(orden, "Listo."))
    except BaseException as ex: upd(j, fase="fallo", ok=False, msg=msg_error(ex))
    finally: ACTIVO["voz"] = None
_YT = {}
def yt():
    if "m" not in _YT: _YT["m"] = _cargar("yt", "youtube-subir.py")
    return _YT["m"]
SALIDA = fm.SALIDA
CAT = _cargar("ec", "estilos-catalogo.py").catalogo()
ESTILOS = cl.ESTILOS; IDIOMAS = cl.IDIOMAS
ANIMOS = ["happy", "melancholic", "romantic", "epic", "dreamy", "dark", "nostalgic", "festive", "chill", "angry"]
INSTR = ["acoustic guitar", "electric guitar", "piano", "strings", "brass", "synth", "808 bass", "drums", "flute", "accordion", "timple", "congas"]
TEMAS = ["el mar de Corralejo al amanecer", "una noche de verano en Fuerteventura", "los amigos de siempre", "el viento que no para", "volver a casa", "las dunas y la luna", "un amor de temporada", "el barrio que no duerme", "empezar de cero", "la guagua de las seis", "el sabor del pescado fresco", "bailar sin pensar en mañana"]
TITULOS = ["Sal en la piel", "Viento de dunas", "Mi isla, mi ritmo", "Luna de Corralejo", "Sin prisa y sin freno", "Guagua de medianoche", "Cabras en la azotea", "Mar de fondo", "Otra vez septiembre", "Calma chicha"]

def lib_ruta(): return os.path.join(SALIDA, "biblioteca-local.json")
def lib_leer():
    try: return json.load(open(lib_ruta(), encoding="utf8"))
    except Exception: return []
def lib_guardar(d):
    os.makedirs(SALIDA, exist_ok=True); tmp = lib_ruta() + ".tmp"; json.dump(d, open(tmp, "w", encoding="utf8"), ensure_ascii=False, indent=1); os.replace(tmp, lib_ruta())
def t5_ok(): return (not SALIDA.startswith("/Volumes/")) or os.path.isdir("/".join(SALIDA.split("/")[:3]))

_NL = threading.Lock()
def siguiente_numero():
    """Serie propia del Mac (letra M) para no chocar con los números de la web: ICO-2026-M00001 / ICL-2026-M00001."""
    with _NL:
        f = os.path.join(SALIDA, "contador-local.json")
        try: n = int(json.load(open(f)).get("n", 0)) + 1
        except Exception: n = 1
        os.makedirs(SALIDA, exist_ok=True); json.dump({"n": n}, open(f, "w")); a = time.strftime("%Y")
        return n, f"ICO-{a}-M{n:05d}", f"ICL-{a}-M{n:05d}"
def duracion_seg(ruta):
    try:
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", ruta], capture_output=True, text=True, timeout=30); return int(float(r.stdout.strip()))
    except Exception: pass
    try:
        import wave
        with wave.open(ruta) as w: return int(w.getnframes() / w.getframerate())
    except Exception: return 0
def mmss(x): return f"{int(x)//60}:{int(x)%60:02d}"
def huella_sha(ruta):
    import hashlib; h = hashlib.sha256()
    with open(ruta, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()
JOBS = {}; JLOCK = threading.Lock(); ACTIVO = {"video": None, "crear": None, "yt": None, "portada": None, "voz": None}
def nuevo_job(tipo):
    jid = secrets.token_hex(4); JOBS[jid] = {"id": jid, "tipo": tipo, "fase": "preparando", "pc": 1, "msg": "Empezando…", "ok": None, "res": None}; return JOBS[jid]
def upd(j, **k): j.update(k)
def msg_error(e):
    if isinstance(e, SystemExit): return str(e.code) if e.code not in (None, 0) else "Se interrumpió el proceso."
    return str(e)[:300] or e.__class__.__name__

_OL = threading.Lock()
def modelo():
    with _OL: return cl.modelo_ollama()
def ollama_gen(prompt, temp=0.9):
    mod = modelo()
    r = json.load(ur.urlopen(ur.Request(cl.OLLAMA + "/api/generate", json.dumps({"model": mod, "prompt": prompt, "stream": False, "options": {"temperature": temp}}).encode(), {"Content-Type": "application/json"}), timeout=600))
    return (r.get("response") or "").strip()
LETRAS_F = os.path.join(SALIDA, "letras-usadas.json")
def lineas_huella(letra):
    out = set()
    for l in str(letra or "").splitlines():
        l = l.strip()
        if not l or l.startswith("["): continue
        n = re.sub(r"[^a-z0-9áéíóúñü ]", "", l.lower()); n = re.sub(r"\s+", " ", n).strip()
        if len(n) >= 12: out.add(hashlib.md5(n.encode()).hexdigest()[:12])
    return out
def letras_previas():
    """Todas las letras ya creadas: biblioteca + registro permanente (sobrevive aunque borres la canción)."""
    res = []
    try: res += [(x.get("titulo", ""), set(x.get("h") or [])) for x in json.load(open(LETRAS_F, encoding="utf8"))]
    except BaseException: pass
    try: res += [(x.get("titulo", ""), lineas_huella(x.get("letra"))) for x in lib_leer() if x.get("letra")]
    except BaseException: pass
    return res
def letra_repetida(letra):
    a = lineas_huella(letra)
    if len(a) < 3: return None
    for t, b in letras_previas():
        if b and len(a & b) / max(1, min(len(a), len(b))) >= 0.3: return t or "otra canción"
    return None
def registrar_letra(titulo, letra):
    h = sorted(lineas_huella(letra))
    if not h: return
    try:
        try: d = json.load(open(LETRAS_F, encoding="utf8"))
        except BaseException: d = []
        d.append({"titulo": titulo, "h": h, "fecha": time.strftime("%Y-%m-%d %H:%M")}); json.dump(d, open(LETRAS_F, "w", encoding="utf8"))
    except BaseException: pass
ANGULOS = ["empieza en mitad de una escena concreta", "cuenta una anécdota con nombre propio y un detalle único", "usa una metáfora inesperada del mar, la montaña o la cocina", "alterna recuerdo y presente", "dirígete a la persona en segunda persona con humor", "usa un objeto cotidiano como símbolo central", "empieza con una pregunta y respóndela en el estribillo", "cuéntala como una carta"]
def letra_unica(titulo, estilo, idioma, tema, dur, upd_=None, ctx=None):
    """Nunca devuelve una letra igual o parecida a una ya creada: reintenta con otro ángulo hasta 6 veces."""
    previas = [t for t, _ in letras_previas() if t][-10:]
    for i in range(6):
        extra = f" Enfoque obligatorio: {random.choice(ANGULOS)}. La letra debe ser completamente nueva y distinta a estas ya existentes: {', '.join(previas)}." if i or previas else ""
        l = ia_letra(titulo, estilo, idioma, (tema or "") + extra, dur, ctx)
        if not letra_repetida(l): return l
        if upd_: upd_(i)
    raise RuntimeError("La IA me ha devuelto letras muy parecidas a otras que ya existen y por seguridad no las uso (YouTube no admite contenido repetido). Pulsa Crear otra vez o cambia el tema.")
TIPOS_NEGOCIO = ["Restaurante", "Bar", "Cafetería", "Coffee shop con CBD", "Bar de copas", "Heladería", "Panadería", "Hotel o apartamentos", "Peluquería o barbería", "Gimnasio", "Taller", "Inmobiliaria", "Tienda", "Clínica o centro de estética", "Evento o festival", "Otro negocio"]
def letra_jingle(p):
    neg = (p.get("negocio") or "").strip(); tipo = p.get("tipo") or "negocio"; zona = (p.get("zona") or "").strip(); ofrece = (p.get("ofrece") or "").strip(); esl = (p.get("eslogan") or "").strip(); cta = (p.get("cta") or "").strip()
    dur = int(p.get("duracion") or 15); idioma = p.get("idioma") or "es"; tono = p.get("tono") or "alegre y cercano"; lineas = {20: "4 a 5", 30: "6 a 8", 45: "10 a 12"}.get(dur, "6 a 8")
    if not neg: raise RuntimeError("Escribe el nombre del negocio.")
    permitido = " ".join([neg, zona, ofrece, esl, cta]).lower(); previas = [t for t, _ in letras_previas() if t][-8:]
    for i in range(5):
        pr = (f"Eres un creador de jingles publicitarios que venden. Escribe la letra de un jingle de {dur} segundos para «{neg}» ({tipo}{', en ' + zona if zona else ''}), en {IDIOMAS.get(idioma, idioma)}. Tono: {tono}.\n"
              f"Lo que ofrece (usa SOLO esto, no inventes nada más): {ofrece or 'no me han dado detalles: habla solo del ambiente y del nombre, sin inventar productos'}.\n"
              + (f"Eslogan a usar: «{esl}».\n" if esl else "Crea además un eslogan corto y memorable.\n")
              + (f"Cierra con esta llamada a la acción: {cta}.\n" if cta else "")
              + f"REGLAS: {lineas} líneas en total. Cada línea de 5 a 7 sílabas, con palabras sencillas y fáciles de pronunciar al cantar (nada de palabras largas ni trabalenguas), rimas en pareados (AABB) y un ritmo de tambor claro. Frase gancho de 3 a 5 palabras que se repite al menos dos veces (puede ser el eslogan). El nombre «{neg}» suena al menos 2 veces. Primera línea con gancho que suene a anuncio de radio. NO inventes precios, ofertas, descuentos, premios, números ni promesas: solo lo que te han dado. Sin nombres de artistas reales ni marcas ajenas. "
              + ("Puedes usar jerga canaria y española natural (mi niño, chacho, guagua…) sin exagerar. " if idioma == "es" else "") + (f"Que no se parezca a estas ya creadas: {', '.join(previas)}. " if previas else "")
              + "Etiquetas: [Verse] y [Chorus]. Devuelve SOLO la letra, sin comentarios.")
        t = ollama_gen(pr, 0.9 + 0.03 * i).strip(); t = re.sub(r"^```\w*\n|```$", "", t).strip()
        if "[" in t: t = t[t.index("["):]
        if "[" not in t: t = "[Chorus]\n" + t
        inventa = [x for x in re.findall(r"\d[\d.,]*|€|\$|%", t) if x.lower() not in permitido]
        if len(t) < 25 or inventa or letra_repetida(t): continue
        return t
    raise RuntimeError("No logré una letra de jingle nueva y sin datos inventados. Pulsa otra vez o añade más detalles de lo que ofrece el negocio.")
def es_borrador(t):
    t = (t or "").strip(); return bool(t) and "[" not in t and len(t.splitlines()) < 8
def ia_titulo_de(idea, estilo, idioma):
    try:
        t = ollama_gen(f"Escribe UN título de canción comercial, corto (máximo 6 palabras), pegadizo y original, en {IDIOMAS.get(idioma, idioma)}, para esta petición: «{idea[:400]}». Estilo {estilo}. Si menciona a una persona, puede incluir su nombre. Responde SOLO con el título, sin comillas.", 0.9)
        t = t.strip().split("\n")[0].strip(" \"«»'*.")
        if 3 <= len(t) <= 60: return t
    except BaseException: pass
    return ""
def norm_idioma(p):
    """«español de Argentina» = español + acento argentino."""
    if isinstance(p, dict) and p.get("idioma") == "es-ar":
        p["idioma"] = "es"; p["acento"] = "Argentine Rioplatense"
    return p


DIALECTOS = {"Argentine Rioplatense": "español rioplatense de Argentina (Buenos Aires): VOSEO verbal completo (vos tenés, querés, sabés, sos, mirá, venite, dale, decime), lunfardo natural y variado (laburo, guita, mina, pibe, chabón, bondi, birra, morfar, mango, gamba, posta, piola, copado, boliche, bardo, fiaca, quilombo, re- como intensificador), «che» solo de vez en cuando; giros y modismos porteños reales; NUNCA «tú», ni «guagua», ni expresiones de España, Canarias ni México", "Spanish from Spain": "español de España (tú, vale, tío, guay, molar)",
             "Canarian Spanish": "español canario (mi niño, chacho, guagua, fistro, ñoño, jerga canaria natural)", "Mexican": "español mexicano (güey, chido, neta, órale, padre; nada de jerga de España)",
             "Colombian": "español colombiano (parce, bacano, chévere, qué más; nada de jerga de España)", "British": "inglés británico (mate, innit, lads)", "American": "inglés americano",
             "Brazilian Portuguese": "português do Brasil", "European Portuguese from Portugal": "português de Portugal", "French": "français", "German": "Deutsch", "Italian": "italiano"}
ACENTO_EN = {"Argentine Rioplatense": "strong Buenos Aires porteño Rioplatense Spanish accent, 'sh' sound for ll and y, aspirated s, Italian-influenced sing-song intonation, clearly NOT Mexican, NOT Castilian and NOT neutral Latin American", "Spanish from Spain": "Castilian Spanish accent from Spain", "Canarian Spanish": "Canary Islands Spanish accent",
             "Mexican": "Mexican Spanish accent", "Colombian": "Colombian Spanish accent", "British": "British English accent", "American": "American English accent", "Italian": "Italian accent",
             "Brazilian Portuguese": "Brazilian Portuguese accent", "European Portuguese from Portugal": "European Portuguese accent", "French": "French accent", "German": "German accent"}
IDIOMA_EN = {"es": "Spanish", "es-ar": "Spanish", "en": "English", "it": "Italian", "de": "German", "pt": "Portuguese", "fr": "French"}
def es_rap(ids):
    t = " ".join([(CAT.get(str(i).lower()) or {}).get("nombre", str(i)) + " " + tags_base(i, str(i).lower()) for i in ids]).lower()
    return any(k in t for k in ("hip hop", "rap", "trap", "drill", "phonk", "cloud rap", "boom bap", "g-funk", "old school", "golden age", "crunk", "dirty south", "turntabl", "sample-based"))
GUIAS_FAM = {"Urbano y hip hop": "flow urbano, ritmo marcado, personalidad y actitud; frases con pegada rítmica", "Latino y tropical": "ritmo bailable, frases cortas con pegada rítmica, coros fáciles de corear, sabor y picardía",
             "Rock": "actitud, imágenes potentes, estribillo coreable tipo himno", "Electrónica": "pocas palabras, frases repetitivas e hipnóticas pensadas para un drop", "Raíces y folk": "narrativa con imágenes del paisaje y la gente, sencillez poética",
             "Reggae y mundo": "mensaje positivo, ritmo relajado, frases repetidas tipo mantra", "Jazz, soul y funk": "elegancia y swing, emoción en cada frase, vocabulario sofisticado", "Cine, clásica y ambiente": "poética, minimalista y evocadora"}
def guia_letra(ids):
    if es_rap(ids): return "RAP: versos densos con rimas internas, flow y punchlines; el hook cantado es corto y pegadizo. Que suene a rap de verdad, no a canción pop con rimas.", True
    f = (CAT.get(str(ids[0]).lower()) or {}).get("familia", ""); return GUIAS_FAM.get(f, ""), False
VOZ_SEXO = {"hombre": "male lead vocals", "mujer": "female lead vocals", "duo": "male and female duet vocals", "coro": "group choir vocals, gang vocals", "rap": "male rap vocals, rhythmic spoken flow", "susurro": "soft intimate whispered vocals"}
VOZ_GENERO = [(("flamenco", "rumba", "timple", "isa"), "passionate raw flamenco-style singing with melisma"), (("tango",), "dramatic expressive tango singing"), (("bolero", "balada", "ballad"), "tender emotional crooner vocals"),
              (("salsa", "merengue", "bachata", "cumbia", "vallenato", "mambo"), "tropical sonero-style vocals with backing chorus"), (("reggaeton", "perreo", "dembow", "dancehall", "latin trap"), "urban melodic vocals with autotune touch"),
              (("mariachi", "ranchera"), "powerful ranchera vibrato vocals"), (("soul", "motown", "gospel", "r&b", "neo soul"), "warm soulful gospel-tinged vocals with melismas"), (("jazz", "swing", "blues"), "smoky jazz club vocals"),
              (("rock", "punk", "grunge", "metal"), "gritty powerful rock vocals"), (("country", "folk", "bluegrass", "celtic"), "honest warm storytelling vocals"), (("electro", "house", "techno", "trance", "edm", "synthwave"), "processed airy electronic vocals"),
              (("reggae", "ska", "dub"), "laid-back reggae vocals with offbeat phrasing")]
def voz_caption(ids, p, rap):
    sexo = VOZ_SEXO.get(p.get("voz") or ""); txt = " ".join(tags_base(i, str(i).lower()) + " " + (CAT.get(str(i).lower()) or {}).get("nombre", "") for i in ids[:1]).lower(); gen = next((v for ks, v in VOZ_GENERO if any(k in txt for k in ks)), "")
    if rap and p.get("voz") in (None, "", "auto", "hombre", "rap"): return "male rap vocals, rhythmic rap flow with a sung hook"
    if rap and p.get("voz") == "mujer": return "female rap vocals, rhythmic flow with a sung hook"
    return ", ".join(x for x in [sexo, gen] if x)
def fon_arg(l):
    """Escribe la letra CANTADA como suena en Buenos Aires (ll/y → sh) para que el motor de música marque el acento. La letra mostrada y guardada no cambia."""
    out = []
    for ln in str(l or "").splitlines():
        if ln.strip().startswith("["): out.append(ln); continue
        x = re.sub(r"ll", "sh", ln); x = re.sub(r"Ll|LL", "Sh", x)
        x = re.sub(r"(?<=[aeiouáéíóú])y(?=[aeiouáéíóú])", "sh", x); x = re.sub(r"\by(?=[aeiouáéíóú])", "sh", x); x = re.sub(r"\bY(?=[aeiouáéíóú])", "Sh", x)
        out.append(x)
    return "\n".join(out)
def letra_cantada(letra, p, idioma):
    if idioma == "es" and (p.get("acento") or "") == "Argentine Rioplatense" and p.get("acento_fon", True) is not False and letra and "[instrumental]" not in str(letra).lower(): return fon_arg(letra)
    return letra
MODOS_EN = {"major": ("Ionian (major scale)", "major"), "natural minor": ("Aeolian (natural minor scale)", "minor"), "harmonic minor": ("harmonic minor scale with raised 7th, dramatic", "minor"), "melodic minor": ("melodic minor scale, jazzy and smooth", "minor"),
            "dorian": ("Dorian mode, minor with raised 6th, soulful and groovy", "minor"), "phrygian": ("Phrygian mode, minor with flat 2nd, dark and Spanish-tinged", "minor"), "lydian": ("Lydian mode, major with raised 4th, dreamy and bright", "major"),
            "mixolydian": ("Mixolydian mode, major with flat 7th, bluesy and rock", "major"), "locrian": ("Locrian mode, tense and unstable", "minor"), "major pentatonic": ("major pentatonic scale, open and folk-like", "major"),
            "minor pentatonic": ("minor pentatonic scale, raw and bluesy", "minor"), "blues": ("blues scale with blue notes", "minor"), "phrygian dominant": ("Phrygian dominant scale, flamenco, Spanish", "minor"),
            "double harmonic": ("double harmonic scale, Arabic and Eastern flavor", "minor"), "whole tone": ("whole tone scale, floating and dreamlike", "major")}
def texto_modo(p):
    m = MODOS_EN.get(p.get("modo") or "")
    if not m: return None, None
    raiz = (p.get("tono") or "").split(" ")[0]
    return (f"{raiz + ' ' if raiz else ''}{m[0]}", (f"{raiz} {m[1]}" if raiz else None))
def construir_caption(ids, pre, bpm, ex, inst, idioma, p):
    """Prompt para el motor de música: en inglés, con el género mandando, voz y acento concretos y calidad de estudio."""
    t0 = tags_base(ids[0], str(ids[0]).lower()); gen = t0.split(",")[0].strip(); rap = es_rap(ids); P = []
    if pre: P.append(pre)
    P.append(tags_combinados(ids))
    if not inst:
        P.append(voz_caption(ids, p, rap))
        acc = ACENTO_EN.get(p.get("acento") or "")
        P.append(f"lead vocals sung in {IDIOMA_EN.get(idioma, idioma)}" + (f" with {acc}" if acc else ""))
    else: P.append("instrumental, no vocals")
    P.append(", ".join(ex)); P.append(f"{bpm} BPM" if bpm else "")
    P.append("professional studio production, polished mix and master, rich dynamics, wide stereo image, award-winning quality")
    P.append(f"authentic {gen}" + ("" if gen.lower() in ("pop", "modern pop") else ", NOT generic pop"))
    return ". ".join(x for x in P if x)
def caption_final(ids, pre, bpm, ex, inst, idioma, p, letra, nombres):
    """Caption del productor (Gemini) + condiciones fijas de voz, acento, idioma y BPM; si Gemini no está, el método de siempre."""
    base = construir_caption(ids, pre, bpm, ex, inst, idioma, p)
    try:
        g = cl.caption_gemini(nombres, IDIOMA_EN.get(idioma, idioma), p.get("tema"), letra, p.get("voz"), p.get("acento"), bpm, inst, ", ".join(ex))
        if not g: return base
        fijo = []
        if not inst:
            t0 = tags_base(ids[0], str(ids[0]).lower()); rap = es_rap(ids); fijo.append(voz_caption(ids, p, rap))
            acc = ACENTO_EN.get(p.get("acento") or ""); fijo.append(f"lead vocals sung in {IDIOMA_EN.get(idioma, idioma)}" + (f" with {acc}" if acc else ""))
        else: fijo.append("instrumental, no vocals")
        if bpm: fijo.append(f"{bpm} BPM")
        gen = tags_base(ids[0], str(ids[0]).lower()).split(",")[0].strip()
        return (pre + ". " if pre else "") + g + ". " + ". ".join(x for x in fijo if x) + f". authentic {gen}" + ("" if gen.lower() in ("pop", "modern pop") else ", NOT generic pop") + ", professional studio production, award-winning quality"
    except Exception: return base
AJUSTES_F = os.path.join(SALIDA, "ajustes-compositor.json"); FUENTES_F = os.path.join(SALIDA, "fuentes-letras.json")
def ajustes_leer():
    try: return {"poeta": True, **json.load(open(AJUSTES_F, encoding="utf8"))}
    except Exception: return {"poeta": True}
def fuentes_guardar(titulo, fu):
    try:
        try: d = json.load(open(FUENTES_F, encoding="utf8"))
        except Exception: d = {}
        d[titulo] = [{"titular": a, "medio": b, "enlace": c} for a, b, c in fu]; json.dump(d, open(FUENTES_F, "w", encoding="utf8"), ensure_ascii=False)
    except Exception: pass
def fuentes_de(titulo):
    try: return json.load(open(FUENTES_F, encoding="utf8")).get(titulo) or []
    except Exception: return []
def descargar_ollama():
    """Saca el modelo de letras de la memoria: en un Mac de 16 GB compite con el motor de música y lo ralentiza."""
    for url in {cl.OLLAMA, "http://127.0.0.1:11434", "http://127.0.0.1:11435"}:
        try:
            tags = json.load(ur.urlopen(url + "/api/ps", timeout=3)).get("models") or []
            for m in tags: ur.urlopen(ur.Request(url + "/api/generate", json.dumps({"model": m.get("name") or m.get("model"), "keep_alive": 0}).encode(), {"Content-Type": "application/json"}), timeout=15).read()
        except Exception: pass
ACE_TMP = os.path.expanduser("~/IslandCrewAI/ACE-Step-1.5/.cache/acestep/tmp/api_audio")
def ocupado():
    nom = {"crear": "una canción", "video": "un videoclip", "yt": "una subida a YouTube", "portada": "una portada", "voz": "un proceso de voz"}
    return [nom.get(k, k) for k, v in ACTIVO.items() if v]
def _peso(ruta):
    try: return os.path.getsize(ruta)
    except OSError: return 0
def limpiar_temporales(edad_s=1200, todo=False):
    """Borra lo que queda a medias o sobrante: WAVs en bruto del motor de música (carpeta interna del Mac), portadas/vídeos de canciones que ya no están en la biblioteca y temporales. Con todo=True ignora la edad."""
    lib_n = 0; liberado = 0; ahora = time.time(); hay = any(ACTIVO.values())
    lim = ahora + 1 if todo else ahora - (10800 if hay else edad_s)
    def quitar(ruta):
        nonlocal lib_n, liberado
        try:
            if os.path.isdir(ruta): tam = sum(_peso(os.path.join(a, f)) for a, _, fs in os.walk(ruta) for f in fs); shutil.rmtree(ruta, ignore_errors=True)
            else: tam = _peso(ruta); os.remove(ruta)
            liberado += tam; lib_n += 1
        except OSError: pass
    try:
        for f in os.listdir(ACE_TMP):
            q = os.path.join(ACE_TMP, f)
            if not f.startswith("._") and os.path.isfile(q) and os.path.getmtime(q) < lim: quitar(q)
            elif f.startswith("._"): quitar(q)
    except OSError: pass
    if not hay or todo:
        try:
            enlib = {os.path.splitext(x.get("archivo", ""))[0] for x in lib_leer()}
            enlib |= {os.path.splitext(f)[0].replace("-ficha", "") for f in os.listdir(SALIDA) if f.lower().endswith((".mp3", ".wav", ".txt")) and not f.startswith("._")}
            for sub in ("portadas", "videos"):
                b = os.path.join(SALIDA, sub)
                for d in os.listdir(b) if os.path.isdir(b) else []:
                    q = os.path.join(b, d)
                    if d.startswith("._") or (os.path.isdir(q) and d not in enlib and "audiolibro" not in d and os.path.getmtime(q) < (ahora + 1 if todo else ahora - 3600)): quitar(q)
            for pat in ("*_af.wav", "*_rec.wav", "*.part", "*.tmp"):
                for q in glob.glob(os.path.join(SALIDA, pat)): quitar(q)
            yt = os.path.join(SALIDA, "_yt_tmp")
            for f in os.listdir(yt) if os.path.isdir(yt) else []:
                q = os.path.join(yt, f)
                if os.path.getmtime(q) < lim: quitar(q)
        except OSError: pass
    return {"archivos": lib_n, "liberado_mb": round(liberado / 1e6, 1)}
def ia_letra(titulo, estilo, idioma, tema, dur, ctx=None):
    try:
        modelo(); estilo = nombres_estilos(estilo) if "|" in str(estilo) or str(estilo).lower() in CAT else estilo
        ctx = ctx or {}; ids = ctx.get("ids") or [estilo]; guia, rap = guia_letra(ids); rap = rap or FORZAR_RAP["on"]; guia = guia if not FORZAR_RAP["on"] else (guia + " Se recitará en voz alta con flow rítmico: versos con ritmo marcado y rimas."); ac = ctx.get("acento"); dtxt = DIALECTOS.get(ac) if ac and ac != "neutro" else None
        if dtxt and idioma == "es" and ac in ("British", "American", "Brazilian Portuguese", "European Portuguese from Portugal", "French", "German", "Italian"): dtxt = None
        if dtxt: tema = f"{tema} DIALECTO OBLIGATORIO: escribe con el vocabulario y las expresiones de {dtxt}.".strip()
        aj = ajustes_leer(); os.environ["CB_POETA_NUBE"] = "0" if aj.get("poeta_nube") is False else "1"
        if aj.get("poeta") or (aj.get("poeta_nube") is not False and cl._clave_gemini()):
            l = cl.letra_poetica(titulo, estilo, idioma, tema, dur <= 100 if not rap else True, dtxt, guia, rap, bool(aj.get("actualidad")))
            fu = cl.FUENTES.get(titulo)
            if fu: fuentes_guardar(titulo, fu)
            return l
        return cl.letra_con_ollama(titulo, estilo, idioma, tema, dur <= 100 if not rap else True, dtxt, guia, rap, )
    except SystemExit as e: raise RuntimeError(msg_error(e))
def ia_titulo_tema(estilo, idioma):
    try:
        t = ollama_gen(f"Dame un título de canción ORIGINAL y una idea breve (una frase) para una canción de estilo {estilo} en {IDIOMAS.get(idioma, idioma)}. Responde SOLO con JSON así: {{\"titulo\":\"...\",\"tema\":\"...\"}}")
        m = re.search(r"\{.*\}", t, re.S); d = json.loads(m.group(0)) if m else {}
        if d.get("titulo"): return str(d["titulo"])[:80], str(d.get("tema") or "")[:200]
    except BaseException: pass
    return random.choice(TITULOS), random.choice(TEMAS)

def ia_artista(estilo, idioma):
    try:
        t = ollama_gen(f"Inventa UN nombre artístico original (1 a 3 palabras) para un cantante o grupo de {estilo}, que suene bien en {IDIOMAS.get(idioma, idioma)}. Sin nombres de artistas reales ni marcas. Responde SOLO con el nombre.", 1.0)
        t = t.strip().split("\n")[0].strip(" \"«»'*.")
        if 2 <= len(t) <= 40: return t
    except BaseException: pass
    return random.choice(["Luna Cabrera", "Los Vientos del Sur", "Mar Adentro", "Kiko Dunas", "Sal y Sol", "Nube Roja", "Isla Beat"])
def prompt_imagen(titulo, estilo, letra, animo):
    base = f"album cover art, {estilo} music, mood {', '.join(animo or [])}, title «{titulo}», no text, no letters, no words, cinematic, highly detailed, square composition"
    try:
        if letra and len(letra) > 40:
            t = ollama_gen("Lee esta letra de canción y describe en INGLÉS, en una sola frase de máximo 35 palabras, la escena visual más potente para su portada (personajes, lugar, luz, colores, atmósfera). Sin texto ni letras en la imagen. Responde SOLO con la frase.\n\n" + letra[:1800], 0.8)
            t = t.strip().split("\n")[0].strip(" \"")
            if len(t) > 15: return f"album cover art, {estilo} music, {t}, no text, no letters, cinematic lighting, highly detailed, square composition"
    except BaseException: pass
    return base
def azar(con_letra=True):
    ests = random.sample(list(CAT), random.choice([1, 1, 2, 3])); estilo = ests[0]; idioma = random.choice(["es", "es", "en", "it", "de"]); dur = random.choice([60, 90, 120, 150])
    titulo, tema = ia_titulo_tema(estilo, idioma); letra = ""
    if con_letra:
        try: letra = ia_letra(titulo, estilo, idioma, tema, dur, {"ids": ests})
        except BaseException: letra = ""
    return {"titulo": titulo, "estilo": estilo, "estilos": ests, "idioma": idioma, "tema": tema, "duracion": dur, "letra": letra, "tono": random.choice(["", "C major", "A minor", "G major", "D minor", "E minor", "F major"]), "compas": random.choice(["4/4", "4/4", "3/4", "6/8"]),
            "bpm": random.choice([0, 80, 90, 100, 110, 120]), "voz": random.choice(["hombre", "mujer", "duo", "auto"]), "energia": random.choice(["low", "medium", "high"]), "animo": random.sample(ANIMOS, 1), "instrumentos": []}

def lista_estilos(p):
    ids = [str(x).strip() for x in (p.get("estilos") or [p.get("estilo") or "pop"]) if str(x).strip()][:5]
    if (p.get("estilo_libre") or "").strip(): ids = (ids + [p["estilo_libre"].strip()])[:5]
    return ids or ["pop"]
def nombres_estilos(txt):
    return " + ".join((CAT.get(x.strip().lower()) or {}).get("nombre", x.strip()) for x in str(txt).split("|") if x.strip())
def tags_combinados(ids):
    tg = [tags_base(i, i.lower()) for i in ids]
    return tg[0] if len(tg) == 1 else f"seamless fusion of {len(tg)} genres: " + " + ".join(f"({t})" for t in tg)
def tags_base(estilo_in, estilo_id): return (CAT.get(estilo_id) or {}).get("tags") or ESTILOS.get(estilo_id, estilo_in)
TIPOS_JSON = json.dumps(TIPOS_NEGOCIO, ensure_ascii=False)
def grupos_estilos():
    g = {}
    for k, v in CAT.items(): g.setdefault(v["familia"], []).append([k, v["nombre"]])
    return {f: sorted(l, key=lambda x: x[1].lower()) for f, l in sorted(g.items())}
_GV = {}
def gvoz():
    if "m" not in _GV: _GV["m"] = _cargar("gv", "voz-gemini.py")
    return _GV["m"]
FORZAR_RAP = {"on": False}
def trabajo_crear(j, p):
    try:
        titulo = (p.get("titulo") or "").strip(); ids_est = lista_estilos(p); estilo_in = ids_est[0]; estilo_id = estilo_in.lower()
        _nom = " + ".join((CAT.get(i.lower()) or {}).get("nombre", i) for i in ids_est); _fam = (CAT.get(estilo_id) or {}).get("familia", "Pop")
        idioma = p.get("idioma") or "es"; tema = p.get("tema") or ""; es_jingle = p.get("formato") in ("jingle", "anuncio"); dur = min(240, max(20, int(p.get("duracion") or 120))); bpm = int(p.get("bpm") or 0); n = min(3, max(1, int(p.get("n") or 1))); inst = bool(p.get("instrumental"))
        vg = (p.get("voz_motor") == "gemini") and not inst
        if vg and not gvoz().clave(): raise RuntimeError("Para la voz de Gemini hace falta la clave gratuita de Gemini (GEMINI_API_KEY en el proyecto).")
        FORZAR_RAP["on"] = bool(vg)
        letra = "[Instrumental]" if inst else (p.get("letra") or "").strip()
        if letra and not inst and es_borrador(letra):  # lo escrito es una idea/petición, no una letra: la IA compone la canción a partir de ella
            tema = (letra + " " + tema).strip(); letra = ""
            if not titulo: upd(j, fase="letra", pc=2, msg="Buscando un título con gancho para tu idea…"); titulo = ia_titulo_de(tema, _nom, idioma)
        if not titulo: upd(j, fase="letra", pc=2, msg="Inventando el título con IA…"); titulo, _tm = ia_titulo_tema(nombres_estilos("|".join(ids_est)), idioma); tema = tema or _tm
        if not t5_ok(): raise RuntimeError("El disco T5 EVO no está conectado. Conéctalo para guardar la música.")
        letra_manual = bool(letra) and not inst
        if letra_manual:
            rep = letra_repetida(letra)
            if rep: raise RuntimeError(f"Esa letra es igual o muy parecida a «{rep}», que ya creaste. No se permite repetir letras (YouTube puede sancionar el canal). Cambia la letra o deja la caja vacía para que la IA escriba una nueva.")
            if n > 1 and not es_jingle: n = 1; upd(j, msg="Con una letra escrita por ti hago una sola versión (cada versión debe tener letra distinta).")
        if not letra: upd(j, fase="letra", pc=3, msg="Escribiendo la letra con IA…"); letra = letra_unica(titulo, _nom, idioma, tema, dur, lambda i: upd(j, msg=f"Letra demasiado parecida a otra existente; escribo una nueva (intento {i+2}/6)…"), {"ids": ids_est, "acento": p.get("acento")}); j["letra"] = letra
        descargar_ollama()  # libera ~5 GB de memoria antes de generar la música
        upd(j, fase="motor", pc=6, msg="Arrancando el motor de música (la primera vez puede tardar unos minutos)…")
        try: cl.asegurar_acestep()
        except SystemExit as e: raise RuntimeError(msg_error(e))
        hechas = []
        for i in range(n):
            if i > 0 and not inst and not letra_manual:
                upd(j, fase="letra", msg=f"Escribiendo una letra nueva para la versión {i+1}…"); letra = letra_unica(titulo, _nom, idioma, tema, dur, None, {"ids": ids_est, "acento": p.get("acento")}); j["letra"] = letra
            if not inst: registrar_letra(titulo, letra)
            plan_vg = None; dur_i = dur
            if vg:
                upd(j, fase="voz", pc=7, msg="Gemini graba la voz con el acento elegido…")
                plan_vg = gvoz().preparar(letra, p.get("voz_gemini") or "Puck", p.get("acento"), bpm or 92, os.path.join(tempfile.gettempdir(), "cb-vg-" + str(int(time.time()))), lambda m: upd(j, msg=m))
                bpm = plan_vg["bpm"]; dur_i = plan_vg["duracion"]
            base = 8 + i * (90 / n); ancho = 90 / n
            def hook(tid, meta, fase, pc, msg="", bib=None, base=base, ancho=ancho): upd(j, fase="generando", pc=int(min(97, base + ancho * (max(0, pc) / 100))), msg=(msg or "Generando…") + (f" · versión {i+1}/{n}" if n > 1 else ""))
            fm.progreso = hook
            ex = []
            estilo_vis = _nom or estilo_in
            _mtxt, _mkey = texto_modo(p)
            if _mtxt: ex.append("music in " + _mtxt + ", melody and harmony strictly following this scale")
            elif p.get("tono"): ex.append("key of " + p["tono"])
            if p.get("compas"): ex.append(p["compas"] + " time signature")
            ex += [x for x in (p.get("animo") or []) if x]; ex += [x + " instrument" for x in (p.get("instrumentos") or []) if x]
            if p.get("energia"): ex.append(p["energia"] + " energy")
            if es_jingle and not bpm: bpm = random.choice([100, 104, 108, 112, 118])
            JPRE = "advertising jingle, catchy memorable hook, polished professional studio production, bright clear lead vocal, tight arrangement, strong rhythmic groove, major key, radio-ready" if es_jingle else ""
            pet = {"prompt": caption_final(ids_est, JPRE, bpm, ex, inst or vg, idioma, p, letra, _nom) + (". instrumental beat with a clear pocket and space for a rapper, no vocals, no sung voice" if vg else ""), "lyrics": ("[Instrumental]" if vg else letra_cantada(letra, p, idioma)), "vocal_language": idioma, "audio_duration": dur_i, "thinking": False, "audio_format": "wav", "batch_size": 1, "seed": random.randint(1, 2**31 - 1), "use_random_seed": False,
                   "meta": {"titulo": titulo if n == 1 else f"{titulo} (v{i+1})", "estilo": re.sub(r"[^a-z0-9-]+", "-", estilo_id)[:30] or "libre", "formato": (p.get("formato") if es_jingle else "cancion"), "idioma": idioma, "marca": ""}}
            if _mkey: pet["key_scale"] = _mkey
            elif p.get("tono"): pet["key_scale"] = p["tono"]
            if p.get("compas"): pet["time_signature"] = p["compas"].split("/")[0]
            if bpm: pet["bpm"] = bpm
            tit_v = pet["meta"]["titulo"]
            try: ok = fm.generar(pet, f"{i+1}/{n}")
            except SystemExit as e: raise RuntimeError(msg_error(e))
            if not ok: raise RuntimeError("El motor de música devolvió un error. Mira ~/IslandCrewAI/acestep.log")
            ruta = fm.ULTIMA_RUTA
            if vg and plan_vg:
                upd(j, fase="voz", pc=94, msg="Mezclando la voz de Gemini con la base (ajustando cada estrofa al ritmo)…")
                base_i = ruta[:-4] + "-base.wav"; shutil.move(ruta, base_i); r_m = gvoz().mezclar(plan_vg, base_i, ruta, VOZ_PY)
                upd(j, msg=f"Voz mezclada: {r_m['estrofas']} de {r_m['de']} estrofas a {r_m['bpm']} BPM.")
                try: os.remove(base_i)
                except OSError: pass
                shutil.rmtree(plan_vg["carpeta"], ignore_errors=True)
            cl.salida(ruta, tit_v, estilo_vis, idioma)
            mp3 = ruta[:-4] + ".mp3"; fin = mp3 if os.path.exists(mp3) else ruta; arch = os.path.basename(fin)
            num, ico, icl = siguiente_numero(); dseg = duracion_seg(fin); sha = huella_sha(fin)
            datos = {"pieza": num, "numero": ico, "licencia": icl, "duracion_seg": dseg, "sha256": sha}
            try: open(ruta[:-4] + "-ficha.txt", "w", encoding="utf8").write(ficha_texto({"titulo": tit_v, "estilo": estilo_vis, "idioma": idioma, "creada": time.strftime("%d/%m/%Y %H:%M"), "letra": "", **datos}, completa=True))
            except OSError: pass
            d = lib_leer(); d.insert(0, {"archivo": arch, "titulo": tit_v, "estilo": estilo_vis, "idioma": idioma, "creada": time.strftime("%Y-%m-%d %H:%M"), "letra": letra, "youtube": None, "familia": _fam, "estilos": ids_est, **datos, **({"tipo": "jingle", "negocio": p.get("negocio")} if es_jingle else {}), "ops": {k: p.get(k) for k in ("voz_motor", "voz_gemini", "tono", "modo", "compas", "bpm", "voz", "acento", "animo", "instrumentos", "energia", "tema", "duracion") if p.get(k)}}); lib_guardar(d); hechas.append(arch)
        vc = nombre_voz(p.get("voz_clon")) if p.get("voz_clon") else ""
        if vc and hechas and not inst:
            for q, arch_h in enumerate(list(hechas)):
                k = {}; ct = threading.Thread(target=trabajo_voz, args=(k, {"orden": "cantar", "archivo": arch_h, "voz": vc, "tono": int(p.get("voz_clon_tono") or 0)}), daemon=True); ct.start()
                while ct.is_alive():
                    upd(j, fase="voz", pc=min(99, 90 + int(k.get("pc", 0) / 12 + q * 8 / max(1, len(hechas)))), msg=f"Pasando la canción {q+1}/{len(hechas)} a tu voz «{vc}»… " + str(k.get("msg", ""))[-70:]); time.sleep(2)
                if k.get("ok") is False: upd(j, msg="La canción está hecha, pero no pude pasarla a tu voz: " + str(k.get("msg", ""))[:200])
        upd(j, fase="listo", pc=100, ok=True, msg=f"Listo: {len(hechas)} canción(es) en tu biblioteca.", res=hechas)
    except BaseException as e: upd(j, fase="fallo", ok=False, msg=msg_error(e))
    finally:
        ACTIVO["crear"] = None
        try: limpiar_temporales(120)
        except Exception: pass

def titulo_tecnico(t):
    """«trap · cancion · es», «Sin título 1523»…: nombres de archivo, no títulos de canción."""
    t = (t or "").strip().lower()
    return (not t) or bool(re.match(r"^[\w\- ]+ · (cancion|jingle[\w\-]*|audio|narrado)( · \w+)?$", t)) or t.startswith("sin título") or bool(re.match(r"^\d{8}-\d{6}", t))
def poner_portada(e, st, ts):
    c = os.path.join("portadas", st, ts) if ts else os.path.join("portadas", st)
    e["portada"] = os.path.join(c, "portada-3000-con-texto.jpg"); e["portada_yt"] = os.path.join(c, "youtube-1280x720.jpg"); e["portada_sel"] = ts; e["portada_v"] = ts or 0
    e["portada_ok"] = any(x["ts"] == ts and x.get("ok") for x in e.get("portadas", []))
def trabajo_portada(j, p):
    try:
        arch = os.path.basename(p.get("archivo") or ""); st = os.path.splitext(arch)[0]; d = lib_leer(); e = next((x for x in d if x.get("archivo") == arch), None)
        if e is None: e = {"archivo": arch, "titulo": st}; d.insert(0, e)
        titulo = (p.get("titulo") or e.get("titulo") or st).strip(); artista = (p.get("artista") or e.get("artista") or "").strip()
        est = e.get("estilo") or ""; fam = e.get("familia") or next((v["familia"] for v in CAT.values() if v["nombre"] == est), "Pop")
        base_c = os.path.join(SALIDA, "portadas", st); ts = str(int(time.time() * 1000)); carpeta = os.path.join(base_c, ts); os.makedirs(carpeta, exist_ok=True); foto = None
        if p.get("foto"):
            import base64; raw = p["foto"].split(",", 1)[-1]; foto = os.path.join(base_c, "foto-original.jpg"); open(foto, "wb").write(base64.b64decode(raw))
        if not foto and p.get("reusar") and os.path.isfile(os.path.join(base_c, "foto-original.jpg")): foto = os.path.join(base_c, "foto-original.jpg")
        otra = None
        if p.get("usar_letra") or p.get("ia_imagen"):
            upd(j, pc=15, msg="La IA está pensando qué escena dibujar con tu letra…"); pr = prompt_imagen(titulo, est, e.get("letra") or "", (e.get("ops") or {}).get("animo")); j["prompt"] = pr
            upd(j, pc=30, msg="Creando la imagen con IA (internet, gratis; tarda hasta 1-2 min)…"); otra = pt.imagen_ia(pr, random.randint(1, 10**6))
            if otra is None: upd(j, msg="No pude crear la imagen por IA (¿sin internet?). Sigo con arte generativo propio…")
        upd(j, pc=65, msg="Componiendo la portada y los formatos para cada plataforma…")
        if completar_registro(e): pass
        if titulo_tecnico(titulo):
            upd(j, pc=10, msg="Inventando un título de verdad para la canción…"); titulo, _tm = ia_titulo_tema(est or "pop", e.get("idioma") or "es")
        if not artista: upd(j, msg="Inventando el nombre del artista…"); artista = ia_artista(est or "pop", e.get("idioma") or "es")
        res = pt.crear(carpeta, titulo, artista, fam, est, foto, p.get("look") or "auto", otra, float(p.get("fuerza") or 0.4), numero=e.get("numero"))
        e["titulo"] = titulo; e["artista"] = artista; e.setdefault("portadas", [])
        if e.get("portada") and not e["portadas"]: e["portadas"] = [{"ts": "", "ok": bool(e.get("portada_ok"))}]
        e["portadas"].append({"ts": ts, "ok": False}); poner_portada(e, st, ts)
        d = [x for x in d if x.get("archivo") != arch]; d.insert(0, e); lib_guardar(d)
        upd(j, fase="listo", pc=100, ok=True, msg="Portada lista: 3000×3000, Spotify, YouTube, Instagram e historias. Están en la carpeta «portadas» del disco.", res=list(res))
    except BaseException as ex: upd(j, fase="fallo", ok=False, msg=msg_error(ex))
    finally: ACTIVO["portada"] = None

TITULAR = "Maximiliano Olmos Sánchez · Island Crew Marketing"
def ficha_texto(e, completa=False):
    dur = mmss(e["duracion_seg"]) if e.get("duracion_seg") else ""; ops = e.get("ops") or {}
    tec = " · ".join(str(x) for x in [ops.get("tono"), ops.get("modo"), ops.get("compas"), ops.get("bpm") and f"{ops['bpm']} BPM", ops.get("voz"), *(ops.get("animo") or [])] if x)
    ei = " · ".join(x for x in [e.get("estilo") and f"Estilo: {e['estilo']}", e.get("idioma") and f"Idioma: {e['idioma']}"] if x)
    L = ["━━━━━━━━━━━━━━━━━━━━", "FICHA DE CREACIÓN · ISLAND CREW MUSIC", "━━━━━━━━━━━━━━━━━━━━", f"Título: {e.get('titulo','')}"]
    if e.get("artista"): L.append(f"Artista: {e['artista']}")
    L.append(f"Nº de registro de la pieza: {e.get('numero') or 'pendiente'}"); L.append(f"Nº de licencia: {e.get('licencia') or 'pendiente'}")
    if dur: L.append(f"Duración: {dur}")
    if ei: L.append(ei)
    if tec: L.append(f"Detalles: {tec}")
    if e.get("creada"): L.append(f"Creada: {e['creada']}")
    if e.get("sha256"): L.append(f"Huella digital (SHA-256): {e['sha256'][:32]}…")
    fu = fuentes_de(e.get("titulo"))
    if fu: L += ["Inspirada en titulares de actualidad (solo como inspiración):"] + [f"- {x['titular']}" + (f" ({x['enlace']})" if x.get("enlace") else "") for x in fu]
    L += [f"Titular de todos los derechos: {TITULAR}", "Creación asistida por IA.", "Todos los derechos reservados.", "Para usarla: hola@islandcrew.es (cita el número de licencia)."]
    return "\n".join(L) + "\n"

def titulo_viral(e):
    """Título corto y magnético con IA local; si la IA no está, uno de plantilla."""
    base = e.get("titulo") or "Sin título"; est = (e.get("estilo") or "").strip()
    try:
        t = ollama_gen(f"Escribe UN solo título de YouTube viral, de máximo 60 caracteres, para una canción llamada «{base}» de estilo {est}. Que despierte curiosidad o emoción, sin mentir, sin comillas, sin hashtags. Responde SOLO con el título.", 0.9)
        t = t.strip().split("\n")[0].strip(" \"«»'*"); 
        if 8 <= len(t) <= 80: return t
    except BaseException: pass
    return f"{base} 🎧 {est.title()} que se te pega" if est else f"{base} 🎧 Música original"
def descripcion_yt(e):
    base = e.get("titulo") or "esta canción"; est = e.get("estilo") or "música"
    gancho = f"🎧 «{base}» — {est} original. Dale al play, súbelo y cuéntame en comentarios qué sentiste.\n👉 Suscríbete para no perderte la próxima pieza."
    tags = " ".join("#" + re.sub(r"[^A-Za-z0-9ÁÉÍÓÚáéíóúñÑ]", "", x) for x in [est, "MusicaOriginal", "IslandCrew", "CabraBeats", "MusicaIA", e.get("idioma") == "es" and "MusicaEnEspañol" or "NewMusic"] if x and re.sub(r"[^A-Za-z0-9]", "", str(x)))
    autoria = f"✍️ Obra 100% original de Maximiliano Olmos Sánchez.\n🐐 Creada con Cabra Beats, el software de creación musical de Island Crew para negocios y todo tipo de proyectos (islandcrew.es)."
    cola = f"\n\n{autoria}\n\n{tags}"; cabeza = f"{gancho}\n\n{ficha_texto(e)}"
    lt = (e.get("letra") or "").strip(); letra = ""
    if lt and lt.lower() != "[instrumental]":
        sitio = 4900 - len(cabeza) - len(cola) - len("\n\n📝 LETRA COMPLETA\n") - 400  # margen para los créditos que añade YouTube
        letra = "\n\n📝 LETRA COMPLETA\n" + (lt if len(lt) <= sitio else lt[:max(sitio, 0)].rsplit("\n", 1)[0] + "\n…")
    return cabeza + letra + cola
UNIV_F = os.path.join(SALIDA, "universos-usados.json")
def universos_usados():
    try: return json.load(open(UNIV_F, encoding="utf8"))
    except BaseException: return []
def registrar_universo(firma):
    try: d = universos_usados(); d.append(firma); json.dump(d[-500:], open(UNIV_F, "w", encoding="utf8"))
    except BaseException: pass
CLIPOPS = {"estilos": [[k, v["nombre"]] for k, v in vc.ESTILOS_LETRA.items()], "grades": [[k, v[0]] for k, v in vc.GRADES.items()], "fuentes": [[k, k.capitalize()] for k in vc.FUENTE if os.path.isfile(vc.FUENTE[k])],
           "pos": [["abajo", "Abajo"], ["centro", "Centro"], ["arriba", "Arriba"], ["izquierda", "Abajo a la izquierda"]], "anim": [["fundido", "Fundido"], ["subida", "Sube"], ["bajada", "Baja"]]}
def aplicar_universo(u, f):
    f = {k: v for k, v in (f or {}).items() if v not in (None, "")}
    if f.get("estilo_letra") in vc.ESTILOS_LETRA:
        st = vc.ESTILOS_LETRA[f["estilo_letra"]]; u["estilo_letra"] = f["estilo_letra"]; u["estilo_nombre"] = st["nombre"]
        if not f.get("fuente"): u["fuente"] = vc.fuente_ok(st["fuentes"][0]) if u["fuente"] not in st["fuentes"] else u["fuente"]
        u["pos"] = st["pos"] if not f.get("pos") else u["pos"]; u["anim"] = st["anim"] if not f.get("anim") else u["anim"]
    if f.get("fuente") in vc.FUENTE: u["fuente"] = vc.fuente_ok(f["fuente"])
    if f.get("grade") in vc.GRADES: u["grade"] = f["grade"]; u["grade_nombre"] = vc.GRADES[f["grade"]][0]
    if f.get("pos") in ("abajo", "centro", "arriba", "izquierda"): u["pos"] = f["pos"]
    if f.get("anim") in ("fundido", "subida", "bajada"): u["anim"] = f["anim"]
    if f.get("grano") is not None: u["grano"] = max(0, min(20, int(f["grano"])))
    if f.get("barras") is not None: u["barras"] = bool(f["barras"])
    return u
def clip_universo(e, nuevo=False, forzar=None):
    c = e.setdefault("clip", {}); u = c.get("universo")
    if nuevo or not u:
        u = vc.universo(e, universos_usados()); c["videos"] = c.get("videos") or {}
        shutil.rmtree(os.path.join(SALIDA, "videos", os.path.splitext(e["archivo"])[0], "escenas"), ignore_errors=True)
    u = aplicar_universo(dict(u), forzar); c["universo"] = u; return u
def trabajo_clip(j, p):
    try:
        arch = os.path.basename(p.get("archivo") or ""); st = os.path.splitext(arch)[0]; d = lib_leer(); e = next((x for x in d if x.get("archivo") == arch), None)
        if e is None: raise RuntimeError("No encuentro esa canción.")
        audio = os.path.join(SALIDA, arch)
        if not os.path.isfile(audio): raise RuntimeError("No encuentro el audio de la canción.")
        if not (e.get("letra") or "").strip() or (e.get("letra") or "").strip().lower() == "[instrumental]": e = dict(e, letra="[Verse]\n" + (e.get("titulo") or "Música"))
        fm_ = p.get("formato") if p.get("formato") in ("h", "v") else "h"; previa = bool(p.get("previa"))
        u = clip_universo(lib_ent(d, arch) or e, bool(p.get("nuevo_universo")), p.get("forzar")); t5 = os.path.join(SALIDA, "videos", st)
        upd(j, fase="video", pc=1, msg="Preparando el videoclip…")
        def prog(pc, m=""): upd(j, pc=int(pc), msg=m or j.get("msg"))
        r = vc.montar(audio, e["letra"], e, u, os.path.join(t5, "previa.mp4" if previa else f"clip-{fm_}.mp4"), t5, fm_, previa, llm=lambda pr, t: ollama_gen(pr, t), fallback=lambda t, pal, sm: pt.arte_generativo(t, pal, sm),
                      progreso=prog, idioma=e.get("idioma") or "es", n_escenas=int(p.get("n_escenas") or 8), intro=(float(p["intro"]) if p.get("intro") not in (None, "") else None), desfase=float(p.get("desfase") or 0), dur_audio=e.get("duracion_seg"))
        d = lib_leer(); en = lib_ent(d, arch)
        if en is not None:
            c = en.setdefault("clip", {}); c["universo"] = u; c.setdefault("videos", {}); c["mundo"] = r.get("mundo") or u.get("mundo", ""); c["v"] = int(time.time()); c["ajustes"] = {"formato": fm_, "n_escenas": int(p.get("n_escenas") or 8), "intro": p.get("intro"), "desfase": p.get("desfase") or 0}
            if previa: c["previa"] = os.path.join("videos", st, "previa.mp4")
            else: c["videos"][fm_] = os.path.join("videos", st, f"clip-{fm_}.mp4"); registrar_universo(u["firma"])
            lib_guardar(d)
        nota = f" OJO: {r['fallos']} de {r['escenas']} escenas no se pudieron crear con IA (internet lento o servicio saturado) y se repitieron imágenes. Pulsa «Crear videoclip» otra vez y solo se reintentan esas." if r.get("fallos") else ""
        ns = f" Letra sincronizada: {r.get('sync')}." if str(r.get("sync", "")).startswith("exacta") else f" OJO: letra con sincronía ESTIMADA ({r.get('aviso_sync') or 'sin reconocedor'}); ajusta con «Adelantar/retrasar»."
        upd(j, fase="listo", pc=100, ok=True, msg=("Vista previa lista (24 s)." if previa else "¡Videoclip terminado! Lo tienes en la caja de la canción.") + ns + nota)
    except BaseException as ex: upd(j, fase="fallo", ok=False, msg=msg_error(ex))
    finally: ACTIVO["video"] = None
def lib_ent(d, arch): return next((x for x in d if x.get("archivo") == arch), None)
def trabajo_youtube(j, archivo, publico, clip=None, programar=None):
    try:
        y = yt(); ruta = os.path.join(SALIDA, os.path.basename(archivo))
        if not os.path.exists(ruta): raise RuntimeError("No encuentro ese archivo en tu biblioteca.")
        d = lib_leer(); e = next((x for x in d if x.get("archivo") == os.path.basename(archivo)), {"titulo": os.path.splitext(os.path.basename(archivo))[0], "archivo": os.path.basename(archivo)})
        if completar_registro(e): d = [x for x in d if x.get("archivo") != e["archivo"]]; d.insert(0, e); lib_guardar(d)
        reg = y.cargar(y.REGISTRO, {}); h = y.huella(ruta)
        if h in reg: upd(j, fase="listo", pc=100, ok=True, msg="Ya estaba subida a YouTube (no se repite): " + reg[h]["url"], res=reg[h]["url"]); return
        upd(j, pc=8, msg="Comprobando el permiso de YouTube…")
        if y.estado_permiso() != "ok": raise RuntimeError("YouTube no está conectado en este Mac. Pulsa «Conectar YouTube» (en Estado del sistema) y acepta el permiso en el navegador.")
        upd(j, fase="video", pc=20, msg="Creando el vídeo con portada…"); pp = os.path.join(SALIDA, e["portada_yt"]) if e.get("portada_yt") else ""; cp = os.path.join(SALIDA, ((e.get("clip") or {}).get("videos") or {}).get(clip or "", "x")); v = (cp if clip and os.path.isfile(cp) else None) or y.a_video(ruta, {"titulo": e.get("titulo"), "estilo": e.get("estilo"), "portada": pp if os.path.isfile(pp) else ""})
        try:
            upd(j, fase="subiendo", pc=55, msg="Subiendo a YouTube (puede tardar unos minutos)…"); tok = y.token_valido(False)
            tv = titulo_viral(e); upd(j, msg="Título para YouTube: " + tv)
            r = y.subir(v, tv, y.con_credito(descripcion_yt(e)), tok, bool(publico), programar or None)
        finally:
            if v != ruta and os.path.basename(v).endswith("_yt.mp4"):
                try: os.remove(v)
                except OSError: pass
        real = (r.get("status") or {}).get("privacyStatus", "private"); url = f"https://studio.youtube.com/video/{r['id']}/edit"
        reg[h] = {"archivo": os.path.basename(ruta), "id": r["id"], "url": url, "fecha": time.strftime("%Y-%m-%d %H:%M"), "privacidad": real, "programado_para": (r.get("status") or {}).get("publishAt") or ""}; y.guardar_seguro(y.REGISTRO, reg)
        mini_ok, mini_msg = False, "esta canción no tiene portada creada"
        if e.get("portada_yt"):
            upd(j, pc=96, msg="Poniendo la portada como miniatura del vídeo…"); mini_ok, mini_msg = y.miniatura_jpg(r["id"], os.path.join(SALIDA, e["portada_yt"]), tok)
        e["youtube"] = {"url": url, "estado": real, "fecha": time.strftime("%Y-%m-%d"), "miniatura": bool(mini_ok), "programado_para": (r.get("status") or {}).get("publishAt") or ""}; d = [x for x in d if x.get("archivo") != e["archivo"]]; d.insert(0, e); lib_guardar(d)
        nota_m = " · Miniatura: tu portada ✔" if mini_ok else (f" · Miniatura NO puesta ({mini_msg})" if e.get("portada_yt") else " · Sin portada: YouTube usará un fotograma como miniatura")
        upd(j, fase="listo", pc=100, ok=True, msg=("Publicada" if real == "public" else "Subida como PRIVADA (revísala y publícala en YouTube Studio)") + nota_m + ": " + url, res=url)
    except BaseException as ex: upd(j, fase="fallo", ok=False, msg=msg_error(ex))
    finally: ACTIVO["yt"] = None


# ---- Cola de subidas programadas (30 canciones, 1 al día…) ----
COLA_F = os.path.join(SALIDA, "cola-youtube.json"); COLA_W = {"t": None}; MAX_SUBIDAS_DIA = 5  # la cuota gratis de YouTube da para unas 5-6 subidas al día
def cola_leer():
    try: return json.load(open(COLA_F, encoding="utf8"))
    except Exception: return []
def cola_guardar(c):
    tmp = COLA_F + ".tmp"; open(tmp, "w", encoding="utf8").write(json.dumps(c, ensure_ascii=False, indent=1)); os.replace(tmp, COLA_F)
def cola_worker():
    fallos = 0
    try:
        while True:
            c = cola_leer(); pend = [x for x in c if x.get("estado") == "pendiente"]
            if not pend: break
            hoy = time.strftime("%Y-%m-%d")
            if sum(1 for x in c if x.get("subida_dia") == hoy) >= MAX_SUBIDAS_DIA: time.sleep(900); continue
            with JLOCK:
                if ACTIVO["yt"]: busy = True
                else: busy = False; j = nuevo_job("youtube"); ACTIVO["yt"] = j["id"]
            if busy: time.sleep(20); continue
            it = pend[0]; prog = it.get("programar")
            try:
                if not prog or datetime.datetime.fromisoformat(prog.replace("Z", "+00:00")) < datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=20):
                    prog = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)).strftime("%Y-%m-%dT%H:%M:%SZ"); it["programar"] = prog
            except Exception: pass
            trabajo_youtube(j, it["archivo"], False, None, prog)
            c = cola_leer(); it = next((x for x in c if x.get("archivo") == it["archivo"] and x.get("estado") == "pendiente"), None)
            if it is None: continue  # cancelada mientras subía
            if j.get("ok"): it["estado"] = "subida"; it["subida_dia"] = hoy; it["msg"] = j.get("msg", "")[-200:]; fallos = 0
            else:
                m = str(j.get("msg", "")); it["msg"] = m[-300:]
                if "quota" in m.lower() or "cuota" in m.lower(): cola_guardar(c); time.sleep(3600); continue  # sin cuota hoy: reintenta en una hora
                it["estado"] = "error"; fallos += 1
            cola_guardar(c)
            if fallos >= 3: break  # algo va mal (p. ej. YouTube sin conectar): se para y te lo dice
            time.sleep(5)
    finally: COLA_W["t"] = None
def cola_arrancar():
    with JLOCK:
        if COLA_W["t"] and COLA_W["t"].is_alive(): return
        COLA_W["t"] = threading.Thread(target=cola_worker, daemon=True); COLA_W["t"].start()

_EST = {"t": 0, "d": None}
def vivo(url):
    try: ur.urlopen(url, timeout=2); return True
    except Exception as e: return hasattr(e, "code")
def estado():
    if time.time() - _EST["t"] < 8 and _EST["d"]: return _EST["d"]
    try: libre = shutil.disk_usage("/").free / 1e9
    except Exception: libre = -1
    try: yest = yt().estado_permiso() if os.path.exists(os.path.expanduser("~/IslandCrewAI/youtube/client_secret.json")) else "sin_cliente"
    except BaseException: yest = "desconocido"
    d = {"acestep": vivo(cl.ACE_URL), "ollama": vivo("http://127.0.0.1:11434/api/tags") or vivo("http://127.0.0.1:11435/api/tags"), "t5": t5_ok(), "salida": SALIDA, "libre_gb": round(libre, 1), "youtube": yest, "ffmpeg": bool(shutil.which("ffmpeg"))}
    _EST.update(t=time.time(), d=d); return d
def completar_registro(e):
    """Toda canción tiene su número único: si es antigua y no lo tiene, se le asigna aquí (una sola vez) y se guarda."""
    ruta = os.path.join(SALIDA, e.get("archivo", ""))
    if not os.path.isfile(ruta): return False
    cam = False
    if not e.get("numero"): n, ico, icl = siguiente_numero(); e.update(pieza=n, numero=ico, licencia=icl); cam = True
    if not e.get("duracion_seg"): e["duracion_seg"] = duracion_seg(ruta); cam = True
    if not e.get("sha256"):
        try: e["sha256"] = huella_sha(ruta); cam = True
        except OSError: pass
    return cam
def canciones():
    d = lib_leer(); conocidos = {x.get("archivo") for x in d}; extra = []
    try:
        arch = sorted((f for f in os.listdir(SALIDA) if f.lower().endswith((".mp3", ".wav")) and not f.startswith(".")), key=lambda f: -os.path.getmtime(os.path.join(SALIDA, f)))
        bases = {os.path.splitext(f)[0]: f for f in arch if f.lower().endswith(".mp3")}
        for f in arch:
            b = os.path.splitext(f)[0]
            if f in conocidos or (f.lower().endswith(".wav") and b in bases) or bases.get(b, f) in conocidos: continue
            extra.append({"archivo": f, "titulo": re.sub(r"^\d{8}-\d{6}_", "", b).replace("_", " · "), "estilo": "", "idioma": "", "creada": time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(os.path.join(SALIDA, f)))), "letra": "", "youtube": None})
    except Exception: pass
    todo = d + extra; cam = False
    for e in sorted((x for x in todo if not x.get("numero")), key=lambda x: x.get("creada") or ""):
        cam = completar_registro(e) or cam
    if cam:
        try: lib_guardar([x for x in todo if x.get("numero") or x in d] if False else todo)
        except OSError: pass
    return todo[:150]

class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _ok_host(self): return (self.headers.get("Host") or "").split(":")[0] in ("127.0.0.1", "localhost")
    def _json(self, d, c=200): b = json.dumps(d, ensure_ascii=False).encode(); self.send_response(c); self.send_header("Content-Type", "application/json; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.send_header("Cache-Control", "no-store"); self.end_headers(); self.wfile.write(b)
    def _fichero(self, ruta, tipo):
        tam = os.path.getsize(ruta); rg = self.headers.get("Range"); a, b = 0, tam - 1; c = 200
        if rg and rg.startswith("bytes="):
            x, _, z = rg[6:].partition("-"); a = int(x) if x else 0; b = int(z) if z else tam - 1; b = min(b, tam - 1); c = 206
        self.send_response(c); self.send_header("Content-Type", tipo); self.send_header("Accept-Ranges", "bytes"); self.send_header("Content-Length", str(b - a + 1))
        if c == 206: self.send_header("Content-Range", f"bytes {a}-{b}/{tam}")
        self.end_headers()
        with open(ruta, "rb") as f:
            f.seek(a); resto = b - a + 1
            while resto > 0:
                bl = f.read(min(1 << 16, resto))
                if not bl: break
                try: self.wfile.write(bl)
                except Exception: break
                resto -= len(bl)
    def do_GET(self):
        if not self._ok_host(): return self._json({"error": "no"}, 403)
        u = urlparse(self.path); q = parse_qs(u.query)
        if u.path == "/": b = open(os.path.join(AQUI, "cabra-beats-app.html"), encoding="utf8").read().replace("__TOKEN__", TOKEN).replace("__TIPOS__", TIPOS_JSON).replace("__CLIPOPS__", json.dumps(CLIPOPS, ensure_ascii=False)).replace("__ESTILOS__", json.dumps(grupos_estilos(), ensure_ascii=False), 1).replace("__IDIOMAS__", json.dumps(IDIOMAS, ensure_ascii=False), 1).replace("__ANIMOS__", json.dumps(ANIMOS), 1).replace("__INSTR__", json.dumps(INSTR), 1).replace("__TEMAS__", json.dumps(TEMAS, ensure_ascii=False), 1).encode(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        if u.path in ("/img/cabra-hero.jpg", "/img/cabra-recorte.png"):
            p = os.path.join(AQUI, os.path.basename(u.path))
            if os.path.exists(p): return self._fichero(p, "image/jpeg" if p.endswith(".jpg") else "image/png")
            return self._json({}, 404)
        if u.path == "/logo.png":
            p = os.path.join(AQUI, "cabra-beats-logo.png")
            if not os.path.exists(p): p = os.path.join(RAIZ, "public", "images", "icon-512.png")
            if os.path.exists(p): return self._fichero(p, "image/png")
            return self._json({}, 404)
        if u.path == "/api/ocupado": return self._json({"activo": ocupado()})
        if u.path == "/avatar":
            b = open(os.path.join(AQUI, "cabra-avatar.html"), encoding="utf8").read().replace("__TOKEN__", TOKEN).encode(); self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b); return
        if u.path.startswith("/av/"):
            rel = u.path[4:].replace("..", ""); p = os.path.join(AQUI, "vendor-avatar", rel)
            MIME = {".mjs": "text/javascript", ".js": "text/javascript", ".wasm": "application/wasm", ".task": "application/octet-stream"}
            if os.path.isfile(p): return self._fichero(p, MIME.get(os.path.splitext(p)[1], "application/octet-stream"))
            return self._json({"error": "falta: ejecuta scripts/preparar-avatar.sh"}, 404)
        if (q.get("t") or [""])[0] != TOKEN and self.headers.get("x-cb") != TOKEN: return self._json({"error": "sin permiso"}, 403)
        if u.path == "/audio":
            f = os.path.basename((q.get("f") or [""])[0]); p = os.path.join(SALIDA, f)
            if f.lower().endswith((".mp3", ".wav")) and os.path.exists(p): return self._fichero(p, "audio/mpeg" if f.lower().endswith(".mp3") else "audio/wav")
            return self._json({}, 404)
        if u.path == "/clip":
            f = (q.get("f") or [""])[0]; pq = os.path.normpath(os.path.join(SALIDA, f))
            if f.startswith("videos/") and pq.startswith(os.path.normpath(SALIDA)) and f.lower().endswith((".mp4", ".jpg")) and os.path.isfile(pq): return self._fichero(pq, "video/mp4" if f.lower().endswith(".mp4") else "image/jpeg")
            return self._json({}, 404)
        if u.path == "/portada":
            f = (q.get("f") or [""])[0].replace("..", ""); pq = os.path.join(SALIDA, f)
            if f.startswith("portadas/") and f.lower().endswith(".jpg") and os.path.isfile(pq): return self._fichero(pq, "image/jpeg")
            return self._json({}, 404)
        if u.path == "/api/estado": return self._json(estado())
        if u.path == "/api/canciones": return self._json(canciones())
        if u.path == "/api/job": return self._json(JOBS.get((q.get("id") or [""])[0]) or {"fase": "desconocido", "ok": False, "msg": "No encuentro ese trabajo."})
        return self._json({}, 404)
    def do_POST(self):
        if not self._ok_host() or self.headers.get("x-cb") != TOKEN: return self._json({"error": "sin permiso"}, 403)
        try: p = json.loads(self.rfile.read(int(self.headers.get("Content-Length") or 0)) or b"{}")
        except Exception: p = {}
        norm_idioma(p)
        r = urlparse(self.path).path
        if r == "/api/azar": return self._json(azar(bool(p.get("letra", True))))
        if r == "/api/ia":
            try:
                if p.get("campo") == "letra":
                    idea = p.get("letra") if es_borrador(p.get("letra")) else ""; tema = ((idea or "") + " " + (p.get("tema") or "")).strip(); tit = (p.get("titulo") or "").strip(); est = nombres_estilos(p.get("estilo") or "pop")
                    if not tit and idea: tit = ia_titulo_de(idea, est, p.get("idioma") or "es")
                    return self._json({"texto": letra_unica(tit or "Sin título", p.get("estilo") or "pop", p.get("idioma") or "es", tema, int(p.get("duracion") or 120), None, {"ids": lista_estilos(p), "acento": p.get("acento")}), "titulo": tit})
                est = nombres_estilos(p.get("estilo") or "pop")
                if p.get("campo") == "artista": return self._json({"texto": ia_artista(est, p.get("idioma") or "es")})
                t, tm = ia_titulo_tema(est, p.get("idioma") or "es"); return self._json({"texto": t if p.get("campo") == "titulo" else tm})
            except BaseException as e: return self._json({"error": msg_error(e)}, 500)
        if r == "/api/jingle-letra":
            try:
                l = letra_jingle(p); tit = "Jingle · " + (p.get("negocio") or "").strip(); esl = (p.get("eslogan") or "").strip()
                if not esl:
                    try: esl = ollama_gen(f"Escribe UN eslogan publicitario de máximo 7 palabras para «{p.get('negocio')}» ({p.get('tipo')}), sin inventar datos ni precios. Responde SOLO con el eslogan.", 0.9).strip().split("\n")[0].strip(" \"«»'*.")
                    except BaseException: esl = ""
                return self._json({"letra": l, "titulo": tit, "eslogan": esl})
            except BaseException as e: return self._json({"error": msg_error(e)}, 500)
        if r == "/api/clip-universo":
            arch = os.path.basename(p.get("archivo") or ""); d = lib_leer(); e = lib_ent(d, arch)
            if e is None: return self._json({"error": "no encuentro la canción"}, 404)
            u = clip_universo(e, bool(p.get("nuevo")), p.get("forzar")); st = os.path.splitext(arch)[0]; mu = os.path.join("videos", st, f"muestra-{int(time.time())}.jpg")
            try:
                esc = os.path.join(SALIDA, "videos", st, "escenas"); fo = next((os.path.join(esc, f) for f in sorted(os.listdir(esc)) if f.endswith("-h.jpg")), None) if os.path.isdir(esc) else None
                if not fo and e.get("portada"): fo = os.path.join(SALIDA, e["portada"].replace("portada-3000-con-texto", "portada-3000-sin-texto"))
                for f0 in glob.glob(os.path.join(SALIDA, "videos", st, "muestra-*.jpg")): os.remove(f0)
                vc.muestra(e, u, os.path.join(SALIDA, mu), fo)
            except BaseException as ex: mu = ""
            e["clip"]["muestra"] = mu; lib_guardar(d); return self._json({"ok": True, "universo": u, "muestra": mu})
        if r == "/api/clip":
            with JLOCK:
                if ACTIVO["video"]: return self._json({"id": ACTIVO["video"], "ya": True})
                j = nuevo_job("video"); ACTIVO["video"] = j["id"]
            threading.Thread(target=trabajo_clip, args=(j, p), daemon=True).start(); return self._json({"id": j["id"]})
        if r == "/api/crear":
            with JLOCK:
                if ACTIVO["crear"]: return self._json({"id": ACTIVO["crear"], "ya": True})
                j = nuevo_job("crear"); ACTIVO["crear"] = j["id"]
            threading.Thread(target=trabajo_crear, args=(j, p), daemon=True).start(); return self._json({"id": j["id"]})
        if r == "/api/youtube":
            with JLOCK:
                if ACTIVO["yt"]: return self._json({"id": ACTIVO["yt"], "ya": True})
                j = nuevo_job("youtube"); ACTIVO["yt"] = j["id"]
            threading.Thread(target=trabajo_youtube, args=(j, p.get("archivo") or "", p.get("publico"), p.get("clip"), p.get("programar")), daemon=True).start(); return self._json({"id": j["id"]})
        if r == "/api/conectar-youtube":
            def con():
                try: yt().token_valido(True, True)
                except BaseException: pass
                _EST["t"] = 0
            threading.Thread(target=con, daemon=True).start(); return self._json({"ok": True, "msg": "Se abre el navegador para que aceptes el permiso de YouTube."})
        if r == "/api/avatar-informe":
            f = os.path.join(SALIDA, "avatar-informe.json")
            try: d = json.load(open(f, encoding="utf8"))
            except Exception: d = []
            d.append(p); json.dump(d[-30:], open(f, "w", encoding="utf8"), ensure_ascii=False, indent=1)
            return self._json({"ok": True})
        if r == "/api/ajustes":
            d = ajustes_leer()
            for k in ("poeta", "actualidad", "poeta_nube"):
                if k in p: d[k] = bool(p[k])
            if p: json.dump(d, open(AJUSTES_F, "w", encoding="utf8"))
            return self._json(d)
        if r == "/api/limpiar":
            return self._json(limpiar_temporales(300))
        if r == "/api/plan":
            f = os.path.join(SALIDA, "plan-crecimiento.json")
            try: d = json.load(open(f, encoding="utf8"))
            except Exception: d = {}
            if p.get("guardar"):
                nuevo = {k: p["guardar"].get(k) for k in ("inicio", "fase", "subs", "horas", "shorts", "avisos", "vistas") if k in p["guardar"]}
                h = d.get("historial") or []
                if any(k in nuevo for k in ("subs", "horas", "vistas")): h.append({"fecha": time.strftime("%Y-%m-%d"), "subs": nuevo.get("subs", d.get("subs")), "horas": nuevo.get("horas", d.get("horas")), "vistas": nuevo.get("vistas", d.get("vistas"))})
                d.update(nuevo); d["historial"] = h[-60:]; json.dump(d, open(f, "w", encoding="utf8"), ensure_ascii=False, indent=1)
            return self._json(d)
        if r == "/api/yt-lote":
            c = cola_leer(); hay = {x["archivo"] for x in c if x.get("estado") in ("pendiente", "subida")}; lib = {x.get("archivo"): x for x in lib_leer()}; n = 0
            for it in p.get("items") or []:
                a = os.path.basename(it.get("archivo") or "")
                if a in hay or not os.path.exists(os.path.join(SALIDA, a)) or (lib.get(a) or {}).get("youtube"): continue
                c.append({"archivo": a, "titulo": (lib.get(a) or {}).get("titulo") or a, "programar": it.get("programar"), "estado": "pendiente"}); hay.add(a); n += 1
            cola_guardar(c)
            if n: cola_arrancar()
            return self._json({"ok": True, "añadidas": n})
        if r == "/api/yt-cola":
            c = cola_leer(); return self._json({"cola": c, "activa": bool(COLA_W["t"] and COLA_W["t"].is_alive()), "max_dia": MAX_SUBIDAS_DIA})
        if r == "/api/yt-cola-cancelar":
            c = cola_leer()
            for x in c:
                if x.get("estado") in ("pendiente", "error"): x["estado"] = "cancelada"
            cola_guardar(c); return self._json({"ok": True})
        if r == "/api/yt-cola-reintentar":
            c = cola_leer()
            for x in c:
                if x.get("estado") == "error": x["estado"] = "pendiente"
            cola_guardar(c); cola_arrancar(); return self._json({"ok": True})
        if r == "/api/borrar":
            n = 0; fs = p.get("archivos") or []
            if p.get("subidas"): fs = [x["archivo"] for x in lib_leer() if x.get("youtube")]
            for f in fs:
                st = os.path.splitext(os.path.basename(f))[0]
                for suf in (".mp3", ".wav", "-ficha.txt"):
                    q = os.path.join(SALIDA, st + suf)
                    if os.path.isfile(q):
                        try: os.remove(q); n += 1
                        except OSError: pass
            for f in fs:
                for sub in ("portadas", "videos"): shutil.rmtree(os.path.join(SALIDA, sub, os.path.splitext(os.path.basename(f))[0]), ignore_errors=True)
            quitar = {os.path.splitext(os.path.basename(f))[0] for f in fs}
            lib_guardar([x for x in lib_leer() if os.path.splitext(x.get("archivo", ""))[0] not in quitar]); _EST["t"] = 0
            return self._json({"ok": True, "borrados": n})
        if r == "/api/portada":
            with JLOCK:
                if ACTIVO["portada"]: return self._json({"id": ACTIVO["portada"], "ya": True})
                j = nuevo_job("portada"); ACTIVO["portada"] = j["id"]
            threading.Thread(target=trabajo_portada, args=(j, p), daemon=True).start(); return self._json({"id": j["id"]})
        if r == "/api/voz-estado": return self._json(voz_estado())
        if r == "/api/voz-subir":
            import base64; nom = nombre_voz(p.get("nombre")); carp = os.path.join(SALIDA, "voces", nom, "audios"); os.makedirs(carp, exist_ok=True); n = 0
            for a in p.get("archivos") or []:
                nm = re.sub(r"[^A-Za-z0-9._-]", "_", os.path.basename(a.get("nombre") or f"audio{n}.wav"))[-60:]
                open(os.path.join(carp, f"{n:03d}_{nm}"), "wb").write(base64.b64decode((a.get("b64") or "").split(",", 1)[-1])); n += 1
            return self._json({"ok": True, "subidos": n, "total": len(os.listdir(carp))})
        if r == "/api/voz":
            with JLOCK:
                if ACTIVO["voz"]: return self._json({"id": ACTIVO["voz"], "ya": True})
                j = nuevo_job("voz"); ACTIVO["voz"] = j["id"]
            threading.Thread(target=trabajo_voz, args=(j, p), daemon=True).start(); return self._json({"id": j["id"]})
        if r == "/api/portada-estado":
            arch = os.path.basename(p.get("archivo") or ""); d = lib_leer(); e = next((x for x in d if x.get("archivo") == arch), None)
            if e is None: return self._json({"error": "no encuentro la canción"}, 404)
            st = os.path.splitext(arch)[0]; ts = str(p.get("ts") if p.get("ts") is not None else e.get("portada_sel", ""))
            if e.get("portada") and not e.get("portadas"): e["portadas"] = [{"ts": "", "ok": bool(e.get("portada_ok"))}]
            lst = e.get("portadas", [])
            if p.get("estado") == "aprobar":
                for x in lst: x["ok"] = (x["ts"] == ts)
                poner_portada(e, st, ts)
            elif p.get("estado") == "usar": poner_portada(e, st, ts)
            elif p.get("estado") == "eliminar":
                shutil.rmtree(os.path.join(SALIDA, "portadas", st, ts) if ts else os.path.join(SALIDA, "portadas", st), ignore_errors=True)
                lst = [x for x in lst if x["ts"] != ts]; e["portadas"] = lst
                if lst: poner_portada(e, st, lst[-1]["ts"])
                else:
                    for k in ("portada", "portada_yt", "portada_ok", "portada_v", "portada_sel", "portadas"): e.pop(k, None)
            lib_guardar(d); return self._json({"ok": True})
        if r == "/api/meta":
            arch = os.path.basename(p.get("archivo") or ""); d = lib_leer(); e = next((x for x in d if x.get("archivo") == arch), None)
            if e is None: e = {"archivo": arch, "titulo": os.path.splitext(arch)[0]}; d.insert(0, e)
            for k in ("titulo", "artista"):
                if p.get(k) is not None: e[k] = str(p[k]).strip()[:120]
            lib_guardar(d); return self._json({"ok": True})
        if r == "/api/finder":
            f = os.path.basename(p.get("archivo") or ""); c = p.get("portada"); subprocess.Popen(["open", os.path.join(SALIDA, "videos" if p.get("clip") else "portadas", os.path.splitext(f)[0])] if (c or p.get("clip")) else ["open", "-R", os.path.join(SALIDA, f)]); return self._json({"ok": True})
        if r == "/api/salir": self._json({"ok": True}); threading.Thread(target=lambda: (time.sleep(0.4), os._exit(0)), daemon=True).start(); return
        return self._json({}, 404)

def puerto_libre():
    for pt in [8765] + list(range(8766, 8790)):
        s = socket.socket(); 
        try: s.bind(("127.0.0.1", pt)); s.close(); return pt
        except OSError: s.close()
    return 0
def abrir_ventana(url):
    if os.environ.get("CB_NO_VENTANA"): return
    chrome = "/Applications/Google Chrome.app"
    if os.path.isdir(chrome): subprocess.Popen(["open", "-na", "Google Chrome", "--args", "--app=" + url, "--user-data-dir=" + os.path.expanduser("~/IslandCrewAI/ventana-chrome"), "--window-size=1180,860"])
    else: subprocess.Popen(["open", url])
def main():
    os.makedirs(os.path.dirname(INFO), exist_ok=True)
    if "--limpiar" in sys.argv:
        r = limpiar_temporales(0, True); print(f"Limpieza hecha: {r['archivos']} elementos, {r['liberado_mb']} MB liberados."); return
    if "--parar" in sys.argv:
        try: i = json.load(open(INFO)); os.kill(int(i["pid"]), 15); print("Cabra Beats parado.")
        except Exception: print("No estaba en marcha.")
        return
    try:  # si ya está en marcha, solo se vuelve a abrir la ventana
        i = json.load(open(INFO)); os.kill(int(i["pid"]), 0)
        if vivo(f"http://127.0.0.1:{i['port']}/logo.png"): abrir_ventana(f"http://127.0.0.1:{i['port']}/"); return
    except Exception: pass
    pt = int(os.environ.get("CB_PUERTO") or puerto_libre()); srv = ThreadingHTTPServer(("127.0.0.1", pt), H)
    json.dump({"pid": os.getpid(), "port": pt}, open(INFO, "w")); os.chmod(INFO, 0o600)
    threading.Timer(0.8, lambda: abrir_ventana(f"http://127.0.0.1:{pt}/")).start()
    def calentar():  # enciende solo la IA de letras y el motor de música, sin que toques nada
        try: modelo()
        except BaseException: pass
        try: cl.asegurar_acestep()
        except BaseException: pass
        _EST["t"] = 0
    threading.Thread(target=calentar, daemon=True).start()
    threading.Thread(target=lambda: (time.sleep(5), limpiar_temporales(1200)), daemon=True).start()
    if any(x.get("estado") == "pendiente" for x in cola_leer()): cola_arrancar()
    print(f"Cabra Beats personal en marcha (puerto {pt}).", flush=True); srv.serve_forever()
if __name__ == "__main__": main()
