#!/bin/bash
# Deja listo el pendrive COMPLETO (suite + todos los motores) a partir de la edición ligera ya construida.
# Uso: bash armar-completa.sh   (después de construir-usb.sh y comprimir-usb.sh)
set -e
SUITE="$(cd "$(dirname "$0")" && pwd)"; S="$SUITE/.."
BASE="/Volumes/T5 EVO/IslandCrewAI/pendrive"; LIG="$BASE/Island Crew Suite - LIGERO"; COM="$BASE/Island Crew Suite - PENDRIVE 100G"
[ -d "$LIG/Paquetes" ] || { echo "Primero ejecuta construir-usb.sh y comprimir-usb.sh"; exit 1; }
mkdir -p "$COM"
rsync -a --delete "$LIG/Paquetes/" "$COM/Paquetes/"; rsync -a "$LIG/Mac/" "$COM/Mac/"; rsync -a "$LIG/Windows/" "$COM/Windows/"
[ -d "$LIG/Licencias" ] && rsync -a "$LIG/Licencias/" "$COM/Licencias/"
cp "$SUITE/instaladores/Instalar-Motores-Mac.command" "$COM/Mac/"; chmod +x "$COM/Mac/Instalar-Motores-Mac.command"
M="$COM/Motores/app-musica"; rm -rf "$M"; mkdir -p "$M/scripts"
cd "$S" && rsync -a --exclude __pycache__ cabra-beats-app.py cabra-beats-app.html cabra-avatar.html cabra-beats-logo.png cancion-local.py estilos-catalogo.py estilos-web.json fabrica-musica.py portada-local.py video-clip.py video-lirico.py video-cine.py video-marca.py voz-clonada.py voz-gemini.py kokoro-voz.py youtube-subir.py qc-audio.py reel-musical.py kitchen-intro.py fuentes vendor-avatar "$M/scripts/"
cp "$SUITE/musica-lanzador.sh" "$M/cabra-beats-lanzar.sh"; chmod +x "$M/cabra-beats-lanzar.sh"
echo "Listo: $COM"; du -sh "$COM"
