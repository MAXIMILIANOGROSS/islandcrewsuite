#!/bin/bash
# Island Crew Marketing Suite · instalador para Mac
set -e
cd "$(dirname "$0")/.."
RAIZ="$(pwd)"
echo ""
echo " Island Crew Marketing Suite"
echo " Instalando en tu Mac, un momento..."
echo ""
if [ "$(uname -m)" = "arm64" ]; then R="runtime-mac-arm64"; B="bin-mac-arm64"; else R="runtime-mac-x64"; B="bin-mac-x64"; fi
PQ="$RAIZ/Paquetes/mac-$( [ "$(uname -m)" = arm64 ] && echo arm64 || echo x64 ).tar.xz"
if [ -f "$PQ" ]; then LISTA="Paquetes"; else LISTA="app $R $B Licencias"; fi
for n in $LISTA; do
  [ -d "$RAIZ/$n" ] || { echo " Falta la carpeta $n en el pendrive. Copia el pendrive completo."; exit 1; }
done
DEST="$HOME/Library/Application Support/IslandCrewSuite/programa"
pkill -f "IslandCrewSuite/programa" 2>/dev/null || true
rm -rf "$DEST"; mkdir -p "$DEST/app/bin"
if [ -f "$PQ" ]; then
  tar xJf "$PQ" -C "$DEST"
else
cp -R "$RAIZ/app/." "$DEST/app/"
cp -R "$RAIZ/$R" "$DEST/runtime"
tar xzf "$DEST/runtime/python.tar.gz" -C "$DEST/runtime" && rm -f "$DEST/runtime/python.tar.gz"
cp -R "$RAIZ/Licencias" "$DEST/Licencias"
cp -R "$RAIZ/$B/." "$DEST/app/bin/"
fi
chmod -R u+rwx "$DEST/runtime" "$DEST/app/bin"
xattr -dr com.apple.quarantine "$DEST" 2>/dev/null || true
crear_app() { # id nombre icono argumentos
  local APP="$HOME/Applications/$2.app"
  rm -rf "$APP"; mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
  cat > "$APP/Contents/MacOS/lanzar" <<EOS
#!/bin/bash
D="\$HOME/Library/Application Support/IslandCrewSuite/programa"
PY="\$D/runtime/python/bin/python3"; SU="\$D/app/scripts/suite/suite.py"; V="\$D/app/bin/ventana-mac"
if [ -x "\$V" ]; then exec "\$V" "$2" "\$D/app/$3.icns" -- "\$PY" "\$SU" $4 "\$@"; fi
exec "\$PY" "\$SU" $4 "\$@"
EOS
  chmod +x "$APP/Contents/MacOS/lanzar"
  [ -f "$DEST/app/$3.icns" ] && cp "$DEST/app/$3.icns" "$APP/Contents/Resources/icono.icns"
  cat > "$APP/Contents/Info.plist" <<EOP
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleName</key><string>$2</string>
<key>CFBundleDisplayName</key><string>$2</string>
<key>CFBundleIdentifier</key><string>es.islandcrew.$1</string>
<key>CFBundleExecutable</key><string>lanzar</string>
<key>CFBundleIconFile</key><string>icono</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleVersion</key><string>1.0</string>
<key>LSMinimumSystemVersion</key><string>11.0</string>
</dict></plist>
EOP
  xattr -dr com.apple.quarantine "$APP" 2>/dev/null || true
}
rm -rf "$HOME/Applications/Island Crew Suite.app"
crear_app suite "Island Crew Suite" icono ""
crear_app carta "Carta Viva Island Crew" carta "--abrir carta"
crear_app publicaciones "Publicaciones Island Crew" publicaciones "--abrir publicaciones"
crear_app anuncios "Anuncios Island Crew" anuncios "--abrir anuncios"
crear_app musica "Cabra Beats Island Crew" musica "--abrir musica"
[ -f "$DEST/app/icono.icns" ] || cp "$DEST/app/icono.icns" /dev/null 2>/dev/null || true
# Escritorio: solo el monitor de la suite. Los 4 programas se quedan en la carpeta Aplicaciones del usuario (para el Dock).
for n in "Carta Viva Island Crew" "Publicaciones Island Crew" "Anuncios Island Crew" "Cabra Beats Island Crew"; do [ -L "$HOME/Desktop/$n" ] && rm -f "$HOME/Desktop/$n"; done
ln -sfn "$HOME/Applications/Island Crew Suite.app" "$HOME/Desktop/Island Crew Suite" 2>/dev/null || true
echo " Instalado. Abriendo Island Crew Suite..."
open "$HOME/Applications/Island Crew Suite.app"
