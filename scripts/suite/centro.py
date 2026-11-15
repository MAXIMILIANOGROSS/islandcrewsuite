"""Island Crew Intelligence Center · calcula métricas REALES leyendo los ficheros de los programas.
No inventa nada: lo que no se registra se marca como «sin datos». Compatible con Python 3.9+."""
import os, re, json, time, glob, datetime
import core
from centro_txt import TX

_D = {t[0]: t[1:] for t in TX}
_IDX = {"es": -1, "en": 0, "it": 1, "de": 2}


def codigo():
    try:
        import marca
        c = marca.codigo()
    except Exception: c = "es"
    return c if c in _IDX else "es"


def t(s):
    i = _IDX[codigo()]
    return s if i < 0 else (_D.get(s) or [s, s, s])[i] or s


def L(es, en, it, de):
    return (es, en, it, de)[{"es": 0, "en": 1, "it": 2, "de": 3}[codigo()]]


def diccionario():
    """Para la pantalla: español → idioma elegido."""
    i = _IDX[codigo()]
    return {} if i < 0 else {k: v[i] for k, v in _D.items()}


# ---------------------------------------------------------------- lectura de ficheros
def _j(p, d=None):
    try: return json.load(open(p, encoding="utf8"))
    except Exception: return d


def _iso(s):
    try: return datetime.datetime.fromisoformat(str(s).replace(" ", "T")[:19]).timestamp()
    except Exception: return None


def _id_ts(i):
    """Los identificadores de plato llevan la hora de creación en base 36: se usa solo como ESTIMACIÓN."""
    try:
        v = int(str(i)[1:9], 36) / 1000.0
        return v if 1.7e9 < v < 2.2e9 else None
    except Exception: return None


