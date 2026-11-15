#!/usr/bin/env python3
"""Analítica REAL de YouTube (YouTube Analytics API) -> web (/api/oficina/media-metricas). Solo cifras que devuelve YouTube; si una métrica no está disponible se deja vacía, nunca se inventa.
Requiere reautorizar YouTube una vez (Acciones -> Reautorizar YouTube) para añadir el permiso yt-analytics.readonly, y tener activada la «YouTube Analytics API» en Google Cloud."""
# PATH_EXTRA: el worker arranca desde launchd sin /opt/homebrew/bin; sin esto no encuentra ffmpeg ni ffprobe.
import os as _os
_os.environ["PATH"] = _os.pathsep.join([x for x in ["/opt/homebrew/bin", "/usr/local/bin", "/opt/homebrew/sbin"] if x not in _os.environ.get("PATH", "")] + [_os.environ.get("PATH", "")])

import importlib.util, json, os, sys, time, urllib.request, urllib.parse, urllib.error
AQUI = os.path.dirname(os.path.abspath(__file__))
def _cargar(nombre, f):
    sp = importlib.util.spec_from_file_location(nombre, os.path.join(AQUI, f)); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
BASE = "https://youtubeanalytics.googleapis.com/v2/reports"
def consulta(tok, metricas, ini, fin, dim="video", extra=None):
    q = {"ids": "channel==MINE", "startDate": ini, "endDate": fin, "metrics": metricas, "dimensions": dim, "maxResults": 200}
    if dim == "video": q["sort"] = "-views"
    q.update(extra or {})
    r = urllib.request.Request(BASE + "?" + urllib.parse.urlencode(q), headers={"Authorization": "Bearer " + tok})
    return json.load(urllib.request.urlopen(r, timeout=60))
def filas(d):
    cols = [c["name"] for c in d.get("columnHeaders", [])]; return [dict(zip(cols, f)) for f in d.get("rows", [])]
def _get(tok, url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers={"Authorization": "Bearer " + tok}), timeout=60))
def canal(tok):
    """Cifras del CANAL para el panel de monetización. Solo lo que devuelve YouTube; lo que falla queda como None (nunca se inventa)."""
    r = {"fuente": "youtube_api", "medido": time.strftime("%Y-%m-%d"), "suscriptores": None, "horas12m": None, "shorts90d": None, "subidas90d": None, "avisos": []}
    sube = None
    try:
        d = _get(tok, "https://www.googleapis.com/youtube/v3/channels?part=statistics,contentDetails&mine=true"); it = (d.get("items") or [{}])[0]
        st = it.get("statistics", {}); r["suscriptores"] = None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0))
        sube = it.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
    except Exception as e: r["avisos"].append("suscriptores: " + str(e)[:80])
    try:
        fin = time.strftime("%Y-%m-%d"); ini = time.strftime("%Y-%m-%d", time.localtime(time.time() - 365 * 86400))
        f = _sin_dim(tok, "estimatedMinutesWatched", ini, fin)
        if f: r["horas12m"] = round(float(f[0].get("estimatedMinutesWatched") or 0) / 60, 1)
    except Exception as e: r["avisos"].append("horas: " + str(e)[:80])
    try:
        fin = time.strftime("%Y-%m-%d"); ini = time.strftime("%Y-%m-%d", time.localtime(time.time() - 90 * 86400)); tot = 0
        for f in filas(consulta(tok, "views", ini, fin, dim="creatorContentType")):
            if str(f.get("creatorContentType", "")).upper().startswith("SHORT"): tot += int(f.get("views") or 0)
        r["shorts90d"] = tot
    except Exception as e: r["avisos"].append("Shorts: " + str(e)[:80])
    if sube:
        try:
            lim = time.time() - 90 * 86400; n = 0; pag = ""
            for _ in range(10):
                d = _get(tok, "https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails,status&maxResults=50&playlistId=" + sube + pag)
                for x in d.get("items", []):
                    if x.get("status", {}).get("privacyStatus") != "public": continue
                    t = time.mktime(time.strptime(x["contentDetails"]["videoPublishedAt"][:19], "%Y-%m-%dT%H:%M:%S")) if x["contentDetails"].get("videoPublishedAt") else 0
                    if t >= lim: n += 1
                if not d.get("nextPageToken"): break
                pag = "&pageToken=" + d["nextPageToken"]
            r["subidas90d"] = n
        except Exception as e: r["avisos"].append("subidas: " + str(e)[:80])
    return r
