#!/usr/bin/env python3
"""Une OpenStreetMap + Overture en UNA lista de locales de Corralejo (public/data/corralejo-places.json).
Mismo formato que antes: el juego 3D y el mapa Toytown leen este archivo. Sin red; usa los JSON ya descargados.
Uso: python3 scripts/import-overture-places.py && python3 scripts/build-unified-venues.py"""
import json, math, os, re, unicodedata
D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "data")
def load(n):
    try: return json.load(open(os.path.join(D, n)))
    except Exception: return None
osm = load("corralejo-osm.raw.json"); ov = load("corralejo-places.overture.json") or load("corralejo-places.json") or {"places": []}
els = osm["elements"] if isinstance(osm, dict) else (osm or [])
def norm(t): return re.sub(r"[^a-z0-9]", "", unicodedata.normalize("NFD", (t or "").lower()))
def cat(t):
    a, to, sh = t.get("amenity", ""), t.get("tourism", ""), t.get("shop", "")
    if a in ("restaurant", "bar", "pub", "fast_food", "ice_cream"): return "bar" if a == "pub" else a
    if a == "cafe": return "cafe"
    if to in ("hotel", "hostel", "apartment", "guest_house", "motel"): return "hotel"
    if sh: return "supermarket" if sh in ("supermarket", "convenience") else "shop"
    return None
def pos(e):
    if "lat" in e and "lon" in e: return e["lat"], e["lon"]
    if e.get("center"): return e["center"]["lat"], e["center"]["lon"]
    g = e.get("geometry")
    if g: return sum(p["lat"] for p in g) / len(g), sum(p["lon"] for p in g) / len(g)
    return None
def first(t, *ks):
    for k in ks:
        v = t.get(k)
        if v: return v.split(";")[0].strip()
    return None
def addr(t):
    parts = [" ".join(x for x in (t.get("addr:street"), t.get("addr:housenumber")) if x), t.get("addr:postcode"), t.get("addr:city")]
    return ", ".join(x for x in parts if x) or None
out = []
for e in els:
    t = e.get("tags") or {}; c = cat(t); p = pos(e)
    if not t.get("name") or not c or not p: continue
    wa = first(t, "contact:whatsapp", "whatsapp")
    out.append({"id": f"osm{e['type'][0]}{e['id']}", "name": t["name"], "lat": p[0], "lng": p[1], "type": c,
        "email": first(t, "email", "contact:email"), "phone": wa or first(t, "phone", "contact:phone", "mobile", "contact:mobile"),
        "web": first(t, "website", "contact:website", "url"), "address": addr(t), "social": first(t, "contact:instagram", "contact:facebook"),
        "oid": e["id"], "src": "osm"})
def dist(a, b): return math.hypot((a["lat"] - b["lat"]) * 111000, (a["lng"] - b["lng"]) * 111000 * math.cos(math.radians(a["lat"])))
merged = 0
for g in ov.get("places", []):
    best = None
    for o in out:
        if norm(o["name"]) == norm(g["name"]) or dist(o, g) < 25: best = o; break
    if best:
        merged += 1
        for k in ("email", "phone", "web", "address", "social"):
            if not best.get(k) and g.get(k): best[k] = g[k]
        best["src"] = "osm+overture"
    else:
        out.append({k: g.get(k) for k in ("id", "name", "lat", "lng", "type", "email", "phone", "web", "address", "social", "oid")} | {"src": "overture"})
def wa_digits(ph):
    d = re.sub(r"[^\d+]", "", (ph or "").split("/")[0].split(",")[0])
    if d.startswith("+"): d = d[1:]
    elif d.startswith("00"): d = d[2:]
    elif len(d) == 9: d = "34" + d
    return d if len(d) >= 10 else ""
for o in out:
    d = wa_digits(o.get("phone")); o["wa"] = None
    if d and not (d.startswith("34") and d[2:3] not in ("6", "7")): o["wa"] = f"https://wa.me/{d}"  # solo móviles españoles o números extranjeros/explícitos
json.dump({"places": out, "attribution": "Lugares: © colaboradores de OpenStreetMap (ODbL) y Overture Maps Foundation"}, open(os.path.join(D, "corralejo-places.json"), "w"), ensure_ascii=False)
n = len(out); print(f"OK: {n} locales ({merged} fusionados OSM+Overture); con teléfono {sum(1 for o in out if o.get('phone'))}, con WhatsApp directo {sum(1 for o in out if o.get('wa'))}, con correo {sum(1 for o in out if o.get('email'))}")
