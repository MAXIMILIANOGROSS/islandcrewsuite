#!/bin/bash
# Construye «Carta Viva.app» (ventana propia) y la deja en el Escritorio. Se hace UNA vez.
set -e
D="$(cd "$(dirname "$0")/../../.." && pwd)"; APP="$(mktemp -d)/Carta Viva.app"; M="$APP/Contents/MacOS"; mkdir -p "$M" "$APP/Contents/Resources"
swiftc -O -o "$M/CartaViva" "$D/scripts/carta-viva/app-nativa/main.swift" -framework Cocoa -framework WebKit
cat > "$APP/Contents/Info.plist" <<P
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict><key>CFBundleExecutable</key><string>CartaViva</string><key>CFBundleIdentifier</key><string>es.islandcrew.cartaviva</string><key>CFBundleName</key><string>Carta Viva</string><key>CFBundleIconFile</key><string>icon</string><key>CFBundlePackageType</key><string>APPL</string><key>LSMinimumSystemVersion</key><string>11.0</string><key>NSHighResolutionCapable</key><true/></dict></plist>
P
T="$(mktemp -d)"; /usr/local/bin/python3 - "$T/i.png" "$D/scripts/carta-viva/cabra-logo.png" <<'PY'
import sys
from PIL import Image, ImageDraw
im=Image.open(sys.argv[2]).convert("RGB"); w,h=im.size; s=h; x=int(w*0.5-s*0.52); x=max(0,min(x,w-s))
c=im.crop((x,0,x+s,s)).resize((824,824),Image.LANCZOS)
m=Image.new("L",(824,824),0); ImageDraw.Draw(m).rounded_rectangle((0,0,823,823),185,fill=255)
o=Image.new("RGBA",(1024,1024),(0,0,0,0)); o.paste(c,(100,100),m); o.save(sys.argv[1])
PY
IC="$T/c.iconset"; mkdir -p "$IC"; for s in 16 32 128 256 512; do sips -z $s $s "$T/i.png" --out "$IC/icon_${s}x${s}.png" >/dev/null; sips -z $((s*2)) $((s*2)) "$T/i.png" --out "$IC/icon_${s}x${s}@2x.png" >/dev/null; done
iconutil -c icns "$IC" -o "$APP/Contents/Resources/icon.icns"
rm -rf "$HOME/Desktop/Carta Viva.app"; cp -R "$APP" "$HOME/Desktop/"
xattr -cr "$HOME/Desktop/Carta Viva.app" 2>/dev/null; codesign --force --deep -s - "$HOME/Desktop/Carta Viva.app" 2>/dev/null || true
echo "✔ Listo: icono «Carta Viva» en tu escritorio."
