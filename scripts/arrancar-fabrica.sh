#!/bin/bash
# Diagnostica y arranca la fábrica de música en tu Mac: ACE-Step (puerto 8001), disco T5 EVO y worker. No borra nada.
echo "== 1. Disco T5 EVO"; [ -d "/Volumes/T5 EVO" ] && echo "OK conectado" || echo "FALTA: conecta el disco T5 EVO"
echo "== 2. Fichero de claves"; [ -f ~/.islandcrew-env ] && echo "OK ~/.islandcrew-env" || echo "FALTA ~/.islandcrew-env (CRON_SECRET e ISLANDCREW_URL)"
echo "== 3. ACE-Step (8001)"
if curl -s -m 4 -o /dev/null http://127.0.0.1:8001/health; then echo "OK responde"; else
  echo "No responde: arrancando en segundo plano (tarda 1-3 min en cargar modelos)…"
  ( cd ~/IslandCrewAI/ACE-Step-1.5 && PATH="$HOME/.local/bin:$PATH" nohup ./start_api_server_macos.sh > ~/IslandCrewAI/acestep.log 2>&1 & )
fi
echo "== 4. Worker"
if pgrep -f fabrica-worker.py >/dev/null; then echo "OK en marcha"; else
  echo "Arrancando worker…"; ( cd "$(dirname "$0")/.." && nohup python3 scripts/fabrica-worker.py > ~/IslandCrewAI/worker.log 2>&1 & )
fi
echo; echo "Registros: tail -f ~/IslandCrewAI/acestep.log   y   tail -f ~/IslandCrewAI/worker.log"
echo "Luego, en la web: Oficina → interruptor de motores ENCENDIDO."