def _musica(d):
    base = os.path.join(d, "musica"); out = {}
    try: nombres = os.listdir(base)
    except Exception: nombres = []
    for n in nombres:
        m = re.match(r"^(\d{8})-(\d{6})_(.+)$", n)
        if not m: continue
        stem = re.sub(r"\.(wav|mp3|mp4|jpg|json|txt)$", "", m.group(3)); low = stem.lower()
        k = "audiolibro" if low.startswith("audiolibro") else "jingle" if "jingle" in low else "cancion" if "cancion" in low else "otra"
        key = m.group(1) + m.group(2) + "_" + stem
        try: ts = time.mktime(time.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M%S"))
        except Exception: continue
        out.setdefault(key, {"key": key, "k": k, "t": ts, "n": stem.replace("_", " ")})
    lib = _j(os.path.join(base, "biblioteca-local.json"), []) or []
    claves = {}
    for x in lib:
        m = re.match(r"^(\d{8})-(\d{6})_(.+)$", str(x.get("archivo", "")))
        if m: claves[m.group(1) + m.group(2) + "_" + re.sub(r"\.(wav|mp3)$", "", m.group(3))] = x
    return list(out.values()), lib, claves


def _cartas(d):
    rs = []
    for f in sorted(glob.glob(os.path.join(d, "cartas", "*", "carta.json"))):
        dr = os.path.dirname(f)
        if os.path.basename(dr).startswith("_"): continue
        c = _j(f, {}) or {}
        vids = {}
        for v in glob.glob(os.path.join(dr, "videos", "*.mp4")):
            if not os.path.basename(v).startswith("_"): vids[os.path.basename(v)] = os.path.getmtime(v)
        platos = c.get("platos", []) or []
        con_video = [p for p in platos if p.get("video") in vids]
        ult = max([os.path.getmtime(f)] + list(vids.values()))
        rs.append({"id": os.path.basename(dr), "nombre": c.get("nombre") or os.path.basename(dr), "platos": platos, "vids": vids, "con_video": con_video,
                   "web": os.path.exists(os.path.join(dr, "web", "index.html")), "qr": os.path.exists(os.path.join(dr, "QR-carta.png")), "url": bool((c.get("url_publica") or "").strip()), "ult": ult,
                   "posts": (_j(os.path.join(dr, "publicaciones.json"), {}) or {}).get("posts", [])})
    return rs


def _anuncios():
    h = _j(os.path.join(core.carpeta_config(), "anuncios-historial.json"), []) or []
    return [{"t": _iso(x.get("fecha")), "n": x.get("titular") or "", "r": x.get("restaurante") or ""} for x in h if _iso(x.get("fecha"))]


# ---------------------------------------------------------------- periodos
def periodo(clave, d1=None, d2=None):
    ahora = time.time(); hoy = datetime.date.today()
    def ep(d): return time.mktime(d.timetuple())
    def mes(a, m):
        while m < 1: a -= 1; m += 12
        while m > 12: a += 1; m -= 12
        return datetime.date(a, m, 1)
    if clave == "hoy": a, b = ep(hoy), ahora; pa, pb = a - 86400, a
    elif clave == "7d": a, b = ahora - 7 * 86400, ahora; pa, pb = a - 7 * 86400, a
    elif clave == "mes": ini = mes(hoy.year, hoy.month); a, b = ep(ini), ahora; pa, pb = ep(mes(ini.year, ini.month - 1)), ep(ini)
    elif clave == "mes_ant": ini = mes(hoy.year, hoy.month - 1); a, b = ep(ini), ep(mes(hoy.year, hoy.month)); pa, pb = ep(mes(ini.year, ini.month - 1)), ep(ini)
    elif clave == "trim":
        q = (hoy.month - 1) // 3 * 3 + 1; ini = datetime.date(hoy.year, q, 1); a, b = ep(ini), ahora; pa, pb = ep(mes(ini.year, ini.month - 3)), ep(ini)
    elif clave == "anio": ini = datetime.date(hoy.year, 1, 1); a, b = ep(ini), ahora; pa, pb = ep(datetime.date(hoy.year - 1, 1, 1)), ep(ini)
    elif clave == "custom":
        try: a = ep(datetime.date.fromisoformat(d1)); b = ep(datetime.date.fromisoformat(d2)) + 86400
        except Exception: a, b = ahora - 30 * 86400, ahora
        if b <= a: b = a + 86400
        pa, pb = a - (b - a), a
    else: a, b = ahora - 30 * 86400, ahora; pa, pb = a - 30 * 86400, a
    return a, b, pa, pb


def _cubos(a, b):
    dias = (b - a) / 86400.0
    if dias <= 35: paso, fmt = 86400, "%d/%m"
    elif dias <= 140: paso, fmt = 7 * 86400, "%d/%m"
    else: paso, fmt = None, "%m/%y"
    cubos = []
    if paso:
        x = a
        while x < b: cubos.append((x, min(x + paso, b), time.strftime(fmt, time.localtime(x)))); x += paso
    else:
        d0 = datetime.date.fromtimestamp(a).replace(day=1)
        while time.mktime(d0.timetuple()) < b:
            n = datetime.date(d0.year + (d0.month == 12), d0.month % 12 + 1, 1)
            cubos.append((time.mktime(d0.timetuple()), time.mktime(n.timetuple()), d0.strftime(fmt))); d0 = n
    return cubos


def _por_mes(ts, n=12):
    hoy = datetime.date.today(); out = []
    for i in range(n - 1, -1, -1):
        m = hoy.month - i; a = hoy.year
        while m < 1: m += 12; a -= 1
        out.append((a, m))
    cnt = {k: 0 for k in out}
    for x in ts:
        if x is None: continue
        d = datetime.date.fromtimestamp(x)
        if (d.year, d.month) in cnt: cnt[(d.year, d.month)] += 1
    return [{"x": "%02d/%02d" % (m, a % 100), "v": cnt[(a, m)]} for a, m in out]


# ---------------------------------------------------------------- finanzas (manuales)
def finanzas_ruta(): return os.path.join(core.carpeta_datos(), "finanzas.json")
def finanzas_leer(): return _j(finanzas_ruta(), []) or []


def finanzas_guardar(lista):
    json.dump(lista, open(finanzas_ruta(), "w", encoding="utf8"), ensure_ascii=False, indent=1)


def finanzas_calc(a, b, pa, pb):
    f = finanzas_leer(); r = {"hay": bool(f), "por_unidad": {}, "mensual": {}, "recurrente": 0.0, "movs": f}
    for u in ("musica", "carta", "social", "general"): r["por_unidad"][u] = {"ing": 0.0, "gas": 0.0, "ing_ant": 0.0, "gas_ant": 0.0}
    for x in f:
        ts = _iso(x.get("fecha")); u = x.get("unidad") if x.get("unidad") in r["por_unidad"] else "general"
        try: imp = float(x.get("importe") or 0)
        except Exception: continue
        ing = x.get("tipo") == "ingreso"
        if ts is not None and a <= ts < b: r["por_unidad"][u]["ing" if ing else "gas"] += imp
        if ts is not None and pa <= ts < pb: r["por_unidad"][u]["ing_ant" if ing else "gas_ant"] += imp
        if ts is not None:
            k = time.strftime("%Y-%m", time.localtime(ts)); r["mensual"][k] = r["mensual"].get(k, 0.0) + (imp if ing else -imp)
        if ing and x.get("categoria") == "Suscripciones" and ts is not None and a <= ts < b: r["recurrente"] += imp
    return r


# ---------------------------------------------------------------- cálculo principal
def calcular(clave="30d", d1=None, d2=None, activos=None):
    activos = activos or {}
    d = core.carpeta_datos(); a, b, pa, pb = periodo(clave, d1, d2); ahora = time.time()
    stems, lib, claves = _musica(d); cartas = _cartas(d); anuncios = _anuncios()
    reg = {"musica": [], "carta": [], "social": []}

    # ---- Cabra Beats
    comp = {"cancion": 0, "jingle": 0, "audiolibro": 0, "otra": 0}; est = {"yt": 0, "ficha": 0, "solo": 0, "audio": 0}
    nombre_k = {"cancion": t("Canciones"), "jingle": t("Jingles"), "audiolibro": t("Audiolibros"), "otra": t("Otras pistas")}
    estilos = {}
    for s in stems:
        comp[s["k"]] += 1; x = claves.get(s["key"])
        if s["k"] == "audiolibro": e = t("Audiolibro"); est["audio"] += 1
        elif x: e = t("En YouTube") if x.get("youtube") else t("Con ficha, sin subir"); est["yt" if x.get("youtube") else "ficha"] += 1
        else: e = t("Solo archivo, sin ficha"); est["solo"] += 1
        if x and x.get("estilo"): estilos[x["estilo"]] = estilos.get(x["estilo"], 0) + 1
        reg["musica"].append({"n": (x or {}).get("titulo") or s["n"], "k": nombre_k[s["k"]], "e": e, "t": s["t"], "x": (x or {}).get("estilo", "")})
    prod = [s for s in stems if s["k"] != "audiolibro"]; con_ficha = est["yt"] + est["ficha"]
    mus_ev = [s["t"] for s in stems]
    musica = {
        "kpi": [{"l": t("Producciones generadas"), "v": len(prod)}, {"l": t("Canciones"), "v": comp["cancion"]}, {"l": t("Jingles"), "v": comp["jingle"]}, {"l": t("Audiolibros"), "v": comp["audiolibro"]},
                {"l": t("Con ficha en la biblioteca"), "v": con_ficha}, {"l": t("En YouTube"), "v": est["yt"]}],
        "donut_estado": {"t": t("Estado de las producciones"), "d": [{"l": t("En YouTube"), "v": est["yt"], "c": "#3ddc97", "f": ["e", t("En YouTube")]}, {"l": t("Con ficha, sin subir"), "v": est["ficha"], "c": "#ffb020", "f": ["e", t("Con ficha, sin subir")]},
                         {"l": t("Solo archivo, sin ficha"), "v": est["solo"], "c": "#7d8aa3", "f": ["e", t("Solo archivo, sin ficha")]}, {"l": t("Audiolibro"), "v": est["audio"], "c": "#b07bff", "f": ["e", t("Audiolibro")]}]},
        "donut_cat": {"t": t("Composición del catálogo"), "d": [{"l": nombre_k[k], "v": comp[k], "c": c, "f": ["k", nombre_k[k]]} for k, c in (("cancion", "#ffb020"), ("jingle", "#ff7a3d"), ("audiolibro", "#b07bff"), ("otra", "#7d8aa3"))]},
        "barras": {"t": t("Producciones por mes"), "d": _por_mes(mus_ev)},
        "embudo": {"t": t("Embudo de producción"), "d": [{"l": t("Producciones generadas"), "v": len(prod)}, {"l": t("Con ficha en la biblioteca"), "v": con_ficha}, {"l": t("En YouTube"), "v": est["yt"]}], "nota": t("Las fases de mezcla, masterización, aprobación y entrega todavía no se registran: no se muestran para no inventarlas.")},
        "ranking": {"t": t("Estilos más usados"), "d": [{"l": k, "v": v} for k, v in sorted(estilos.items(), key=lambda z: -z[1])[:6]]},
        "anillo": {"pct": (100.0 * est["yt"] / len(lib)) if lib else None, "l": t("En YouTube")},
    }

    # ---- Carta Viva
    n_rest = len(cartas); con_platos = [r for r in cartas if r["platos"]]; tot_platos = sum(len(r["platos"]) for r in cartas); tot_vid = sum(len(r["vids"]) for r in cartas)
    activos30 = [r for r in con_platos if ahora - r["ult"] < 30 * 86400]; inact = [r for r in con_platos if r not in activos30]
    n_web = len([r for r in cartas if r["web"]]); n_qr = len([r for r in cartas if r["qr"]]); n_url = len([r for r in cartas if r["url"]])
    completa = [r for r in cartas if r["web"] and r["url"]]; web_sin = [r for r in cartas if r["web"] and not r["url"]]; sin_gen = [r for r in cartas if not r["web"]]
    reg_est = {}
    for r in cartas:
        e = t("Sin platos") if not r["platos"] else (t("Activos (30 días)") if r in activos30 else t("Inactivos"))
        reg["carta"].append({"n": r["nombre"], "k": t("Restaurantes"), "e": e, "t": r["ult"], "x": "%d %s · %d %s" % (len(r["platos"]), t("Platos"), len(r["vids"]), t("Vídeos creados"))})
    for r in cartas:
        for p in r["platos"]:
            reg["carta"].append({"n": p.get("nombre") or "", "k": t("Platos"), "e": t("Vídeos creados") if p in r["con_video"] else t("Pendientes"), "t": r["vids"].get(p.get("video")) or _id_ts(p.get("id")) or r["ult"], "x": r["nombre"]})
    vid_ts = [x for r in cartas for x in r["vids"].values()]; plato_ts = [_id_ts(p.get("id")) for r in cartas for p in r["platos"]]
    rank = sorted(cartas, key=lambda r: -(len(r["platos"]) + len(r["vids"])))[:6]
    carta = {
        "kpi": [{"l": t("Restaurantes"), "v": n_rest}, {"l": t("Activos (30 días)"), "v": len(activos30)}, {"l": t("Con platos (carta creada)"), "v": len(con_platos)}, {"l": t("Platos"), "v": tot_platos},
                {"l": t("Vídeos creados"), "v": tot_vid}, {"l": t("Cartas generadas"), "v": n_web}, {"l": t("Con QR creado"), "v": n_qr}, {"l": t("Pendientes"), "v": tot_platos - sum(len(r["con_video"]) for r in cartas)}],
        "donut_estado": {"t": t("Estado de los restaurantes"), "d": [{"l": t("Activos (30 días)"), "v": len(activos30), "c": "#3fbf7f", "f": ["e", t("Activos (30 días)")]}, {"l": t("Inactivos"), "v": len(inact), "c": "#ffb020", "f": ["e", t("Inactivos")]}, {"l": t("Sin platos"), "v": n_rest - len(con_platos), "c": "#7d8aa3", "f": ["e", t("Sin platos")]}]},
        "donut_cat": {"t": t("Estado de las cartas"), "d": [{"l": t("Carta completa con dirección"), "v": len(completa), "c": "#3fbf7f"}, {"l": t("Carta generada sin dirección"), "v": len(web_sin), "c": "#2ec4b6"}, {"l": t("Carta sin generar"), "v": len(sin_gen), "c": "#7d8aa3"}]},
        "barras": {"t": t("Vídeos creados por mes"), "d": _por_mes(vid_ts)}, "barras2": {"t": t("Platos creados por mes (estimado por su identificador)"), "d": _por_mes(plato_ts)},
        "embudo": {"t": t("Implantación del restaurante"), "d": [{"l": t("Restaurantes"), "v": n_rest}, {"l": t("Con platos (carta creada)"), "v": len(con_platos)}, {"l": t("Vídeos creados"), "v": len([r for r in cartas if r["platos"] and len(r["con_video"]) == len(r["platos"])])},
                   {"l": t("Cartas generadas"), "v": n_web}, {"l": t("Con dirección pública"), "v": n_url}], "nota": t("Escaneos de QR y visitas a la carta: no se registran todavía. No se asume que los QR se escaneen.")},
        "ranking": {"t": t("Restaurantes más activos"), "d": [{"l": r["nombre"], "v": len(r["platos"]) + len(r["vids"])} for r in rank]},
        "anillo": {"pct": (100.0 * sum(len(r["con_video"]) for r in cartas) / tot_platos) if tot_platos else None, "l": t("Avance de la carta (platos con vídeo)")},
    }

    # ---- Cabra Social (Publicaciones + Anuncios)
    posts = [(r["nombre"], p) for r in cartas for p in r["posts"]]; hoy_s = datetime.date.today().isoformat()
    ests = {"borrador": 0, "listo": 0, "publicado": 0}; tipos = {}; atras = []; por_rest = {}
    nombre_e = {"borrador": t("Borrador"), "listo": t("Listo"), "publicado": t("Publicado")}
    for rn, p in posts:
        e = p.get("estado") if p.get("estado") in ests else "borrador"; ests[e] += 1; tipos[p.get("tipo") or "—"] = tipos.get(p.get("tipo") or "—", 0) + 1; por_rest[rn] = por_rest.get(rn, 0) + 1
        if e != "publicado" and str(p.get("fecha") or "9") < hoy_s: atras.append((rn, p))
        reg["social"].append({"n": (p.get("texto") or p.get("tipo") or "")[:90] or (p.get("tipo") or ""), "k": p.get("tipo") or t("Publicaciones planificadas"), "e": nombre_e[e], "t": _iso(p.get("fecha")) or 0, "x": rn})
    for x in anuncios: reg["social"].append({"n": x["n"] or "—", "k": t("Anuncios creados"), "e": t("Anuncios creados"), "t": x["t"], "x": x["r"]})
    pl = len(posts); lis = ests["listo"] + ests["publicado"]; pub = ests["publicado"]
    mes_posts = [_iso(p.get("fecha")) for _, p in posts]
    social = {
        "kpi": [{"l": t("Publicaciones planificadas"), "v": pl}, {"l": t("Publicaciones listas"), "v": lis}, {"l": t("Publicaciones publicadas"), "v": pub}, {"l": t("Pendientes"), "v": pl - pub}, {"l": t("Anuncios creados"), "v": len(anuncios)}],
        "donut_estado": {"t": t("Cola de publicaciones"), "d": [{"l": nombre_e[k], "v": ests[k], "c": c, "f": ["e", nombre_e[k]]} for k, c in (("publicado", "#3ddc97"), ("listo", "#4aa8ff"), ("borrador", "#7d8aa3"))]},
        "donut_cat": {"t": t("Tipos de contenido"), "d": [{"l": k, "v": v, "c": c, "f": ["k", k]} for (k, v), c in zip(sorted(tipos.items(), key=lambda z: -z[1])[:6], ("#4aa8ff", "#00d4ff", "#7aa2ff", "#2ec4b6", "#a0c4ff", "#6c8cff"))]},
        "barras": {"t": t("Publicaciones por mes (fecha planificada)"), "d": _por_mes(mes_posts)}, "barras2": {"t": t("Anuncios por mes"), "d": _por_mes([x["t"] for x in anuncios])},
        "embudo": {"t": t("Embudo de publicaciones"), "d": [{"l": t("Publicaciones planificadas"), "v": pl}, {"l": t("Publicaciones listas"), "v": lis}, {"l": t("Publicaciones publicadas"), "v": pub}],
                   "nota": t("Alcance, impresiones, interacción, clics y clientes potenciales: no hay cuentas sociales conectadas, así que no hay datos de audiencia. Aquí solo se mide producción de contenido.")},
        "ranking": {"t": t("Restaurantes con más publicaciones"), "d": [{"l": k, "v": v} for k, v in sorted(por_rest.items(), key=lambda z: -z[1])[:6]]},
        "anillo": {"pct": (100.0 * pub / pl) if pl else None, "l": t("Publicaciones publicadas")},
    }

    # ---- actividad por periodo (eventos con fecha real)
    ev = {"musica": mus_ev, "carta": vid_ts, "social": [x["t"] for x in anuncios]}
    def cuenta(lst, x, y): return len([v for v in lst if v is not None and x <= v < y])
    cub = _cubos(a, b)
    comp_u = {}
    for u, lst in ev.items():
        cur, ant = cuenta(lst, a, b), cuenta(lst, pa, pb)
        comp_u[u] = {"act": cur, "ant": ant, "var": (100.0 * (cur - ant) / ant) if ant else None}
        {"musica": musica, "carta": carta, "social": social}[u]["linea"] = {"t": t("Actividad en el periodo"), "d": [{"x": c[2], "v": cuenta(lst, c[0], c[1])} for c in cub]}
    pend = {"musica": est["ficha"], "carta": tot_platos - sum(len(r["con_video"]) for r in cartas), "social": pl - pub}
    comp_ok = {"musica": est["yt"], "carta": sum(len(r["con_video"]) for r in cartas), "social": pub + len(anuncios)}
    fin = finanzas_calc(a, b, pa, pb)
    for u in ("musica", "carta", "social"):
        comp_u[u].update({"pend": pend[u], "ok": comp_ok[u], "ing": fin["por_unidad"][u]["ing"] if fin["hay"] else None, "gas": fin["por_unidad"][u]["gas"] if fin["hay"] else None})
        comp_u[u]["ben"] = (comp_u[u]["ing"] - comp_u[u]["gas"]) if fin["hay"] else None
    comp_u["carta"]["clientes"] = len(activos30)

    # ---- globales
    ok_t = sum(comp_ok.values()); pe_t = sum(pend.values()); act_t = sum(comp_u[u]["act"] for u in comp_u); ant_t = sum(comp_u[u]["ant"] for u in comp_u)
    run = [k for k, v in activos.items() if v]
    glob_k = [
        {"id": "assets", "l": t("Activos generados"), "v": tot_vid + len(prod) + len(anuncios) + pl, "d": t("Vídeos de platos + producciones musicales + anuncios + publicaciones generadas."), "s": t("Ficheros de tus programas (carpeta de datos)"), "ty": "real"},
        {"id": "pend", "l": t("Pendientes"), "v": pe_t, "d": t("Platos sin vídeo + publicaciones sin publicar + canciones con ficha sin subir a YouTube."), "s": t("Ficheros de tus programas (carpeta de datos)"), "ty": "real"},
        {"id": "ok", "l": t("Completados"), "v": ok_t, "d": t("Platos con vídeo + publicaciones publicadas + canciones en YouTube + anuncios creados."), "s": t("Ficheros de tus programas (carpeta de datos)"), "ty": "real"},
        {"id": "tasa", "l": t("Tasa de finalización"), "v": round(100.0 * ok_t / (ok_t + pe_t), 1) if (ok_t + pe_t) else None, "u": "%", "d": t("Completados ÷ (completados + pendientes)."), "s": t("Ficheros de tus programas (carpeta de datos)"), "ty": "real"},
        {"id": "act", "l": t("Actividad en el periodo"), "v": act_t, "ant": ant_t, "d": t("Vídeos creados + producciones musicales + anuncios con fecha dentro del periodo."), "s": t("Ficheros de tus programas (carpeta de datos)"), "ty": "real"},
        {"id": "cli", "l": t("Clientes activos"), "v": len(activos30), "d": t("Restaurantes con carta y actividad en los últimos 30 días."), "s": t("Ficheros de tus programas (carpeta de datos)"), "ty": "real"},
        {"id": "run", "l": t("Programas en marcha"), "v": len(run), "d": t("Programas de la suite que están abiertos ahora mismo."), "s": "Suite", "ty": "real"},
    ]
    return {"ahora": ahora, "periodo": {"clave": clave, "a": a, "b": b, "pa": pa, "pb": pb}, "global": glob_k, "unidades": {"musica": musica, "carta": carta, "social": social}, "comparativa": comp_u,
            "registros": {k: sorted(v, key=lambda z: -(z.get("t") or 0))[:400] for k, v in reg.items()}, "finanzas": fin,
            "_h": {"musica": {"stems": len(prod), "lib": len(lib), "yt": est["yt"], "sin_subir": est["ficha"]}, "carta": {"rest": n_rest, "platos": tot_platos, "sin_video": pend["carta"], "inactivos": [r["nombre"] for r in inact], "sin_url": [r["nombre"] for r in web_sin], "act30": len(activos30)},
                   "social": {"pl": pl, "pub": pub, "atras": len(atras), "ads": len(anuncios)}, "ev7": sum(cuenta(ev[u], ahora - 7 * 86400, ahora) for u in ev), "ok": ok_t, "pend": pend}}


# ---------------------------------------------------------------- alertas y analista
def _estado_alertas():
    return _j(os.path.join(core.carpeta_config(), "centro-alertas.json"), {}) or {}


def alertas(c):
    h = c["_h"]; out = []
    def add(n, k, es, en, it, de, ds, den, dit, dde, u=""):
        out.append({"id": k, "nivel": n, "t": L(es, en, it, de), "d": L(ds, den, dit, dde), "u": u})
    cfg = core.carpeta_config(); ahora = time.time()
    for nom, f in (("Carta Viva", "carta-viva-app.py.log"), ("Publicaciones", "publicaciones-app.py.log"), ("Anuncios", "anuncios-app.py.log")):
        p = os.path.join(cfg, f)
        try:
            if os.path.exists(p) and ahora - os.path.getmtime(p) < 86400:
                cola = open(p, "rb").read()[-6000:].decode("utf8", "ignore")
                if "Traceback" in cola: add("critica", "log-" + f, "Error reciente en " + nom, "Recent error in " + nom, "Errore recente in " + nom, "Aktueller Fehler in " + nom, "Hay un error de las últimas 24 horas en el registro del programa.", "There is an error from the last 24 hours in the program log.", "C'è un errore delle ultime 24 ore nel registro del programma.", "Im Programmprotokoll steht ein Fehler der letzten 24 Stunden.")
        except Exception: pass
    if not (core.clave("GEMINI_API_KEY") or core.clave("GROQ_API_KEY")):
        add("aviso", "ia-sin-clave", "No hay clave de IA gratuita", "No free AI key", "Nessuna chiave IA gratuita", "Kein kostenloser KI-Schlüssel", "Sin clave no se pueden traducir las cartas ni escribir textos con IA.", "Without a key, menus cannot be translated and texts cannot be written with AI.", "Senza chiave non si possono tradurre i menù né scrivere testi con IA.", "Ohne Schlüssel können Karten nicht übersetzt und Texte nicht mit KI geschrieben werden.")
    s = h["social"]
    if s["atras"]: add("aviso", "posts-atrasados", "%d publicaciones con la fecha pasada sin publicar" % s["atras"], "%d posts past their date and not published" % s["atras"], "%d post oltre la data e non pubblicati" % s["atras"], "%d Beiträge über dem Datum und nicht veröffentlicht" % s["atras"], "Su fecha planificada ya pasó y siguen sin marcarse como publicadas.", "Their planned date has passed and they are still not marked as published.", "La data pianificata è passata e non sono ancora segnati come pubblicati.", "Das geplante Datum ist vorbei und sie sind noch nicht als veröffentlicht markiert.", "social")
    cv = h["carta"]
    if cv["sin_video"]: add("aviso", "platos-sin-video", "%d platos sin vídeo" % cv["sin_video"], "%d dishes without video" % cv["sin_video"], "%d piatti senza video" % cv["sin_video"], "%d Gerichte ohne Video" % cv["sin_video"], "Contenido pendiente en Carta Viva.", "Pending content in Carta Viva.", "Contenuto in sospeso in Carta Viva.", "Offene Inhalte in Carta Viva.", "carta")
    if cv["inactivos"]: add("aviso", "rest-inactivos", "%d restaurantes sin actividad en 30 días" % len(cv["inactivos"]), "%d restaurants with no activity in 30 days" % len(cv["inactivos"]), "%d ristoranti senza attività da 30 giorni" % len(cv["inactivos"]), "%d Restaurants seit 30 Tagen ohne Aktivität" % len(cv["inactivos"]), ", ".join(cv["inactivos"][:5]), ", ".join(cv["inactivos"][:5]), ", ".join(cv["inactivos"][:5]), ", ".join(cv["inactivos"][:5]), "carta")
    if cv["sin_url"]: add("oportunidad", "carta-sin-url", "%d cartas generadas sin dirección pública" % len(cv["sin_url"]), "%d menus generated without a public address" % len(cv["sin_url"]), "%d menù generati senza indirizzo pubblico" % len(cv["sin_url"]), "%d Karten ohne öffentliche Adresse" % len(cv["sin_url"]), "Sin dirección no se puede crear el QR de la carta: " + ", ".join(cv["sin_url"][:4]), "Without an address the menu QR cannot be created: " + ", ".join(cv["sin_url"][:4]), "Senza indirizzo non si può creare il QR del menù: " + ", ".join(cv["sin_url"][:4]), "Ohne Adresse kann kein QR erstellt werden: " + ", ".join(cv["sin_url"][:4]), "carta")
    m = h["musica"]
    if m["sin_subir"]: add("oportunidad", "musica-sin-subir", "%d canciones con ficha sin subir a YouTube" % m["sin_subir"], "%d songs with a record not uploaded to YouTube" % m["sin_subir"], "%d canzoni con scheda non caricate su YouTube" % m["sin_subir"], "%d Songs mit Eintrag nicht auf YouTube" % m["sin_subir"], "Producción lista que todavía no está publicada.", "Finished production that is not published yet.", "Produzione pronta non ancora pubblicata.", "Fertige Produktion, die noch nicht veröffentlicht ist.", "musica")
    if h["ev7"]: add("info", "nuevos-7d", "%d activos nuevos en 7 días" % h["ev7"], "%d new assets in 7 days" % h["ev7"], "%d nuovi asset in 7 giorni" % h["ev7"], "%d neue Assets in 7 Tagen" % h["ev7"], "Vídeos, producciones musicales y anuncios creados esta semana.", "Videos, music productions and ads created this week.", "Video, produzioni musicali e annunci creati questa settimana.", "Videos, Musikproduktionen und Anzeigen dieser Woche.")
    est = _estado_alertas()
    for a in out: a["estado"] = (est.get(a["id"]) or {}).get("estado", "nueva")
    return out


def alerta_marcar(i, estado):
    p = os.path.join(core.carpeta_config(), "centro-alertas.json"); d = _estado_alertas()
    if estado == "nueva": d.pop(i, None)
    else: d[i] = {"estado": estado, "t": int(time.time())}
    json.dump(d, open(p, "w", encoding="utf8"))


def analista(c):
    """Observaciones calculadas SOLO con los datos de arriba. La confianza baja cuando hay pocos datos."""
    h = c["_h"]; per = L("periodo elegido", "selected period", "periodo scelto", "gewählter Zeitraum"); out = []
    def ins(o, m, imp, acc, conf, p=None):
        out.append({"o": o, "m": m, "p": p or L("datos actuales", "current data", "dati attuali", "aktuelle Daten"), "i": imp, "a": acc, "c": conf})
    s = h["social"]
    if s["pl"]:
        ins(L("Cabra Social tiene %d publicaciones planificadas y %d publicadas." % (s["pl"], s["pub"]), "Cabra Social has %d posts planned and %d published." % (s["pl"], s["pub"]), "Cabra Social ha %d post pianificati e %d pubblicati." % (s["pl"], s["pub"]), "Cabra Social hat %d geplante und %d veröffentlichte Beiträge." % (s["pl"], s["pub"])),
            "%d / %d" % (s["pub"], s["pl"]), L("Lo producido solo genera valor cuando sale a redes.", "What is produced only creates value once it is posted.", "Ciò che si produce crea valore solo quando viene pubblicato.", "Produziertes schafft erst Wert, wenn es veröffentlicht wird."),
            L("Revisa la cola y marca como publicadas las que ya salieron.", "Review the queue and mark the ones already posted as published.", "Controlla la coda e segna come pubblicati quelli già usciti.", "Prüfe die Warteschlange und markiere bereits gepostete als veröffentlicht."), t("alta"))
    if s["atras"]:
        ins(L("%d publicaciones tienen la fecha pasada y no están publicadas." % s["atras"], "%d posts are past their date and not published." % s["atras"], "%d post hanno la data passata e non sono pubblicati." % s["atras"], "%d Beiträge sind über dem Datum und nicht veröffentlicht." % s["atras"]), str(s["atras"]),
            L("Retraso operativo en el calendario.", "Operational delay in the calendar.", "Ritardo operativo nel calendario.", "Operative Verzögerung im Kalender."), L("Publícalas o reprograma sus fechas.", "Publish them or reschedule their dates.", "Pubblicali o riprogramma le date.", "Veröffentliche sie oder plane die Termine um."), t("alta"))
    cv = h["carta"]
    if cv["platos"]:
        ins(L("Carta Viva tiene %d platos y %d aún sin vídeo." % (cv["platos"], cv["sin_video"]), "Carta Viva has %d dishes and %d still without video." % (cv["platos"], cv["sin_video"]), "Carta Viva ha %d piatti e %d ancora senza video." % (cv["platos"], cv["sin_video"]), "Carta Viva hat %d Gerichte, %d noch ohne Video." % (cv["platos"], cv["sin_video"])),
            "%d / %d" % (cv["platos"] - cv["sin_video"], cv["platos"]), L("Una carta sin todos sus vídeos pierde parte de su propuesta.", "A menu without all its videos loses part of its value.", "Un menù senza tutti i video perde parte del suo valore.", "Eine Karte ohne alle Videos verliert einen Teil ihres Werts."),
            L("Pulsa «Crear vídeos y carta» en Carta Viva.", "Press “Create videos and menu” in Carta Viva.", "Premi «Crea video e menù» in Carta Viva.", "Drücke in Carta Viva auf „Videos und Karte erstellen“."), t("alta"))
    m = h["musica"]
    if m["lib"]:
        ins(L("En Cabra Beats hay %d fichas en la biblioteca y %d están en YouTube." % (m["lib"], m["yt"]), "Cabra Beats has %d library records and %d are on YouTube." % (m["lib"], m["yt"]), "Cabra Beats ha %d schede in libreria e %d sono su YouTube." % (m["lib"], m["yt"]), "Cabra Beats hat %d Bibliothekseinträge, %d sind auf YouTube." % (m["lib"], m["yt"])),
            "%d / %d" % (m["yt"], m["lib"]), L("Las canciones sin subir no generan audiencia.", "Songs not uploaded cannot build an audience.", "Le canzoni non caricate non generano pubblico.", "Nicht hochgeladene Songs bauen kein Publikum auf."), L("Sube las pendientes desde su caja en Cabra Beats.", "Upload the pending ones from their box in Cabra Beats.", "Carica quelle in sospeso dalla loro scheda in Cabra Beats.", "Lade die offenen aus ihrer Box in Cabra Beats hoch."), t("alta"))
    for u, nom in (("musica", "Cabra Beats"), ("carta", "Carta Viva"), ("social", "Cabra Social")):
        x = c["comparativa"][u]
        if x["ant"] and x["act"] != x["ant"]:
            v = 100.0 * (x["act"] - x["ant"]) / x["ant"]
            ins(L("La actividad de %s %s un %d%% frente al periodo anterior." % (nom, "subió" if v > 0 else "bajó", abs(v)), "%s activity %s %d%% versus the previous period." % (nom, "rose" if v > 0 else "fell", abs(v)), "L'attività di %s è %s del %d%% rispetto al periodo precedente." % (nom, "salita" if v > 0 else "scesa", abs(v)), "Die Aktivität von %s %s um %d%% gegenüber dem Vorzeitraum." % (nom, "stieg" if v > 0 else "sank", abs(v))),
                "%d → %d" % (x["ant"], x["act"]), L("Es una variación de actividad registrada, no de ingresos.", "This is a change in recorded activity, not revenue.", "È una variazione di attività registrata, non di ricavi.", "Das ist eine Veränderung der erfassten Aktivität, nicht der Einnahmen."),
                L("Mira qué se produjo en uno y otro periodo antes de sacar conclusiones.", "Check what was produced in each period before drawing conclusions.", "Controlla cosa è stato prodotto in ciascun periodo prima di trarre conclusioni.", "Prüfe, was in beiden Zeiträumen produziert wurde, bevor du Schlüsse ziehst."), t("media") if min(x["act"], x["ant"]) < 5 else t("alta"), per)
    pe = h["pend"]
    if sum(pe.values()):
        k = max(pe, key=lambda z: pe[z]); nom = {"musica": "Cabra Beats", "carta": "Carta Viva", "social": "Cabra Social"}[k]
        ins(L("El mayor trabajo pendiente está en %s (%d)." % (nom, pe[k]), "The largest pending workload is in %s (%d)." % (nom, pe[k]), "Il maggior lavoro in sospeso è in %s (%d)." % (nom, pe[k]), "Die größte offene Arbeit liegt bei %s (%d)." % (nom, pe[k])), str(pe[k]),
            L("Es el punto donde más se acumula trabajo sin terminar.", "It is where the most unfinished work piles up.", "È il punto dove si accumula più lavoro non finito.", "Hier staut sich die meiste unfertige Arbeit."), L("Empieza por aquí en tu próxima sesión.", "Start here in your next session.", "Inizia da qui nella prossima sessione.", "Beginne hier in deiner nächsten Sitzung."), t("alta"))
    if not c["finanzas"]["hay"]:
        ins(L("No hay movimientos financieros registrados.", "No financial entries are recorded.", "Nessun movimento finanziario registrato.", "Keine Finanzeinträge erfasst."), "0", L("Sin ellos no se puede calcular beneficio ni margen.", "Without them, profit and margin cannot be calculated.", "Senza di essi non si possono calcolare profitto e margine.", "Ohne sie lassen sich Gewinn und Marge nicht berechnen."),
            L("Añade ingresos y gastos en la pestaña Finanzas.", "Add revenue and expenses in the Finance tab.", "Aggiungi ricavi e spese nella scheda Finanze.", "Füge Einnahmen und Ausgaben im Reiter Finanzen hinzu."), t("alta"))
    return out


def resumen_ia(c, ins):
    """La IA solo redacta con las observaciones calculadas; no puede añadir cifras."""
    import marca
    datos = json.dumps({"kpi": [{k: x.get(k) for k in ("l", "v")} for x in c["global"]], "observaciones": ins}, ensure_ascii=False)
    r = marca.ia_json("Eres analista de negocio. Escribe un resumen ejecutivo de 4 a 6 frases en " + marca.lengua() + " usando SOLO estas cifras y observaciones; no añadas ninguna cifra, causa ni previsión que no esté en los datos, y no hagas frases motivacionales. Si falta un dato, dilo. Responde JSON {\"resumen\": \"...\"}. Datos: " + datos)
    return str(r.get("resumen") or "")


# ---------------------------------------------------------------- instantáneas y objetivos
def snapshot(c):
    p = os.path.join(core.carpeta_config(), "centro-historial.json"); h = _j(p, {}) or {}; hoy = datetime.date.today().isoformat()
    if hoy not in h:
        h[hoy] = {x["id"]: x["v"] for x in c["global"] if x["id"] in ("assets", "pend", "ok")}
        try: json.dump(h, open(p, "w", encoding="utf8"))
        except Exception: pass
    return [{"x": k[5:], "v": v.get("assets", 0)} for k, v in sorted(h.items())][-60:]


def objetivos(nuevo=None):
    p = os.path.join(core.carpeta_config(), "centro-objetivos.json")
    if nuevo is not None:
        d = {k: max(0, int(nuevo.get(k) or 0)) for k in ("musica", "carta", "social")}; json.dump(d, open(p, "w", encoding="utf8")); return d
    return _j(p, {}) or {}


# ---------------------------------------------------------------- API e informes
def api(p="30d", d1=None, d2=None, activos=None):
    c = calcular(p, d1, d2, activos); ins = analista(c); al = alertas(c); hist = snapshot(c)
    out = {k: v for k, v in c.items() if k != "_h"}
    out.update({"analista": ins, "alertas": al, "historial": {"t": "", "d": hist}["d"], "objetivos": objetivos(), "dic": diccionario()})
    return out


def _fuente(n):
    from PIL import ImageFont
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/System/Library/Fonts/Supplemental/Arial.ttf", "C:/Windows/Fonts/arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        try: return ImageFont.truetype(f, n)
        except Exception: pass
    return ImageFont.load_default()


def informe(tipo, p="30d", d1=None, d2=None, activos=None):
    """PDF de varias páginas con las cifras reales. Devuelve (ruta, mensaje)."""
    from PIL import Image, ImageDraw
    import textwrap
    pp = {"semanal": "7d", "mensual": "mes", "trimestral": "trim", "anual": "anio"}.get(tipo, p)
    c = calcular(pp, d1, d2, activos); ins = analista(c); al = alertas(c)
    W, H = 1240, 1754; pag = []; M = 90
    im = [None]; dr = [None]; y = [0]
    def nueva():
        im[0] = Image.new("RGB", (W, H), "white"); dr[0] = ImageDraw.Draw(im[0]); pag.append(im[0]); y[0] = M
        dr[0].rectangle([0, 0, W, 14], fill="#e2b04a")
    def tx(s, n=26, col="#1a1f2b", ind=0, ancho=None):
        f = _fuente(n)
        for ln in textwrap.wrap(str(s), ancho or int((W - 2 * M - ind) / (n * 0.52))) or [""]:
            if y[0] > H - M: nueva()
            dr[0].text((M + ind, y[0]), ln, font=f, fill=col); y[0] += int(n * 1.4)
    def barra(l, v, m, col):
        if y[0] > H - M - 40: nueva()
        dr[0].text((M, y[0]), "%s: %s" % (l, v), font=_fuente(22), fill="#1a1f2b"); y[0] += 30
        dr[0].rectangle([M, y[0], M + 700, y[0] + 14], fill="#e8ebf0"); dr[0].rectangle([M, y[0], M + int(700 * v / m) if m else M, y[0] + 14], fill=col); y[0] += 30
    nueva(); tx("ISLAND CREW INTELLIGENCE CENTER", 40, "#142033"); tx({"semanal": t("Semanal"), "mensual": t("Mensual"), "trimestral": t("Trimestral"), "anual": t("Anual"), "consolidado": t("Consolidado")}.get(tipo, NM_U.get(tipo, tipo)) + " · " + time.strftime("%d/%m/%Y", time.localtime(c["periodo"]["a"])) + " – " + time.strftime("%d/%m/%Y", time.localtime(c["periodo"]["b"] - 1)), 26, "#5a6578")
    y[0] += 20; tx(t("Todas las cifras salen de los ficheros reales de tus programas. Lo que no se registra (escaneos de QR, audiencia, ingresos) aparece como «sin datos» y no se inventa."), 20, "#8d98aa"); y[0] += 20
    unidades = [tipo] if tipo in NM_U else ["musica", "carta", "social"]
    if tipo not in NM_U:
        tx(t("Global"), 32, "#142033")
        for k in c["global"]: tx("%s: %s%s — %s" % (k["l"], "—" if k["v"] is None else nf_(k["v"]), k.get("u", ""), k["d"]), 22)
        y[0] += 14
    for u in unidades:
        d = c["unidades"][u]; col = {"musica": "#ffb020", "carta": "#3fbf7f", "social": "#4aa8ff"}[u]; tx(NM_U[u], 32, "#142033")
        m = max([x["v"] for x in d["kpi"]] + [1])
        for k in d["kpi"]: barra(k["l"], k["v"], m, col)
        x = c["comparativa"][u]; tx("%s: %d · %s: %d" % (t("Periodo"), x["act"], t("anterior"), x["ant"]), 22, "#5a6578"); tx(d["embudo"]["nota"], 18, "#8d98aa"); y[0] += 14
    tx(t("Analista de negocio"), 32, "#142033")
    for a in ins:
        tx("• " + a["o"], 22); tx("%s · %s: %s" % (a["i"], t("Acción sugerida"), a["a"]), 19, "#5a6578", 24)
    y[0] += 10; tx(t("Alertas"), 32, "#142033")
    for a in al: tx("[%s] %s" % (a["nivel"], a["t"]), 21)
    f = c["finanzas"]; tx(t("Finanzas"), 32, "#142033")
    if not f["hay"]: tx(t("No hay movimientos financieros registrados. Los ingresos y gastos se introducen a mano: la suite no los conoce ni los estima."), 20, "#8d98aa")
    else:
        for k, v in f["por_unidad"].items(): tx("%s: %s %.2f · %s %.2f · %s %.2f" % (NM_U.get(k, t("General")), t("Ingresos"), v["ing"], t("Gastos"), v["gas"], t("Beneficio"), v["ing"] - v["gas"]), 21)
    for i, pg in enumerate(pag): ImageDraw.Draw(pg).text((M, H - 60), "Island Crew · hola@islandcrew.es · %d/%d" % (i + 1, len(pag)), font=_fuente(18), fill="#8d98aa")
    dest = os.path.join(os.path.expanduser("~"), "Downloads"); os.makedirs(dest, exist_ok=True)
    ruta = os.path.join(dest, "IslandCrew-Informe-%s-%s.pdf" % (tipo, time.strftime("%Y%m%d-%H%M")))
    pag[0].save(ruta, "PDF", resolution=150, save_all=True, append_images=pag[1:]); return ruta


NM_U = {"musica": "Cabra Beats", "carta": "Carta Viva", "social": "Cabra Social"}


def nf_(v): return ("%g" % round(v, 1))
