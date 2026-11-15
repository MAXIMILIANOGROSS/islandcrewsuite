#!/usr/bin/env python3
"""Puerta local de la Fábrica de canciones: crea música en TU Mac, sin la web (sin Vercel, sin Supabase, sin claves).
Reutiliza el motor que ya existe (scripts/fabrica-musica.py + ACE-Step). Gratis y sin conexión a la web.

  Interactivo:  python3 scripts/cancion-local.py
  Directo:      python3 scripts/cancion-local.py --titulo "Mar de Corralejo" --estilo hiphop --idioma es --tema "el mar y los amigos" --letra-ia
  Con tu letra: python3 scripts/cancion-local.py --titulo "Mi canción" --estilo pop --letra-archivo letra.txt

Requisitos: disco T5 EVO conectado (o MUSICA_DIR), ACE-Step instalado (la puerta lo arranca si no está) y, para --letra-ia, Ollama con algún modelo."""
import threading, random, os, sys, json, time, shutil, subprocess, argparse, importlib.util, random, re, urllib.request as u

for _k in ("ISLANDCREW_URL", "CRON_SECRET"): os.environ.pop(_k, None)  # MODO LOCAL: el motor no habla con la web
AQUI = os.path.dirname(os.path.abspath(__file__))
ACE_URL = os.environ.get("ACESTEP_URL", "http://127.0.0.1:8001")
ACE_CMD = "bash -lc 'cd ~/IslandCrewAI/ACE-Step-1.5 && PATH=$HOME/.local/bin:$PATH ./start_api_server_macos.sh >> ~/IslandCrewAI/acestep.log 2>&1'"
OLLAMA = os.environ.get("OLLAMA_URL", "http://127.0.0.1:11434")
ESTILOS = {
    "hiphop": "hip hop boom bap, drums secos, bajo profundo, crujido de vinilo, rap con flow",
    "trap": "trap oscuro, 808 graves, hi-hats rápidos, rap melódico",
    "pop": "pop moderno, estribillo pegadizo, sintetizadores brillantes, voz clara",
    "rock": "rock, guitarras eléctricas, batería potente, voz enérgica",
    "reggaeton": "reggaeton, dembow, bajo marcado, voz urbana, ritmo bailable",
    "balada": "balada emotiva, piano, cuerdas suaves, voz sentida",
    "flamenco": "flamenco fusión, guitarra española, palmas, voz rasgada",
    "reggae": "reggae relajado, skank de guitarra, bajo cálido, voz suave",
    "electronica": "electrónica, house, sintetizadores, bombo constante, ambiente nocturno",
    "latino": "latino tropical, percusión, metales, ritmo de baile, voz alegre",
    "timple": "folk canario, timple, guitarra, ritmo isleño, voz cálida",
}
IDIOMAS = {"es": "español de España (puedes usar jerga canaria)", "es-ar": "español de Argentina (rioplatense: vos, che, pibe)", "en": "inglés", "it": "italiano", "de": "alemán", "pt": "portugués", "fr": "francés"}

def vivo(url):
    try: u.urlopen(url, timeout=3); return True
    except u.HTTPError: return True  # responde (aunque sea 404): el servidor está en marcha
    except Exception: return False

def asegurar_acestep():
    if vivo(ACE_URL): return
    print("Arrancando ACE-Step (la primera vez puede tardar 1-3 minutos)…", flush=True)
    subprocess.Popen(ACE_CMD, shell=True)
    for _ in range(60):
        time.sleep(5)
        if vivo(ACE_URL): print("ACE-Step listo."); return
    sys.exit("ACE-Step no arrancó. Mira ~/IslandCrewAI/acestep.log")

def comando_ollama():
    """Cómo arrancar Ollama en este Mac (igual que el trabajador): OLLAMA_CMD, la app de Ollama o «ollama serve». None si no está instalado."""
    import shlex
    if os.environ.get("OLLAMA_CMD"): return os.environ["OLLAMA_CMD"]
    for ap in ("/Applications/Ollama.app", os.path.expanduser("~/Applications/Ollama.app")):
        if os.path.isdir(ap): return "open -a " + shlex.quote(ap)
    for b in (shutil.which("ollama"), "/opt/homebrew/bin/ollama", "/usr/local/bin/ollama"):
        if b and os.path.isfile(b): return shlex.quote(b) + " serve"
    return None

def dir_modelos():
    """Carpeta con los modelos de Ollama: OLLAMA_MODELS, ~/.islandcrew-env o el disco extraíble (T5 EVO). Es la que tiene una subcarpeta «manifests»."""
    import glob
    cand = [os.environ.get("OLLAMA_MODELS", "")]
    try:
        for l in open(os.path.expanduser("~/.islandcrew-env"), encoding="utf8"):
            if "OLLAMA_MODELS" in l and "=" in l: cand.append(l.split("=", 1)[1].strip().strip("'\""))
    except Exception: pass
    for v in glob.glob("/Volumes/*"):
        cand += [v + "/IslandCrewAI/ollama/models", v + "/IslandCrewAI/ollama", v + "/IslandCrewAI/modelos/ollama", v + "/ollama/models", v + "/ollama", v + "/.ollama/models", v + "/IslandCrewAI/.ollama/models"]
        cand += glob.glob(v + "/*/*ollama*/models") + glob.glob(v + "/*/*ollama*") + glob.glob(v + "/*ollama*/models") + glob.glob(v + "/*ollama*")
    for c in cand:
        c = os.path.expanduser(c or "")
        if c and os.path.isdir(os.path.join(c, "manifests")): return c
        if c and os.path.isdir(os.path.join(c, "models", "manifests")): return os.path.join(c, "models")
    return None