def _sin_dim(tok, metricas, ini, fin):
    q = {"ids": "channel==MINE", "startDate": ini, "endDate": fin, "metrics": metricas}
    return filas(json.load(urllib.request.urlopen(urllib.request.Request(BASE + "?" + urllib.parse.urlencode(q), headers={"Authorization": "Bearer " + tok}), timeout=60)))
def medir(dias=28):
    yt = _cargar("yt", "youtube-subir.py"); fm = _cargar("fm", "fabrica-musica.py")
    try: tok = yt.token_valido(False)
    except SystemExit: return {"ok": False, "motivo": "permiso de YouTube caducado: Media OS → Conectar YouTube"}
    fin = time.strftime("%Y-%m-%d"); ini = time.strftime("%Y-%m-%d", time.localtime(time.time() - dias * 86400)); hoy = fin; aviso = []
    try: base = filas(consulta(tok, "views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained,subscribersLost,likes,comments,shares", ini, fin))
    except urllib.error.HTTPError as e:
        cuerpo = e.read().decode(errors="ignore")[:300]
        return {"ok": False, "motivo": ("falta el permiso de analítica: Media OS → Conectar YouTube (y activa «YouTube Analytics API» en Google Cloud)" if e.code in (401, 403) else f"YouTube Analytics respondió {e.code}: {cuerpo}")}
    imp = {}
    try:
        for f in filas(consulta(tok, "videoThumbnailImpressions,videoThumbnailImpressionsClickRate", ini, fin)): imp[f["video"]] = f
    except Exception as e: aviso.append("impresiones/CTR no disponibles por la API para este canal (míralos en Studio): " + str(e)[:80])
    cortos = {}; sep = False
    try:
        for f in filas(consulta(tok, "views", ini, fin, dim="video,creatorContentType")):
            if str(f.get("creatorContentType", "")).upper().startswith("SHORT"): cortos[f["video"]] = True
        sep = True
    except Exception as e: aviso.append("no se pudo separar Shorts de largos")
    out = []
    for f in base:
        v = f["video"]; i = imp.get(v, {})
        out.append({"video_id": v, "fecha": hoy, "fuente": "analytics_api", "es_short": ((True if cortos.get(v) else False) if sep else None), "vistas": f.get("views"), "impresiones": i.get("videoThumbnailImpressions"), "ctr": i.get("videoThumbnailImpressionsClickRate"), "duracion_media_seg": f.get("averageViewDuration"), "porcentaje_visto": f.get("averageViewPercentage"), "suscriptores_ganados": f.get("subscribersGained"), "compartidos": f.get("shares"), "comentarios": f.get("comments"), "likes": f.get("likes"), "tiempo_visto_min": f.get("estimatedMinutesWatched"), "extra": {"suscriptores_perdidos": f.get("subscribersLost"), "ventana_dias": dias}})
    try: cn = canal(tok)
    except Exception as e: cn = None; aviso.append("canal: " + str(e)[:80])
    r = fm._web("/api/oficina/media-metricas", {"metricas": out, "avisos": aviso, "canal": cn})
    return {"ok": bool(r and r.get("ok")), "videos": len(out), "avisos": aviso, "motivo": "" if r else "la web no respondió (ISLANDCREW_URL y CRON_SECRET)"}
if __name__ == "__main__":
    print(json.dumps(medir(int(sys.argv[1]) if len(sys.argv) > 1 else 28), ensure_ascii=False))
