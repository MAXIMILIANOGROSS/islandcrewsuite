#!/bin/bash
# CABRA BEATS PERSONAL: un clic arranca TODO en tu Mac (web local + trabajador + música) y abre Cabra Beats. Sin Vercel.
D="/Users/maximilianoolmos/Downloads/island-crew-web"; [ -d "$D" ] || D="$(cd "$(dirname "$0")/.." && pwd)"
URL="http://localhost:3000"; LOG="$HOME/IslandCrewAI/web-local.log"; ENV="$HOME/.islandcrew-env"; mkdir -p "$HOME/IslandCrewAI"
aviso() { osascript -e "display notification \"$1\" with title \"Cabra Beats\"" >/dev/null 2>&1; }
vivo() { c=$(curl -s -o /dev/null -w "%{http_code}" -m 4 "$URL/" 2>/dev/null); [ "$c" = "200" ] || [ "$c" = "307" ] || [ "$c" = "308" ]; }
aviso "Arrancando… puede tardar un minuto la primera vez."
# 1) El trabajador del Mac habla con la web LOCAL (se guarda copia del archivo original una sola vez)
if grep -q "ISLANDCREW_URL=https://islandcrew.es" "$ENV" 2>/dev/null; then
  [ -f "$ENV.antes-de-cabra-beats" ] || cp "$ENV" "$ENV.antes-de-cabra-beats"
  sed -i '' 's|ISLANDCREW_URL=https://islandcrew.es|ISLANDCREW_URL=http://localhost:3000|' "$ENV"
  launchctl kickstart -k "gui/$(id -u)/es.islandcrew.fabrica" >/dev/null 2>&1
fi
# 2) La web local (si no está ya en marcha)
if ! vivo; then
  nohup /bin/zsh -lc "cd '$D' && exec npm run dev" >> "$LOG" 2>&1 &
  disown 2>/dev/null
  for i in $(seq 1 45); do sleep 2; vivo && break; done
fi
if ! vivo; then aviso "No arrancó la web local. Mira ~/IslandCrewAI/web-local.log"; exit 1; fi
curl -s -o /dev/null -m 120 "$URL/oficina" >/dev/null 2>&1   # precalienta la pantalla para que abra rápido
aviso "Listo. Se abre Cabra Beats."
# Se abre como una ventana propia de software (sin barra del navegador) si hay Chrome; si no, en el navegador normal
if [ -d "/Applications/Google Chrome.app" ]; then open -na "Google Chrome" --args --app="$URL/oficina?vista=beats"; else open "$URL/oficina?vista=beats"; fi