def modelo_ollama():
    if os.environ.get("OLLAMA_MODEL"): return os.environ["OLLAMA_MODEL"]
    global OLLAMA
    def tags():
        try: return json.load(u.urlopen(OLLAMA + "/api/tags", timeout=5)).get("models") or []
        except Exception: return None
    md = dir_modelos(); m = tags()
    if md and not m:  # los modelos están en otro disco: se arranca un Ollama PROPIO (puerto 11435) apuntando a esa carpeta, sin tocar el que ya hubiera
        exe = next((b for b in (shutil.which("ollama"), "/opt/homebrew/bin/ollama", "/usr/local/bin/ollama", "/Applications/Ollama.app/Contents/Resources/ollama") if b and os.path.isfile(b)), None)
        if not exe: sys.exit(f"Encuentro tus modelos en {md} pero no el programa «ollama». Instálalo (https://ollama.com/download).")
        OLLAMA = "http://127.0.0.1:11435"
        if tags() is None:
            print(f"Arrancando Ollama con tus modelos de {md}…", flush=True)
            subprocess.Popen([exe, "serve"], env={**os.environ, "OLLAMA_MODELS": md, "OLLAMA_HOST": "127.0.0.1:11435"}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            for _ in range(24):
                time.sleep(5)
                if tags() is not None: break
        m = tags()
        if m is None: sys.exit("Ollama no arrancó con la carpeta de modelos del disco extraíble.")
    elif m is None:  # no responde y no hay carpeta externa: se intenta arrancar el normal
        cmd = comando_ollama()
        if not cmd: sys.exit("Ollama no está instalado en este Mac. Instálalo (https://ollama.com/download) o usa --letra-archivo con tu propia letra.")
        print("Arrancando Ollama…", flush=True); subprocess.Popen(cmd, shell=True)
        for _ in range(24):
            time.sleep(5); m = tags()
            if m is not None: break
        if m is None: sys.exit("Ollama no arrancó. Ábrelo a mano (app Ollama) y repite el comando.")
    if not m: sys.exit("Ollama funciona pero no encuentro modelos. Dime dónde están: ejecuta  find /Volumes -maxdepth 4 -name manifests 2>/dev/null  — o usa --letra-archivo con tu propia letra.")
    print("Modelos encontrados:", ", ".join(x["name"] for x in m)[:200]); return m[0]["name"]

def letra_con_ollama(titulo, estilo, idioma, tema, corta, idioma_txt=None, guia=None, rap=False):
    mod = modelo_ollama()
    if not mod: sys.exit("No encuentro Ollama con modelos. Arráncalo (ollama serve) y descarga uno (p. ej. ollama pull llama3.2), o usa --letra-archivo.")
    secc = ("[Verse 1], [Chorus], [Verse 2], [Chorus], [Verse 3], [Outro]" if rap else "[Verse 1], [Chorus], [Verse 2], [Chorus], [Outro]") if corta else "[Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Pre-Chorus], [Chorus], [Bridge], [Chorus], [Outro]"
    pr = (f"Eres un compositor de éxitos virales. Escribe la letra de una canción ORIGINAL titulada «{titulo}», estilo {estilo}, escrita en {idioma_txt or IDIOMAS.get(idioma, idioma)}. "
          f"PETICIÓN DEL CLIENTE (lo más importante: respétala al pie de la letra: nombres, ocasión, detalles y tono): {tema or 'libre, con una historia concreta y emoción real'}.\n"
          "OBJETIVO: una canción con potencial comercial real, de las que la gente repite y comparte; que suene a canción de radio actual del género pedido, no a poema.\n"
          "REGLAS PARA QUE SEA PEGADIZA Y VIRAL:\n"
          "1) La primera línea debe enganchar de golpe (una imagen, una confesión o una pregunta que obligue a seguir escuchando).\n"
          "2) El estribillo es corto (2 a 4 líneas), con una frase gancho fácil de cantar y recordar, que repite el título o su idea; se repite IGUAL cada vez.\n"
          + ("3) RAP REAL: versos largos de 8 a 12 líneas de 12 a 16 sílabas, con rimas internas y encadenadas, flow con cambios de ritmo y punchlines; el estribillo es un hook corto cantado.\n" if rap else "3) Versos de 4 líneas cortas (6 a 9 sílabas), con rima clara y ritmo natural al hablar.\n") +
          "4) Imágenes concretas y sensoriales (lugares, objetos, gestos), emoción real, nada de frases vacías ni clichés.\n"
          "5) Un giro o sorpresa en el puente que cambie el sentido del estribillo.\n"
          "6) Una línea final memorable para el cierre. Sin nombres de artistas reales ni marcas.\n"
          "7) Si la petición nombra a una persona (cumpleaños, amigo, familiar, pareja, homenaje a alguien que ya no está), usa su nombre varias veces, incluido el estribillo, con detalles afectivos concretos; tono alegre si es fiesta, emotivo y luminoso si es recuerdo. No inventes hechos graves ni datos que no te den.\n"
          "8) El título aparece en el estribillo. Evita rimas obvias y palabras de relleno.\n"
          + (f"GUÍA DE ESTILO OBLIGATORIA (la letra debe sonar al género pedido): {guia}\n" if guia else "") + f"Usa estas secciones con sus etiquetas entre corchetes, en este orden: {secc}. Devuelve SOLO la letra, sin explicaciones ni comillas ni comentarios.")
    print(f"Escribiendo la letra con Ollama ({mod})…", flush=True)
    t = ""
    for _intento in range(2):
        r = json.load(u.urlopen(u.Request(OLLAMA + "/api/generate", json.dumps({"model": mod, "prompt": pr, "stream": False, "keep_alive": "30m", "options": {"temperature": 0.9, "num_predict": 1500 if rap else 900}}).encode(), {"Content-Type": "application/json"}), timeout=900))
        t = (r.get("response") or "").strip(); t = re.sub(r"^```\w*\n|```$", "", t).strip()
        if "[" in t: t = t[t.index("["):]  # quita introducciones tipo «Aquí tienes la letra»
        if len(t) >= 60: break
    if "[" not in t: t = "[Verse 1]\n" + t
    if len(t) < 60: sys.exit("Ollama devolvió una letra demasiado corta. Prueba otra vez o usa --letra-archivo.")
    return t

FUENTES = {}  # título -> [(titular, medio, enlace)] usados como inspiración
def _gen(mod, pr, temp=0.9, n=900, t=900):
    r = json.load(u.urlopen(u.Request(OLLAMA + "/api/generate", json.dumps({"model": mod, "prompt": pr, "stream": False, "keep_alive": "30m", "options": {"temperature": temp, "num_predict": n}}).encode(), {"Content-Type": "application/json"}), timeout=t))
    return (r.get("response") or "").strip()
def _solo_letra(t):
    t = re.sub(r"^```\w*\n|```$", "", (t or "").strip()).strip()
    t = t[t.index("["):] if "[" in t else t
    return "\n".join(l for l in (re.sub(r"\*\*|__", "", x).rstrip() for x in t.splitlines()) if not l.strip().startswith(("#", "---", "===")) and not re.match(r"^\s*\*?\s*(g[eé]nero|estilo|t[ií]tulo|genre|style|title|bpm)\s*[:：]", l, re.I))
def actualidad(consulta, n=5):
    """Titulares reales de Google Noticias (gratis, sin clave). Devuelve [(titular, medio, enlace)]; vacío si no hay internet."""
    import urllib.parse, xml.etree.ElementTree as ET
    try:
        x = u.urlopen(u.Request("https://news.google.com/rss/search?q=" + urllib.parse.quote(consulta or "tecnología") + "&hl=es&gl=ES&ceid=ES:es", headers={"User-Agent": "Mozilla/5.0"}), timeout=15).read(); out = []
        for it in ET.fromstring(x).iter("item"):
            tt = (it.findtext("title") or "").strip(); out.append((tt, (it.findtext("source") or "").strip(), (it.findtext("link") or "").strip()))
            if len(out) >= n: break
        return [o for o in out if o[0]]
    except Exception: return []
PROHIBIDAS = "destino, universo, heridas, estrellas, sombras, fuego, alas, infinito, volar, eterno, alma gemela, susurros, latidos, cielo, brillar, sueños, horizonte, llama"

EJEMPLO_ES = ("EJEMPLO DE NIVEL (otra canción; NO copies sus palabras ni su tema, solo aprende el nivel: una metáfora central sostenida, imágenes concretas, rima limpia y sentido claro):\n"
    "El tiempo es un gato viejo que duerme sobre el sillón,\nle acaricio el lomo y ronronea la estación;\n"
    "las horas son migas de pan que el viento no quiere llevar,\ny yo, pajarito de abril, las aprendo a picotear.\n")
def _llave_rima(w):
    """Clave de rima asonante en español: vocal tónica + vocales siguientes."""
    w = re.sub(r"[^a-záéíóúüñ]", "", (w or "").lower())
    if not w: return ""
    g = [m for m in re.finditer(r"[iuü]?[aeoáéó][iuü]?|[áéíóúiuü]", w)]
    if not g: return w[-2:]
    idx = len(g) - 1
    for i, m in enumerate(g):
        if re.search(r"[áéíóú]", m.group()): idx = i; break
    else:
        if len(g) >= 2 and re.search(r"[aeiouns]$", w) and not re.search(r"[áéíóú]", w): idx = len(g) - 2
    def v(grp):
        s = grp.group(); a = re.search(r"[áéíóú]", s)
        s2 = a.group() if a else (re.search(r"[aeo]", s).group() if re.search(r"[aeo]", s) else s[-1])
        return s2.translate(str.maketrans("áéíóúü", "aeiouu"))
    k = v(g[idx]) + "".join(v(x) for x in g[idx + 1:])
    return k.replace("i", "i").replace("u", "u")
def _ult(l):
    p = re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+", l or "")
    return p[-1] if p else ""
def _rima(a, b):
    x, y = _llave_rima(_ult(a)), _llave_rima(_ult(b))
    return bool(x) and x == y and _ult(a).lower() != _ult(b).lower()
def _estrofas(letra):
    """[(etiqueta, [líneas])] por sección."""
    out = []; et = None; ls = []
    for ln in letra.splitlines():
        s = ln.strip()
        if re.match(r"^\[.*\]$", s):
            if et is not None: out.append((et, ls))
            et = s; ls = []
        elif s and et is not None: ls.append(s)
    if et is not None: out.append((et, ls))
    return out
def _bloque_ok(ls):
    if len(ls) < 4: return True
    a, b, c, d = ls[:4]
    return (_rima(a, b) and _rima(c, d)) or (_rima(a, c) and _rima(b, d)) or (_rima(a, d) and _rima(b, c)) or _rima(b, d)
def _puntos(ls):
    if len(ls) < 4: return 9
    a, b, c, d = ls[:4]; return sum([_rima(a, b), _rima(c, d), _rima(a, c), _rima(b, d), _rima(a, d), _rima(b, c)])
def arreglar_rimas(mod, letra, concepto, idioma, intentos=2):
    """Comprueba la rima estrofa a estrofa (español) y reescribe SOLO las que no riman, con palabras que riman reales."""
    if idioma != "es": return letra
    malas = [ls for et, ls in _estrofas(letra) if len(ls) >= 4 and not _bloque_ok(ls)]
    vistas = set(); n = 0
    for ls in malas:
        clave = "\n".join(ls[:4])
        if clave in vistas: continue
        vistas.add(clave); mejor = ls[:4]; pm = _puntos(mejor)
        for _ in range(intentos):
            rimas = _gen(mod, f"Dame 8 palabras en español que rimen (rima asonante o consonante) con «{_ult(mejor[1])}». Responde SOLO con las palabras separadas por comas.", 0.5, 60, 60)
            nuevo = _gen(mod, "Eres un poeta. Reescribe esta estrofa de 4 versos para que RIME de verdad (versos 2 y 4 terminan en palabras que riman entre sí; mejor aún si 1 y 3 también riman). "
                f"Mantén la misma imagen y metáfora, el mismo sentido ({concepto[:160]}) y versos cantables de 6 a 11 sílabas. Palabras que riman con el verso 2, por si te ayudan: {rimas}. No uses: {PROHIBIDAS}. Devuelve SOLO los 4 versos, uno por línea, sin comentarios.\n\nESTROFA:\n" + "\n".join(mejor), 0.8, 200, 200)
            nl = [x.strip() for x in nuevo.splitlines() if x.strip() and not x.strip().startswith("[")][:4]
            if len(nl) == 4 and _puntos(nl) > pm: mejor, pm = nl, _puntos(nl)
            if _bloque_ok(mejor): break
        if mejor != ls[:4]:
            letra = letra.replace("\n".join(ls[:4]), "\n".join(mejor)); n += 1
    if n: print(f"Poeta · Rimas corregidas en {n} estrofa(s).", flush=True)
    return letra

BANCO_ES = """mar cantar soñar andar buscar sembrar mirar llamar quedar callar volar bailar abrazar esperar encontrar olvidar recordar llorar mojar lugar hogar altar azar amar besar dejar pasar contar sanar ganar guardar nadar rezar cuidar alcanzar
volver perder querer tener nacer crecer vencer caer ser ver saber entender tejer correr beber encender mecer atardecer amanecer anochecer renacer merecer padecer
vivir sentir partir decir reír huir subir abrir sufrir morir seguir escribir existir dormir venir fingir latir escupir sacudir
amor dolor color calor flor valor rumor temor sabor fervor resplandor rencor claror candor mayor peor mejor menor sudor vapor favor
sol farol caracol arrebol girasol espejo reflejo viejo consejo lejos
luz cruz voz paz sed red pared pared mes ciudad verdad edad libertad soledad ciudad humildad bondad
ayer mujer placer anochecer querer deber
ado lado pasado costado cuidado dorado cansado soñado amado olvidado callado mojado prado estado enamorado rosado sembrado cerrado
ada nada callada mirada mañana ventana sabana campana lana semana cama llama rama fama pasada alborada madrugada espada nevada tejada enramada jornada orilla
día alegría melodía poesía armonía compañía fantasía travesía sinfonía ironía osadía cobardía agonía lejanía mía tía
corazón canción razón pasión rincón balcón ilusión emoción sillón montón perdón pregón son salón avión limón algodón botón camión
gente mente presente ausente fuente corriente puente ardiente frente simiente vertiente oriente creciente luciente inocente dolente paciente
noche broche coche derroche reproche
cielo suelo vuelo pelo anhelo consuelo hielo velo duelo abuelo desvelo
tiempo viento cuento lento aliento momento invento sustento aposento pensamiento sentimiento movimiento
fuego juego ruego luego ciego sosiego riego
vida herida salida partida perdida huida medida bebida caída dormida despedida comida querida mordida
ola sola cola bola amapola rosa mariposa prosa hermosa preciosa fosa cosa diosa
luna cuna fortuna laguna aceituna ninguna una duna
arena pena cadena melena sirena escena condena serena azucena colmena
playa raya atalaya valla malla
isla brisa risa prisa camisa guirnalda
nube sube tubo
barco charco arco marco charco
sombra nombra alfombra
lluvia ola
raíz feliz cicatriz perdiz matiz nariz raíz
alma calma palma salma
camino destino vecino vino molino pino tino marino cristalino
silencio presencia ausencia paciencia esencia inocencia indulgencia herencia
rio frío río hastío bravío estío tío navío
abril mil sutil febril fácil gentil pretil
corre torre borre
casa brasa masa pasa tasa
pan van afán galán capitán volcán desván
sueño dueño pequeño leño empeño diseño ceño
cantares mares lugares hogares pesares azares
miedo credo ruedo
puerta abierta cierta muerta despierta desierta
tierra guerra sierra cerra encierra destierra
verso universo reverso disperso inverso
palabra labra abra cuadra
hoja roja moja arroja deshoja congoja
ojos antojos rojos enojos despojos
labios agravios sabios rabios
manos hermanos humanos lejanos livianos veranos
besos regresos tropiezos pesos excesos
nieve lleve breve leve mueve
""".split()
def _tonica_ini(w):
    g = [m for m in re.finditer(r"[iuü]?[aeoáéó][iuü]?|[áéíóúiuü]", w)]
    if not g: return 0
    idx = len(g) - 1
    for i, m in enumerate(g):
        if re.search(r"[áéíóú]", m.group()): idx = i; break
    else:
        if len(g) >= 2 and re.search(r"[aeiouns]$", w): idx = len(g) - 2
    s = g[idx]; k = s.start()
    a = re.search(r"[áéíóú]", s.group())
    if a: k = s.start() + s.group().index(a.group())
    elif re.search(r"[aeo]", s.group()): k = s.start() + re.search(r"[aeo]", s.group()).start()
    return k
def _cons(w):
    w = re.sub(r"[^a-záéíóúüñ]", "", w.lower())
    return w[_tonica_ini(w):].translate(str.maketrans("áéíóúü", "aeiouu")) if w else ""
def familias_rima():
    d = {}
    for w in dict.fromkeys(BANCO_ES):
        if len(w) < 3: continue
        c = _cons(w)
        if len(c) >= 2: d.setdefault(c, []).append(w)
    return {k: v for k, v in d.items() if len(v) >= 4}
def _limpia_verso(x, ya):
    x = (x or "").strip().split("\n")[0].strip()
    x = re.sub(r"^[\-\*\d\.\)\s«\"“]+|[»\"”]+$", "", x).strip()
    return x
def _verso_con_fin(mod, contexto, previos, finales, prohib_re, temp=0.9):
    for i in range(4):
        pr = contexto + ("Versos ya escritos de esta estrofa:\n" + "\n".join(previos) + "\n" if previos else "") + \
            "Escribe SOLO el siguiente verso: cantable (de 6 a 11 sílabas), con sentido literal claro, una imagen concreta, español natural, sin comillas ni numeración. " \
            "DEBE terminar exactamente con UNA de estas palabras (elige la que mejor encaje): " + ", ".join(finales) + "."
        v = _limpia_verso(_gen(mod, pr, temp, 60, 60), previos)
        ult = re.sub(r"[^a-záéíóúüñ]", "", _ult(v).lower())
        if v and ult in finales and 3 <= len(v.split()) <= 14 and not prohib_re.search(v) and v not in previos: return v, True
    return v if v else "…", False
def letra_por_versos(mod, titulo, plan, base, secciones, hechos=""):
    fam = familias_rima(); claves = list(fam)
    proh = re.compile(r"\b(" + "|".join(re.escape(x.strip()) for x in PROHIBIDAS.split(",")).replace("volar", "vuel\\w+|volar") + r")\b", re.I)
    print("Poeta 2/3 · Esquema de la historia por estrofas…", flush=True)
    ideas_t = _gen(mod, "Eres un poeta. " + base + "PLAN:\n" + plan + "\n\nEscribe UNA frase por cada sección de la canción diciendo qué pasa o qué se dice en ella, de modo que la historia avance (de la situación al giro final) y el estribillo sea la idea central con un gancho que incluya el título. "
        "Formato exacto, una por línea: «Etiqueta: frase». Secciones en orden: " + ", ".join(secciones) + ".", 0.8, 500, 500)
    ideas = {}
    for ln in ideas_t.splitlines():
        m = re.match(r"^\W*(\[?[A-Za-z\- ]+\d?\]?)\s*:\s*(.+)$", ln.strip())
        if m: ideas.setdefault(m.group(1).strip("[] ").lower(), m.group(2).strip())
    hechas = {}; out = []; usadas = set(); fallos = 0; total = 0
    print("Poeta 3/3 · Escribiendo verso a verso con rimas reales…", flush=True)
    for et in secciones:
        nom = et.strip("[] "); clave = nom.lower()
        if clave in hechas and nom.lower().startswith(("chorus", "outro")):
            out.append((et, hechas[clave])); continue
        n = 2 if nom.lower().startswith(("pre", "outro")) else 4
        if nom.lower().startswith("outro") and "chorus" in hechas: out.append((et, hechas["chorus"][:2])); continue
        cand = random.sample([k for k in claves if k not in usadas], 6) if len([k for k in claves if k not in usadas]) >= 6 else random.sample(claves, 6)
        menu = "\n".join(f"{i+1}) " + ", ".join(random.sample(fam[k], min(6, len(fam[k])))) for i, k in enumerate(cand))
        idea = ideas.get(clave) or ideas.get(re.sub(r"\s*\d+$", "", clave)) or "continúa la historia"
        try:
            el = _gen(mod, f"Idea de la estrofa: {idea}. Tema de la canción: {titulo}. Elige las DOS listas de palabras (por su número) cuyas palabras mejor podrían cerrar versos de esa idea. Responde solo dos números separados por coma.\n{menu}", 0.4, 12, 40)
            nums = [int(x) - 1 for x in re.findall(r"\d", el)][:2]
        except Exception: nums = []
        if len(nums) < 2 or nums[0] == nums[1] or max(nums) >= 6: nums = [0, 1]
        A, B = cand[nums[0]], cand[nums[1]]; usadas.update([A, B])
        esq = ["A", "B", "A", "B"] if n == 4 else ["A", "A"]
        ctx = (f"Eres un poeta y letrista profesional. {base}PLAN DE LA CANCIÓN:\n{plan}\n{hechos}Sección: {et}. Idea de esta estrofa: {idea}\n"
               + (EJEMPLO_ES if True else "") + f"No uses: {PROHIBIDAS}. Mantén UNA metáfora central coherente con el plan.\n")
        ls = []; usados_fin = set()
        for i in range(n):
            f = [w for w in fam[A if esq[i] == "A" else B] if w not in usados_fin] or fam[A if esq[i] == "A" else B]
            if i == 0 and not nom.lower().startswith("chorus"): f = f
            v, ok = _verso_con_fin(mod, ctx, ls, f[:], proh)
            total += 1; fallos += (0 if ok else 1)
            usados_fin.add(re.sub(r"[^a-záéíóúüñ]", "", _ult(v).lower())); ls.append(v)
        hechas[clave] = ls; out.append((et, ls))
    if fallos: print(f"Poeta · {fallos} de {total} versos no pudieron cerrar con la rima pedida.", flush=True)
    return "\n\n".join(et + "\n" + "\n".join(ls) for et, ls in out)

def _clave_gemini():
    k = os.environ.get("GEMINI_API_KEY", "")
    if not k:
        for f in (os.path.join(AQUI, "..", ".env.local"), os.path.join(AQUI, "..", ".env"), os.path.expanduser("~/IslandCrewAI/.env")):
            try:
                for ln in open(f, encoding="utf8"):
                    if ln.startswith("GEMINI_API_KEY="): k = ln.split("=", 1)[1].strip().strip("\"'"); break
            except OSError: pass
            if k: break
    return k
MODELOS_GEMINI = ["gemini-3.5-flash", "gemini-3.7-flash", "gemini-3-flash-preview", "gemini-3.8-flash", "gemini-3.1-flash-lite", "gemini-flash-latest"]
def _gemini(pr, temp=0.95, n=16000):
    k = _clave_gemini()
    if not k: raise RuntimeError("sin clave de Gemini")
    err = None
    for modelo_g in MODELOS_GEMINI:
        try:
            req = u.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{modelo_g}:generateContent", json.dumps({"contents": [{"parts": [{"text": pr}]}], "generationConfig": {"temperature": temp, "maxOutputTokens": n}}).encode(), {"Content-Type": "application/json", "x-goog-api-key": k})
            r = json.load(u.urlopen(req, timeout=60))
            tx = "".join(p.get("text", "") for p in r["candidates"][0]["content"]["parts"] if not p.get("thought")).strip()
            if r["candidates"][0].get("finishReason") not in (None, "STOP"): err = RuntimeError("respuesta cortada: " + str(r["candidates"][0].get("finishReason"))); continue
            if tx: print(f"  (escrito con {modelo_g})", flush=True); return tx
        except Exception as e:
            err = e; continue
    raise RuntimeError(f"Gemini no respondió: {str(err)[:120]}")
MAESTRO_LETRA = """Eres una autora/autor de canciones de nivel Grammy: combinas el oficio de un gran cantautor, la mirada de un poeta y el instinto de hit de un productor de éxito. Tu trabajo se juzga como si compitiera por Canción del Año.

PROCESO (hazlo en silencio antes de escribir):
1. Encuentra la VERDAD EMOCIONAL de la petición: qué siente de verdad quien la canta y por qué importa ahora. Una sola idea central, dicha con precisión.
2. Elige UNA METÁFORA CENTRAL fresca y concreta (un objeto, oficio, lugar o gesto que "hace" de la emoción) y sostenla de principio a fin, desarrollándola en cada estrofa con una imagen nueva (no repitas la misma imagen). Prohibidas las metáforas gastadas.
3. Diseña el arco: Estrofa 1 = escena concreta que sitúa (detalle sensorial específico: un objeto, un olor, un gesto, una hora); Pre-estribillo = tensión que sube; Estribillo = la idea central en pocas palabras, memorable, con el título o su idea; Estrofa 2 = la escena avanza o se complica (no repite la 1); Puente = GIRO o revelación que cambia cómo se oye el estribillo; Final = cierre que resuelve.
4. Estribillo: 2 a 4 líneas, muy cantable, la frase gancho se repite o varía mínimamente; IGUAL cada vez que aparece.

OFICIO:
- RIMA LIMPIA Y NATURAL en cada estrofa (ABAB, AABB o ABBA; consonante cuando suena bien, asonante si es más natural). Nunca fuerces una palabra solo por rimar: si la rima obliga a decir algo vacío, reescribe la frase. Comprueba verso a verso que las palabras que riman rimen de verdad al pronunciarlas.
- PROSODIA: versos de 6 a 11 sílabas, acentos naturales sobre las sílabas fuertes de la melodía, frases que se puedan respirar y cantar. Longitudes parecidas dentro de cada estrofa.
- Muestra, no cuentes: imágenes concretas y sensoriales (objetos, lugares, texturas, olores, gestos, nombres propios de la petición). Cero abstracciones vacías ("destino", "universo", "sueños infinitos"), cero relleno, cero versos que solo expliquen el verso anterior.
- Cada verso se entiende literalmente y aporta algo nuevo. Evita lugares comunes de la canción comercial; busca la frase que nadie ha escrito pero que todos reconocen como verdad.
- Respeta al máximo los datos de la petición (nombres, ocasión, lugar, hechos, tono) y úsalos como detalles reales dentro de las imágenes.
- Voz y registro coherentes de principio a fin (quién habla y a quién).

ANTES DE RESPONDER, REVÍSALA con esta lista y corrige lo que falle: (a) ¿la metáfora central se sostiene sin mezclar imágenes sin relación? (b) ¿riman de verdad todos los pares? (c) ¿el puente cambia el sentido? (d) ¿el estribillo se quedaría pegado? (e) ¿hay algún cliché o verso de relleno? (f) ¿se puede cantar sin tropezar?"""
def _eval_rimas(l, idioma):
    if idioma != "es": return 0
    return sum(1 for et, ls in _estrofas(l) if len(ls) >= 4 and not _bloque_ok(ls))
def letra_gemini(titulo, estilo, idioma, tema, corta, leng, guia, rap, hechos):
    secc = ("[Verse 1], [Chorus], [Verse 2], [Chorus], [Verse 3], [Outro]" if rap else "[Verse 1], [Chorus], [Verse 2], [Chorus], [Outro]") if corta else "[Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Pre-Chorus], [Chorus], [Bridge], [Chorus], [Outro]"
    pr = (MAESTRO_LETRA + f"\n\nENCARGO: letra ORIGINAL titulada «{titulo}», estilo {estilo}, en {leng}.\nPETICIÓN DEL CLIENTE: {tema or 'libre'}.\n" + (hechos or "")
          + ("RAP: versos de 8 a 12 líneas con rimas internas y encadenadas, flow, punchlines y remates; el estribillo es un hook corto cantado.\n" if rap else "")
          + (f"GUÍA DE ESTILO: {guia}.\n" if guia else "") + f"Palabras gastadas prohibidas: {PROHIBIDAS}. Sin nombres de artistas ni marcas.\n"
          f"Etiquetas de sección entre corchetes, en este orden: {secc}. Devuelve SOLO la letra, sin título, notas ni comentarios.")
    etiquetas = [x.strip() for x in secc.split(",")]
    def una(res, k):
        for _i in range(2):
            try: l = _solo_letra(_gemini(pr, 1.0))
            except Exception as ex: res[k] = None; return
            if "[" in l and len(l) >= 60 and etiquetas[-1].lower() in l.lower(): res[k] = l; return
        res[k] = None
    res = {}; ths = [threading.Thread(target=una, args=(res, k), daemon=True) for k in ((0,) if rap else (0, 1))]
    [x.start() for x in ths]; [x.join(240) for x in ths]
    cand = [x for x in (res.get(0), res.get(1)) if x]
    if not cand: raise RuntimeError("letra incompleta")
    l = cand[0]
    if len(cand) == 2:
        try:
            print("Poeta · Dos versiones escritas; el jurado elige la mejor…", flush=True)
            e0, e1 = _eval_rimas(cand[0], idioma), _eval_rimas(cand[1], idioma)
            ver = _gemini("Eres jurado de los premios Grammy a Canción del Año. Compara estas dos letras de la misma petición («" + (tema or titulo)[:200] + "») y elige la mejor según: poesía y originalidad de la metáfora central (y que se sostenga), rima limpia y natural, sentido claro verso a verso, fuerza del estribillo, giro del puente, imágenes concretas sin clichés y cantabilidad. Responde SOLO con el número 1 o 2.\n\nLETRA 1:\n" + cand[0] + "\n\nLETRA 2:\n" + cand[1], 0.2, 2000)
            m = re.search(r"[12]", ver); pick = int(m.group()) - 1 if m else 0
            if idioma == "es" and abs(e0 - e1) >= 2: pick = 0 if e0 < e1 else 1   # si una tiene muchas más estrofas sin rima, gana la otra
            l = cand[pick]
        except Exception: pass
    if idioma == "es":
        for ronda in range(2):
            malas = []
            for et, ls in _estrofas(l):
                if len(ls) >= 4 and not _bloque_ok(ls) and "\n".join(ls[:4]) not in malas: malas.append("\n".join(ls[:4]))
            if not malas: break
            print(f"Poeta · {len(malas)} estrofa(s) sin rima clara; las reescribo.", flush=True)
            fix = _solo_letra(_gemini("Esta letra tiene estrofas que NO riman bien al pronunciarlas. Reescribe la letra COMPLETA igual que está (mismas etiquetas, orden, historia y metáfora), cambiando SOLO los versos necesarios para que estas estrofas rimen de verdad (ABAB/AABB), con sentido claro, manteniendo el estribillo idéntico en cada repetición:\n\nESTROFAS A ARREGLAR:\n" + "\n---\n".join(malas) + "\n\nLETRA COMPLETA:\n" + l + "\n\nDevuelve SOLO la letra completa.", 0.7))
            if "[" in fix and 0.7 * len(l) <= len(fix) <= 1.4 * len(l): l = fix
    return l
CAPTION_PRODUCTOR = """Eres un productor musical ganador de varios Grammy (Producer of the Year) y director de arreglos. Escribe el PROMPT DE PRODUCCIÓN para un modelo de generación de música (ACE-Step). Debe sonar a disco de estudio profesional, auténtico del género, nada genérico.

Devuelve UN solo párrafo en INGLÉS, de 60 a 110 palabras, en forma de etiquetas descriptivas separadas por comas, que concrete:
- subgénero exacto y época/escena de referencia (sin nombrar artistas ni canciones), y el carácter emocional
- tempo/groove (feel, swing, patrón de batería concreto), tonalidad o modo con color armónico (ej. minor with borrowed chords)
- instrumentación ESPECÍFICA y real del género (modelos de sonido: nylon guitar, Rhodes, 808 sub-bass, upright bass, timple, brass section, etc.), con el papel de cada uno
- ARREGLO y dinámica por secciones: intro, verso contenido, pre-estribillo que sube, estribillo grande y abierto con armonías, puente con cambio de textura, final
- voz: timbre, registro, técnica y actitud de interpretación, dobles y coros
- mezcla y master: espacio, profundidad, calidez, graves, estéreo, sin sonar lo-fi ni plano
No incluyas la letra, ni palabras en español, ni títulos, ni explicaciones. Solo el párrafo."""
def caption_gemini(estilos, idioma, tema, letra, voz, acento, bpm, inst, extra=""):
    if os.environ.get("CB_POETA_NUBE", "1") == "0" or not _clave_gemini(): return ""
    pr = (CAPTION_PRODUCTOR + f"\n\nENCARGO: estilo(s): {estilos}. Idioma cantado: {idioma}. Tema: {tema or 'libre'}. Voz pedida: {voz or 'la que mejor encaje'}"
          + (f", acento {acento}" if acento and acento != "neutro" else "") + (f". BPM aproximado: {bpm}" if bpm else "") + (". INSTRUMENTAL (sin voz)." if inst else "")
          + (f"\nExtras pedidos por el cliente: {extra}" if extra else "") + ("\nCarácter de la letra (para ajustar la emoción del arreglo):\n" + letra[:700] if letra and not inst else ""))
    try:
        c = _gemini(pr, 0.8, 3000).replace("\n", " ").strip().strip('"')
        c = re.sub(r"\s+", " ", c)
        return c[:900] if 60 <= len(c) else ""
    except Exception: return ""

def letra_poetica(titulo, estilo, idioma, tema, corta, idioma_txt=None, guia=None, rap=False, con_actualidad=False):
    """Letra en 3 pasadas: 1) concepto + banco de imágenes, 2) borrador, 3) edición crítica. Opcional: titulares reales como inspiración (sin inventar datos)."""
    mod = modelo_ollama()
    if not mod: sys.exit("No encuentro Ollama con modelos.")
    leng = idioma_txt or IDIOMAS.get(idioma, idioma); hechos = ""; FUENTES.pop(titulo, None)
    if con_actualidad:
        kw = _gen(mod, f"Dame de 2 a 4 palabras clave para buscar noticias actuales relacionadas con esta idea de canción: «{tema or titulo}». Responde SOLO con las palabras, sin comillas.", 0.3, 20, 120).split("\n")[0].strip(" \"«».") or "tecnología"
        fu = actualidad(kw)
        if fu:
            FUENTES[titulo] = fu; print(f"Actualidad ({kw}): {len(fu)} titulares reales.", flush=True)
            hechos = "HECHOS REALES DE HOY (titulares tal como los publican los medios; úsalos solo como inspiración, convertidos en imagen o metáfora; NO añadas datos, cifras ni declaraciones que no estén aquí):\n" + "\n".join(f"- {a} ({b})" for a, b, _ in fu) + "\n"
    if os.environ.get("CB_POETA_NUBE", "1") != "0" and _clave_gemini():
        try:
            print("Poeta · Escribiendo con Gemini gratuito (mucho mejor poesía)…", flush=True)
            return letra_gemini(titulo, estilo, idioma, tema, corta, leng, guia, rap, hechos)
        except Exception as _e: print("Poeta · Gemini no disponible (" + str(_e)[:100] + "); uso el modelo local.", flush=True)
    secc = ("[Verse 1], [Chorus], [Verse 2], [Chorus], [Verse 3], [Outro]" if rap else "[Verse 1], [Chorus], [Verse 2], [Chorus], [Outro]") if corta else "[Verse 1], [Pre-Chorus], [Chorus], [Verse 2], [Pre-Chorus], [Chorus], [Bridge], [Chorus], [Outro]"
    base = f"Canción ORIGINAL titulada «{titulo}», estilo {estilo}, en {leng}. PETICIÓN DEL CLIENTE (respétala: nombres, ocasión, detalles, tono): {tema or 'libre'}.\n"
    print("Poeta 1/3 · Pensando qué quiere decir la canción y reuniendo imágenes…", flush=True)
    plan = _gen(mod, "Eres un poeta y letrista profesional. Todavía NO escribas versos. " + base + hechos +
        "Responde con este formato breve (máximo 250 palabras):\nCONCEPTO: qué quiere decir (una frase)\nPUNTO DE VISTA: quién habla y a quién\nIDEA DEL ESTRIBILLO: la frase gancho\nEL OYENTE SIENTE: ...\nIMÁGENES (8): objetos, lugares y gestos concretos y sensoriales, nada abstracto\nMETÁFORAS NUEVAS (5): una idea abstracta convertida en algo de la vida actual (pantallas, notificaciones, ciudad, trabajo, dinero, tiempo), con una comparación que no sea un cliché\n"
        f"Prohibido usar: {PROHIBIDAS}.", 0.95, 600)
    if idioma == "es" and not rap:
        try:
            sec_l = [x.strip() for x in secc.split(",")]
            v2 = letra_por_versos(mod, titulo, plan, base, sec_l, hechos)
            if len(v2) > 80: return v2
        except Exception as _e: print("Poeta · el método por versos falló, uso el normal:", _e, flush=True)
    print("Poeta 2/3 · Escribiendo el borrador…", flush=True)
    reglas = ("RAP: versos de 8 a 12 líneas de 12 a 16 sílabas, rimas internas y encadenadas, cadencia con silencios y remates; el estribillo es un hook corto." if rap else "Versos de 4 líneas cantables (6 a 10 sílabas), rima natural (consonante, asonante o interna, sin forzarla), acentos naturales del idioma.")
    bor = _solo_letra(_gen(mod, "Eres un poeta y letrista profesional. Con este plan, escribe la letra completa.\n" + base + "PLAN:\n" + plan + "\n"
        + (EJEMPLO_ES + "\n" if idioma == "es" else "") + "REGLAS: RIMA OBLIGATORIA en español (versos pares riman entre sí, mejor ABAB o AABB con rima limpia); UNA METÁFORA CENTRAL que se mantiene en toda la canción y se desarrolla (no metáforas sueltas sin relación); cada verso tiene sentido literal claro; empieza por tener algo que decir, no por rimar; la primera línea engancha; los versos cuentan una historia que avanza (no repiten el estribillo); el estribillo es corto (2 a 4 líneas), memorable, repite el título o su idea y es IGUAL cada vez; el puente trae una revelación o un giro; imágenes concretas en vez de frases profundas vacías; ningún verso de relleno; sin nombres de artistas ni marcas. "
        + reglas + (f" GUÍA DE ESTILO: {guia}." if guia else "") + f" Prohibido: {PROHIBIDAS}. Etiquetas entre corchetes en este orden: {secc}. Devuelve SOLO la letra.", 0.9, 1500 if rap else 900))
    if len(bor) < 60 or "[" not in bor: print("El borrador salió corto; uso el método normal.", flush=True); return letra_con_ollama(titulo, estilo, idioma, tema, corta, idioma_txt, guia, rap)
    print("Poeta 3/3 · Editor crítico: quitando clichés y versos flojos…", flush=True)
    ed = _solo_letra(_gen(mod, "Eres un editor literario exigente. Esta es una letra BORRADOR. Mejórala: cambia clichés y frases genéricas por imágenes concretas, elimina versos de relleno, sustituye abstracciones por escenas, comprueba que se pueda cantar con fluidez, y no fuerces rimas. "
        f"Mantén exactamente las mismas etiquetas de sección y su orden, el estribillo igual en cada repetición y el título dentro del estribillo; no cambies la longitud más de un 10 %. Prohibido: {PROHIBIDAS}. Devuelve SOLO la letra final, sin comentarios.\n\nLETRA:\n" + bor, 0.7, 1500 if rap else 900))
    fin = ed if ("[" in ed and 0.6 * len(bor) <= len(ed) <= 1.5 * len(bor)) else bor
    try: fin = arreglar_rimas(mod, fin, plan, idioma)
    except Exception as _e: print("Poeta · no pude revisar las rimas:", _e, flush=True)
    malas = sorted({m.lower() for m in re.findall(r"\b(" + "|".join(re.escape(x.strip()) for x in PROHIBIDAS.split(",")).replace("volar", "vuel\\w+|volar") + r")\b", fin, re.I)})
    if malas:
        print("Poeta · Cambiando palabras gastadas:", ", ".join(malas), flush=True)
        r2 = _solo_letra(_gen(mod, f"Reescribe SOLO los versos de esta letra que contengan estas palabras gastadas: {', '.join(malas)}. Sustitúyelas por imágenes concretas y nuevas (objetos, lugares, gestos), sin cambiar el sentido, la rima, las etiquetas ni el resto de versos. Devuelve la letra completa.\n\nLETRA:\n" + fin, 0.7, 1500 if rap else 900))
        if "[" in r2 and 0.8 * len(fin) <= len(r2) <= 1.25 * len(fin): fin = r2
    return fin

def preguntar(txt, defecto=""):
    r = input(f"{txt}" + (f" [{defecto}]" if defecto else "") + ": ").strip()
    return r or defecto

def main():
    ap = argparse.ArgumentParser(description="Crea una canción en tu Mac sin la web.")
    ap.add_argument("--titulo"); ap.add_argument("--estilo", help="uno de: " + ", ".join(ESTILOS) + " (o texto libre)"); ap.add_argument("--idioma", choices=list(IDIOMAS))
    ap.add_argument("--tema"); ap.add_argument("--letra-archivo"); ap.add_argument("--letra-ia", action="store_true"); ap.add_argument("--instrumental", action="store_true")
    ap.add_argument("--duracion", type=int, help="segundos (20-240); por defecto 120"); ap.add_argument("--bpm", type=int); ap.add_argument("--n", type=int, default=1, help="cuántas versiones distintas")
    a = ap.parse_args()
    inter = not (a.titulo and a.estilo)
    titulo = a.titulo or preguntar("Título de la canción", "Sin título " + time.strftime("%H%M"))
    estilo = a.estilo or preguntar("Estilo (" + ", ".join(ESTILOS) + " o texto libre)", "pop")
    idioma = a.idioma or (preguntar("Idioma (" + ", ".join(IDIOMAS) + ")", "es") if inter else "es")
    tema = a.tema if a.tema is not None else (preguntar("Tema o idea (opcional)") if inter else "")
    duracion = min(240, max(20, a.duracion or 120)); bpm = a.bpm or 0
    if a.letra_archivo: letra = open(os.path.expanduser(a.letra_archivo), encoding="utf8").read().strip()
    elif a.instrumental: letra = "[Instrumental]"
    elif a.letra_ia or (inter and preguntar("¿Escribo la letra con IA local (Ollama)? s/n", "s").lower().startswith("s")): letra = letra_con_ollama(titulo, estilo, idioma, tema, duracion <= 100)
    else: sys.exit("Falta la letra: usa --letra-ia, --letra-archivo o --instrumental.")
    tags = ESTILOS.get(estilo.lower(), estilo)
    spec = importlib.util.spec_from_file_location("fm", os.path.join(AQUI, "fabrica-musica.py")); fm = importlib.util.module_from_spec(spec); spec.loader.exec_module(fm)
    if fm.SALIDA.startswith("/Volumes/") and not os.path.isdir("/".join(fm.SALIDA.split("/")[:3])): sys.exit("El disco T5 EVO no está conectado: conéctalo (o define MUSICA_DIR).")
    asegurar_acestep()
    ok = 0
    for i in range(1, a.n + 1):
        pet = {"prompt": ". ".join(x for x in [tags, (f"{bpm} BPM" if bpm else ""), "instrumental, sin voz" if a.instrumental else "", f"idioma {IDIOMAS.get(idioma, idioma)}", tema] if x), "lyrics": letra, "vocal_language": idioma,
               "audio_duration": duracion, "thinking": False, "audio_format": "wav", "batch_size": 1, "seed": random.randint(1, 2**31 - 1), "use_random_seed": False,
               "meta": {"titulo": titulo if a.n == 1 else f"{titulo} (v{i})", "estilo": estilo.lower().replace(" ", "-")[:30], "formato": "cancion", "idioma": idioma, "marca": ""}}
        if bpm: pet["bpm"] = bpm
        if fm.generar(pet, f"{i}/{a.n}"): ok += 1; salida(fm.ULTIMA_RUTA, pet["meta"]["titulo"], estilo, idioma)
    print(f"\nHecho: {ok}/{a.n} canciones en {fm.SALIDA}")

def salida(ruta, titulo, estilo, idioma):
    if not ruta or not os.path.exists(ruta): return
    mp3 = ruta[:-4] + ".mp3"
    if shutil.which("ffmpeg") and not os.path.exists(mp3):
        import tempfile; d = tempfile.mkdtemp(prefix="cl-")  # macOS puede negar ffmpeg en discos externos: se convierte en local y se copia
        try:
            shutil.copyfile(ruta, d + "/a.wav")
            if subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", d + "/a.wav", "-codec:a", "libmp3lame", "-b:a", "192k", d + "/a.mp3"]).returncode == 0: shutil.copyfile(d + "/a.mp3", mp3)
        finally: shutil.rmtree(d, ignore_errors=True)
    ficha = ruta[:-4] + "-ficha.txt"
    open(ficha, "w", encoding="utf8").write(f"Título: {titulo}\nEstilo: {estilo} · Idioma: {idioma}\nCreada: {time.strftime('%d/%m/%Y %H:%M')}\nCreación asistida por IA · Maximiliano Olmos Sánchez · Island Crew\n"
        "Todos los derechos reservados. Para usarla: hola@islandcrew.es\nNº de pieza y de licencia: pendientes (se asignan al registrarla en la web de Island Crew).\n")
    print("Audio:", mp3 if os.path.exists(mp3) else ruta, "\nFicha:", ficha)

if __name__ == "__main__": main()
