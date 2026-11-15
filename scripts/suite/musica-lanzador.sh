#!/bin/bash
# Abre Cabra Beats desde la suite instalada (sin rutas de desarrollador). Los motores viven en ~/IslandCrewAI.
AQUI="$(cd "$(dirname "$0")" && pwd)"; DATA="$HOME/IslandCrewAI"; mkdir -p "$DATA"
export MUSICA_DIR="${MUSICA_DIR:-$DATA/musica}"; mkdir -p "$MUSICA_DIR"
export RVC_DIR="${RVC_DIR:-$DATA/herramientas/RVC-WebUI-MacOS}"; export KOKORO_VENV="${KOKORO_VENV:-$DATA/kokoro-venv}"; export HF_HOME="${HF_HOME:-$DATA/hf-cache}"
export OLLAMA_MODELS="${OLLAMA_MODELS:-$HOME/.ollama/models}"; export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:$PATH"
PY=""
for c in "$DATA/ACE-Step-1.5/.venv/bin/python3" /Library/Frameworks/Python.framework/Versions/Current/bin/python3 /usr/local/bin/python3 "$(command -v python3)" /opt/homebrew/bin/python3; do
  [ -x "$c" ] && "$c" -c "import PIL" >/dev/null 2>&1 && { PY="$c"; break; }
done
[ -n "$PY" ] || { echo "Falta Python con Pillow: instala los motores (Instalar-Motores-Mac.command)." >> "$DATA/cabra-beats-app.log"; exit 1; }
exec "$PY" "$AQUI/scripts/cabra-beats-app.py" >> "$DATA/cabra-beats-app.log" 2>&1
