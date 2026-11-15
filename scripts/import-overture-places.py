#!/usr/bin/env python3
"""Lugares de Corralejo desde Overture Maps (datos abiertos, gratis) con DuckDB. Uso: python3 scripts/import-overture-places.py [release]"""
import json, re, subprocess, sys, os, hashlib
try:
    import duckdb
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "-q", "duckdb"]); import duckdb
rel = sys.argv[1] if len(sys.argv) > 1 else "2026-09-23.1"
con = duckdb.connect(); con.execute("INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")
src = f"read_parquet('s3://overturemaps-us-west-2/release/{rel}/theme=places/type=place/*', hive_partitioning=1)"
cols = {r[0]: str(r[1]) for r in con.execute(f"DESCRIBE SELECT * FROM {src} LIMIT 1").fetchall()}
print("columnas:", ", ".join(cols))
if "categories" in cols: catx = "p.categories.primary"
elif "basic_category" in cols: catx = "p.basic_category"
elif "taxonomy" in cols: catx = "array_to_string(p.taxonomy.hierarchy, '_')"
else: catx = "''"
conf = "p.confidence" if "confidence" in cols else "1.0"
em = "p.emails[1]" if "emails" in cols else "NULL"; ph = "p.phones[1]" if "phones" in cols else "NULL"; wb = "p.websites[1]" if "websites" in cols else "NULL"
ad = "concat_ws(', ', p.addresses[1].freeform, p.addresses[1].postcode, p.addresses[1].locality)" if "addresses" in cols else "NULL"
so = "p.socials[1]" if "socials" in cols else "NULL"; st = "p.operating_status" if "operating_status" in cols else "'open'"
q = f"""SELECT p.id, p.names.primary AS name, {catx} AS cat, {conf} AS confidence, p.bbox.xmin AS lng, p.bbox.ymin AS lat, {em} AS email, {ph} AS phone, {wb} AS web, {ad} AS address, {so} AS social, {st} AS status
FROM {src} AS p
WHERE p.bbox.xmin BETWEEN -13.89 AND -13.84 AND p.bbox.ymin BETWEEN 28.72 AND 28.76"""
rows = con.execute(q).fetchall(); print(f"{len(rows)} lugares en la zona (sin filtrar)")
def typ(c):
    c = str(c or "")
    if re.search(r"hotel|hostel|resort|lodging|guest_house|motel", c): return "hotel"
    if re.search(r"cafe|coffee|tea_room", c): return "cafe"
    if re.search(r"bakery|pastry", c): return "bakery"
    if re.search(r"(^|_)bar($|_)|pub|nightlife|night_club|lounge", c): return "bar"
    if re.search(r"restaurant|food|pizza|tapas|seafood|burger|sushi|ice_cream|takeaway|fast_food", c): return "restaurant"
    if re.search(r"supermarket|grocery|convenience", c): return "supermarket"
    return None
out, seen = [], set()
for id_, name, cat, conf, lng, lat, email, phone, web, address, social, status in rows:
    if status and str(status).lower() not in ("open", "none"): continue
    if not name or (conf is not None and conf < 0.6): continue
    t = typ(cat)
    if not t: continue
    k = (name.lower(), round(lat * 4000), round(lng * 4000))
    if k in seen: continue
    seen.add(k); out.append({"id": str(id_), "name": name, "lat": lat, "lng": lng, "type": t, "email": email, "phone": phone, "web": web, "address": address, "social": social, "oid": 9000000000000 + int(hashlib.md5(str(id_).encode()).hexdigest()[:8], 16)})
dest = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "public", "data", "corralejo-places.overture.json")
json.dump({"places": out, "attribution": "Lugares: Overture Maps Foundation (datos abiertos)"}, open(dest, "w"), ensure_ascii=False)
print(f"OK: {len(out)} lugares -> public/data/corralejo-places.overture.json (ahora ejecuta: python3 scripts/build-unified-venues.py)")
