#!/bin/bash
# Abre Cabra Beats Personal (programa propio, sin web ni Vercel ni localhost:3000)
D="/Users/maximilianoolmos/Downloads/island-crew-web"; [ -d "$D" ] || D="$(cd "$(dirname "$0")/.." && pwd)"
ENV="$HOME/.islandcrew-env"; mkdir -p "$HOME/IslandCrewAI"
# Si una versión anterior desvió el trabajador a localhost, se deja como estaba
if grep -q "ISLANDCREW_URL=http://localhost:3000" "$ENV" 2>/dev/null && [ -f "$ENV.antes-de-cabra-beats" ]; then cp "$ENV.antes-de-cabra-beats" "$ENV"; launchctl kickstart -k "gui/$(id -u)/es.islandcrew.fabrica" >/dev/null 2>&1; fi
# Elige un Python que tenga Pillow (al abrirse desde la suite, el PATH cambia y puede salir uno sin Pillow)
PY=""
for c in "$HOME/IslandCrewAI/ACE-Step-1.5/.venv/bin/python3" /Library/Frameworks/Python.framework/Versions/Current/bin/python3 /usr/local/bin/python3 "$(command -v python3)" /opt/homebrew/bin/python3 /usr/bin/python3; do
  [ -x "$c" ] && "$c" -c "import PIL" >/dev/null 2>&1 && { PY="$c"; break; }
done
[ -n "$PY" ] || PY=$(command -v python3 || echo /usr/bin/python3)
exec "$PY" "$D/scripts/cabra-beats-app.py" >> "$HOME/IslandCrewAI/cabra-beats-app.log" 2>&1
