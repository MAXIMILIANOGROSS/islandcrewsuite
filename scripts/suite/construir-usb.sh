#!/bin/bash
# Monta la carpeta del pendrive (Windows + Mac). Se ejecuta en el Mac del propietario.
# Uso: bash construir-usb.sh [carpeta_destino] [carpeta_descargas]
set -e
SUITE="$(cd "$(dirname "$0")" && pwd)"; SCR="$SUITE/.."
BASE="/Volumes/T5 EVO/IslandCrewAI/pendrive"
OUT="${1:-$BASE/Island Crew Suite - USB}"; CACHE="${2:-$BASE/_descargas}"
PY="${PYTHON:-/usr/local/bin/python3}"
mkdir -p "$OUT" "$CACHE"
dl() { [ -s "$CACHE/$2" ] || { echo "Descargando $2 ..."; curl -fL --retry 3 -o "$CACHE/$2.part" "$1" && mv "$CACHE/$2.part" "$CACHE/$2"; }; }

echo "== Aplicación"
rm -rf "$OUT/app"; mkdir -p "$OUT/app/scripts/suite" "$OUT/app/scripts/carta-viva" "$OUT/app/scripts/publicaciones" "$OUT/app/scripts/anuncios"
cp "$SUITE"/{core.py,lic.py,suite.py,asistente.html,inicio.html,clave-publica.txt,marca.py,i18n_data.py,centro.py,centro.html,centro_txt.py,marca.jpg,cabra-social.jpg,ic-carta.png,ic-publicaciones.png,ic-anuncios.png,ic-musica.png,control.jpg,av-carta.jpg,av-publicaciones.jpg,av-anuncios.jpg} "$OUT/app/scripts/suite/"
cp "$SCR/carta-viva/carta-viva-app.py" "$SCR/carta-viva/carta-viva-app.html" "$OUT/app/scripts/carta-viva/"
[ -f "$SCR/carta-viva/cabra-logo.png" ] && cp "$SCR/carta-viva/cabra-logo.png" "$OUT/app/scripts/carta-viva/"
cp "$SCR/publicaciones/publicaciones-app.py" "$SCR/publicaciones/publicaciones-app.html" "$OUT/app/scripts/publicaciones/"
cp "$SCR/anuncios/anuncios-app.py" "$SCR/anuncios/anuncios-app.html" "$OUT/app/scripts/anuncios/"
cp -R "$SCR/carta-viva/vendor" "$OUT/app/scripts/carta-viva/vendor"
for k in carta publicaciones anuncios musica; do cp "$SUITE/icono/$k.icns" "$SUITE/icono/$k.ico" "$OUT/app/"; done
mkdir -p "$OUT/app/bin"; [ -f "$SUITE/ventana/ventana-mac" ] && cp "$SUITE/ventana/ventana-mac" "$OUT/app/bin/"
cp "$SUITE/icono/IslandCrewSuite.icns" "$OUT/app/icono.icns"; cp "$SUITE/icono/IslandCrewSuite.ico" "$OUT/app/icono.ico"
find "$OUT/app" -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true

echo "== Descargas"
dl https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip py-win.zip
dl "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.11.18%2B20261110-aarch64-apple-darwin-install_only.tar.gz" py-mac-arm64.tar.gz
dl "https://github.com/astral-sh/python-build-standalone/releases/download/20261110/cpython-3.11.18%2B20261110-x86_64-apple-darwin-install_only.tar.gz" py-mac-x64.tar.gz
dl https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-9.0.2-essentials_build.zip ff-win.zip
dl https://www.osxexperts.net/ffmpeg80arm.zip ff-mac-arm64.zip
dl https://www.osxexperts.net/ffmpeg80intel.zip ff-mac-x64.zip

echo "== Windows"
rm -rf "$OUT/runtime-win" "$OUT/bin-win"; mkdir -p "$OUT/runtime-win/python" "$OUT/bin-win"
unzip -q -o "$CACHE/py-win.zip" -d "$OUT/runtime-win/python"
"$PY" -m pip install -q --no-deps --only-binary=:all: --platform win_amd64 --python-version 3.11 --implementation cp --abi cp311 --target "$OUT/runtime-win/site-packages" pillow
T=$(mktemp -d); unzip -q -o "$CACHE/ff-win.zip" -d "$T"
cp "$(find "$T" -name ffmpeg.exe | head -1)" "$OUT/bin-win/"; cp "$(find "$T" -maxdepth 2 -iname 'LICENSE*' | head -1)" "$OUT/bin-win/FFMPEG-LICENSE.txt" 2>/dev/null || true; rm -rf "$T"

for A in arm64 x64; do
  echo "== Mac $A"
  PL=macosx_11_0_arm64; [ "$A" = x64 ] && PL=macosx_10_13_x86_64
  rm -rf "$OUT/runtime-mac-$A" "$OUT/bin-mac-$A"; mkdir -p "$OUT/runtime-mac-$A" "$OUT/bin-mac-$A"
  cp "$CACHE/py-mac-$A.tar.gz" "$OUT/runtime-mac-$A/python.tar.gz"
  "$PY" -m pip install -q --no-deps --only-binary=:all: --platform $PL --python-version 3.11 --implementation cp --abi cp311 --target "$OUT/runtime-mac-$A/site-packages" pillow
  unzip -q -o "$CACHE/ff-mac-$A.zip" -x "__MACOSX/*" -d "$OUT/bin-mac-$A"
done

echo "== Instaladores y textos"
rm -rf "$OUT/Windows" "$OUT/Mac" "$OUT/Licencias"; mkdir -p "$OUT/Windows" "$OUT/Mac" "$OUT/Licencias"
cp "$SUITE/instaladores/"{Instalar-Windows.bat,instalar.ps1,Desinstalar.ps1} "$OUT/Windows/"
cp "$SUITE/instaladores/"{Instalar-Mac.command,Desinstalar-Mac.command} "$OUT/Mac/"
chmod +x "$OUT/Mac/"*.command
cp "$SUITE/LICENCIAS.txt" "$OUT/Licencias/LICENCIAS.txt"
cp "$OUT/bin-win/FFMPEG-LICENSE.txt" "$OUT/Licencias/" 2>/dev/null || true
cp "$SUITE/LEEME.md" "$OUT/LEEME.md"
dot_clean -m "$OUT" 2>/dev/null || true
find "$OUT" -name ".DS_Store" -delete 2>/dev/null || true
echo "== Listo"; du -sh "$OUT"; ls "$OUT"
