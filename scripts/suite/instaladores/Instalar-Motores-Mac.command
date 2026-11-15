#!/bin/bash
# Island Crew · Instala los motores de música y voz (Cabra Beats) en este Mac. Hazlo DESPUÉS de instalar la suite.
cd "$(dirname "$0")"; PEN="$(cd .. && pwd)"; MOT="$PEN/Motores"
APP="$HOME/Library/Application Support/IslandCrewSuite/programa/app"; DATA="$HOME/IslandCrewAI"
[ -n "$1" ] && { mkdir -p "$1" && { [ -e "$DATA" ] && [ ! -L "$DATA" ] || ln -sfn "$1" "$DATA"; }; }
mkdir -p "$DATA"; LOG="$DATA/instalar-motores.log"; : > "$LOG"
paso() { echo; echo "== $1"; }
falla() { echo "   ✗ $1 (detalle en $LOG)"; }
echo "ISLAND CREW · Motores de música y voz"
[ -d "$MOT" ] || { echo "No encuentro la carpeta Motores junto a la carpeta Mac."; read -p "Pulsa Intro para cerrar"; exit 1; }
[ -d "$APP" ] || { echo "Primero instala la suite con Instalar-Mac.command."; read -p "Pulsa Intro para cerrar"; exit 1; }
[ "$(uname -m)" = "arm64" ] || { echo "La música necesita un Mac con chip Apple (M1 o superior). Este Mac seguirá con Carta Viva, Publicaciones y Anuncios."; read -p "Pulsa Intro para cerrar"; exit 0; }
RAM=$(( $(sysctl -n hw.memsize) / 1073741824 )); [ "$RAM" -ge 16 ] || { echo "La música necesita 16 GB de memoria y este Mac tiene $RAM GB. Seguirás con las otras fábricas."; read -p "Pulsa Intro para cerrar"; exit 0; }
LIBRE=$(df -g "$DATA" | awk 'NR==2{print $4}'); [ "$LIBRE" -ge 45 ] || { echo "Faltan GB libres: hacen falta 45 y hay $LIBRE. Libera espacio o ejecuta: bash Instalar-Motores-Mac.command /Volumes/TuDiscoExterno/IslandCrewAI"; read -p "Pulsa Intro para cerrar"; exit 0; }
export PATH="$HOME/.local/bin:$PATH"

paso "1/6 Herramienta de instalación (uv)"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh 2>>"$LOG" | sh >>"$LOG" 2>&1
command -v uv >/dev/null || { falla "No se pudo instalar uv (hace falta internet)"; read -p "Pulsa Intro para cerrar"; exit 1; }

paso "2/6 Motor de música (ACE-Step y sus modelos, unos 11 GB)"
mkdir -p "$DATA/ACE-Step-1.5/checkpoints"
rsync -a --exclude .venv --exclude checkpoints "$MOT/acestep/" "$DATA/ACE-Step-1.5/" >>"$LOG" 2>&1
rsync -a "$MOT/checkpoints/" "$DATA/ACE-Step-1.5/checkpoints/" >>"$LOG" 2>&1
(cd "$DATA/ACE-Step-1.5" && uv sync >>"$LOG" 2>&1) && echo "   ✓ Listo" || falla "No se pudo preparar el motor de música"

paso "3/6 Voz (Kokoro)"
rsync -a "$MOT/hf-cache/" "$DATA/hf-cache/" >>"$LOG" 2>&1
uv venv --python 3.11 "$DATA/kokoro-venv" >>"$LOG" 2>&1 && uv pip install --python "$DATA/kokoro-venv/bin/python" "kokoro==0.9.4" "misaki==0.9.4" soundfile spacy numpy torch huggingface_hub >>"$LOG" 2>&1 && echo "   ✓ Listo" || falla "Kokoro no se instaló (la música funciona, pero sin esa voz)"

paso "4/6 Voz clonada (RVC, opcional)"
RV="$DATA/herramientas/RVC-WebUI-MacOS"; mkdir -p "$RV"
rsync -a --exclude .venv --exclude logs "$MOT/rvc/" "$RV/" >>"$LOG" 2>&1
(uv venv --python 3.10 "$RV/.venv" && uv pip install --python "$RV/.venv/bin/python" -r "$RV/requirements/main.txt") >>"$LOG" 2>&1 && echo "   ✓ Listo" || falla "RVC no se instaló (la voz clonada no estará disponible)"

paso "5/6 Letras con IA local (Ollama)"
if [ ! -d "/Applications/Ollama.app" ] && [ ! -d "$HOME/Applications/Ollama.app" ]; then
  curl -L -o /tmp/Ollama.zip https://ollama.com/download/Ollama-darwin.zip >>"$LOG" 2>&1 && mkdir -p "$HOME/Applications" && unzip -qo /tmp/Ollama.zip -d "$HOME/Applications" >>"$LOG" 2>&1 && rm -f /tmp/Ollama.zip
fi
mkdir -p "$HOME/.ollama/models"; rsync -a "$MOT/ollama-models/" "$HOME/.ollama/models/" >>"$LOG" 2>&1
{ [ -d "/Applications/Ollama.app" ] || [ -d "$HOME/Applications/Ollama.app" ]; } && echo "   ✓ Listo" || falla "Ollama no se instaló (las letras con IA local no estarán disponibles; las de Gemini sí)"

paso "6/6 Cabra Beats"
rm -rf "$APP/musica"; mkdir -p "$APP/musica"; rsync -a "$MOT/app-musica/" "$APP/musica/" >>"$LOG" 2>&1; chmod +x "$APP/musica/cabra-beats-lanzar.sh"
[ -x "$APP/musica/cabra-beats-lanzar.sh" ] && echo "   ✓ Listo" || falla "No se pudo instalar Cabra Beats"
echo; echo "Terminado. Abre «Island Crew Suite» y pulsa Cabra Beats."; echo "Si algo salió mal, el detalle está en: $LOG"
read -p "Pulsa Intro para cerrar"
