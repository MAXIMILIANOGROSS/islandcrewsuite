#!/bin/bash
# Construye el programa de Cabra Beats (ventana propia, sin Chrome). Se hace UNA vez.
set -e
D="$(cd "$(dirname "$0")/../.." && pwd)"; APP="$D/Cabra Beats.app"
swiftc -O -o "$APP/Contents/MacOS/CabraBeats" "$D/scripts/app-nativa/main.swift" -framework Cocoa -framework WebKit
cd "$APP/Contents/MacOS" && for f in *; do [ "$f" = CabraBeats ] || rm -f "$f"; done
/usr/libexec/PlistBuddy -c "Set :CFBundleExecutable CabraBeats" "$APP/Contents/Info.plist"
/usr/libexec/PlistBuddy -c "Add :NSMicrophoneUsageDescription string Cabra Beats usa el micrófono para grabar tu voz y clonarla." "$APP/Contents/Info.plist" 2>/dev/null || /usr/libexec/PlistBuddy -c "Set :NSMicrophoneUsageDescription Cabra Beats usa el micrófono para grabar tu voz y clonarla." "$APP/Contents/Info.plist"
# icono propio de Cabra Beats (la cabra con auriculares)
IC="$(mktemp -d)/c.iconset"; mkdir -p "$IC"; SRC="$D/scripts/cabra-beats-icon-1024.png"
if [ -f "$SRC" ]; then for s in 16 32 128 256 512; do sips -z $s $s "$SRC" --out "$IC/icon_${s}x${s}.png" >/dev/null; sips -z $((s*2)) $((s*2)) "$SRC" --out "$IC/icon_${s}x${s}@2x.png" >/dev/null; done; iconutil -c icns "$IC" -o "$APP/Contents/Resources/icon.icns" && echo "✔ icono nuevo"; fi
for DEST in "$HOME/Desktop"; do rm -rf "$DEST/Cabra Beats.app"; cp -R "$APP" "$DEST/"; done
xattr -cr "$HOME/Desktop/Cabra Beats.app" 2>/dev/null; codesign --force --deep -s - "$HOME/Desktop/Cabra Beats.app" 2>/dev/null || true
echo "✔ Listo: icono «Cabra Beats» en tu escritorio. Doble clic y se abre."
