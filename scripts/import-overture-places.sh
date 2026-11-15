#!/usr/bin/env bash
# Descarga GRATIS los lugares de Corralejo de Overture Maps (datos abiertos, sin clave ni facturacion) y genera public/data/corralejo-places.json
set -e
cd "$(dirname "$0")/.."
python3 -m pip install --user -q overturemaps
OM="$(python3 -c 'import sys,site,os;print(os.path.join(site.USER_BASE,"bin","overturemaps"))')"
[ -x "$OM" ] || OM=overturemaps
"$OM" download --bbox=-13.89,28.72,-13.84,28.76 -f geojson --type=place -o /tmp/overture-places.geojson
node scripts/convert-overture-places.mjs /tmp/overture-places.geojson
