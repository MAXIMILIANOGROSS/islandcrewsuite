# ACE-Step 1.5 en tu Mac mini M4 (probado el 1-nov-2026)

- Código y entorno: `~/IslandCrewAI/ACE-Step-1.5` (disco interno, unos pocos GB). Modelos (≈11 GB): `/Volumes/T5 EVO/IslandCrewAI/checkpoints` (enlace simbólico). El disco T5 EVO es exFAT: por eso el entorno no va allí.
- Arrancar: `cd ~/IslandCrewAI/ACE-Step-1.5 && PATH="$HOME/.local/bin:$PATH" ./start_api_server_macos.sh` (API en http://127.0.0.1:8001). Parar: `pkill -f start_api_server_macos`.
- Config usada: LM `acestep-5Hz-lm-0.6B`, DiT `acestep-v15-turbo`, backend MLX, sin comprobar actualizaciones.
- Prueba real: «TEST SONG 001» (español, 30 s, WAV 48 kHz estéreo), ≈90 s de generación. Archivo en `/Volumes/T5 EVO/IslandCrewAI/musica/TEST_SONG_001_v1.wav`.
- Qué NO está comprobado: calidad musical, pronunciación en alemán/italiano, canciones largas, variaciones. Hay que escucharlo.
- Licencia: MIT según repo y ficha del modelo; no es garantía jurídica sobre lo generado (ver `licencia.ts`).
- Vercel no puede llegar a `localhost:8001`: la generación se lanza desde tu Mac (`ACESTEP_URL=http://127.0.0.1:8001`).
