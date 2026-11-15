#!/bin/bash
# Comprime la suite al máximo (xz -9e) en un paquete por sistema y monta el pendrive "ligero".
# Uso: bash comprimir-usb.sh   (después de construir-usb.sh)
set -e
export COPYFILE_DISABLE=1
BASE="/Volumes/T5 EVO/IslandCrewAI/pendrive"; SRC="$BASE/Island Crew Suite - USB"; OUT="$BASE/Island Crew Suite - LIGERO"
SUITE="$(cd "$(dirname "$0")" && pwd)"
rm -rf "$OUT"; mkdir -p "$OUT/Paquetes" "$OUT/Windows" "$OUT/Mac"
STG="$(mktemp -d)"
limpiar() { find "$1" \( -name "__pycache__" -o -name "test" -o -name "tests" -o -name "idle_test" -o -name "tkinter" -o -name "turtledemo" -o -name "ensurepip" -o -name "idlelib" \) -prune -exec rm -rf {} + 2>/dev/null || true; find "$1" \( -name "*.pdb" -o -name "*.pyc" -o -name "*.a" \) -delete 2>/dev/null || true; }
paquete() { # $1 nombre
  (cd "$STG/$1" && tar -cf - .) | xz -9e -T0 > "$OUT/Paquetes/$1.tar.xz"; echo "  $1: $(du -h "$OUT/Paquetes/$1.tar.xz" | cut -f1)"; }

echo "== Windows"
W="$STG/win"; mkdir -p "$W/runtime"
cp -R "$SRC/app" "$W/app"; mkdir -p "$W/app/bin"; cp -R "$SRC/bin-win/." "$W/app/bin/"
cp -R "$SRC/runtime-win/python" "$W/runtime/python"; cp -R "$SRC/runtime-win/site-packages" "$W/runtime/site-packages"
cp -R "$SRC/Licencias" "$W/Licencias"; limpiar "$W"; paquete win

for A in arm64 x64; do
  echo "== Mac $A"; M="$STG/mac-$A"; mkdir -p "$M/runtime"
  cp -R "$SRC/app" "$M/app"; mkdir -p "$M/app/bin"; cp -R "$SRC/bin-mac-$A/." "$M/app/bin/"
  tar xzf "$SRC/runtime-mac-$A/python.tar.gz" -C "$M/runtime"; cp -R "$SRC/runtime-mac-$A/site-packages" "$M/runtime/site-packages"
  rm -rf "$M/runtime/python/share" "$M/runtime/python/lib/tcl"* "$M/runtime/python/lib/tk"* "$M/runtime/python/lib/itcl"* "$M/runtime/python/lib/Tix"* 2>/dev/null || true
  cp -R "$SRC/Licencias" "$M/Licencias"; limpiar "$M"; paquete "mac-$A"
done

cp "$SUITE/instaladores/"{Instalar-Windows.bat,instalar.ps1,Desinstalar.ps1} "$OUT/Windows/"
cp "$SUITE/instaladores/"{Instalar-Mac.command,Desinstalar-Mac.command} "$OUT/Mac/"; chmod +x "$OUT/Mac/"*.command
cp "$SRC/LEEME.md" "$OUT/LEEME.md"; cp -R "$SRC/Licencias" "$OUT/Licencias"
rm -rf "$STG"; find "$OUT" -name ".DS_Store" -delete 2>/dev/null || true
echo "== Listo"; du -sh "$OUT"; du -sh "$OUT"/Paquetes/*
