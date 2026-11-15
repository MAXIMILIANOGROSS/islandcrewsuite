# Fábrica de música automática

Estado: **REQUIERE_USUARIO** (instalar una vez el trabajador en el Mac) · coste 0 €.

1. Ejecuta el SQL 146 en Supabase.
2. En Vercel, el despliegue debe estar Ready. En GitHub, copia el workflow: `cp scripts/autonomia-ciclo.workflow.yml .github/workflows/autonomia-ciclo.yml` y súbelo.
3. En la Oficina: Publicar, Modo autónomo. Enciende el interruptor general, pon las canciones por día y guarda.
4. En el Mac, instala el trabajador (una vez):
   `mkdir -p ~/Library/LaunchAgents ~/Library/Logs && cp scripts/launchd/es.islandcrew.fabrica.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/es.islandcrew.fabrica.plist`
5. Requisitos mientras trabaja: Mac encendido, ACE-Step en 127.0.0.1:8001 y el T5 EVO conectado. Respeta la parada de emergencia. El registro del trabajador está en `~/Library/Logs/islandcrew-fabrica.log`.
6. Parar el trabajador: `launchctl unload ~/Library/LaunchAgents/es.islandcrew.fabrica.plist`.

## Estado del PC y motores (SQL 147)

El trabajador da señal cada minuto («PC encendido») y la Oficina lo muestra en Publicar, Modo autónomo. Los motores solo trabajan con el modo autónomo encendido, el interruptor de motores puesto y sin parada de emergencia. Para que el trabajador arranque ACE-Step u Ollama si están caídos, añade en `~/.islandcrew-env` líneas como `export ACESTEP_CMD="comando que arranca ACE-Step"` y `export OLLAMA_CMD="open -a Ollama"`.

## Subida automática a YouTube
Con **Modo autónomo → Publicar** encendido (y motores encendidos), cada canción que termina la Fábrica se sube a tu canal con `scripts/youtube-subir.py` (usa tu `~/IslandCrewAI/youtube/token.json` ya autorizado). Tope diario local: `YT_MAX_DIA` (por defecto 6). Se pide público y marcado como contenido sintético; si YouTube lo deja privado (proyecto de API sin auditar), se registra como privado, no como publicado. Con Publicar apagado no se sube nada.

## Instalación (fuera de Descargas) y espacio en disco
macOS impide que un servicio en segundo plano lea ~/Downloads. Instala el worker en `~/IslandCrewAI/worker/scripts/` (copia `fabrica-worker.py`, `fabrica-musica.py`, `youtube-subir.py`) y `public/cabra360/cabra-2.webp` en `~/IslandCrewAI/worker/public/cabra360/`; el servicio apunta ahí. Tras cambiar los scripts del repo, vuelve a copiarlos.
Espacio: el vídeo intermedio `_yt.mp4` se borra solo tras subirlo. Los audios ya subidos a YouTube se borran solos (solo si están en el registro de subidas, comprobado por huella). `LIBERAR_DIAS=7` en `~/.islandcrew-env` espera 7 días; `LIBERAR_DIAS=-1` lo desactiva. El panel Modo autónomo avisa si el disco interno baja de 10 GB.

## Actualización automática del Mac
El trabajador descarga solo la última versión de sus 3 scripts desde `islandcrew.es/api/oficina/worker-scripts` al arrancar, cada hora y cuando pulsas **Acciones → Actualizar el Mac ahora** en Modo autónomo (necesita el SQL 149). Valida la sintaxis antes de escribir, guarda copia `.bak` y se reinicia solo (launchd). Ya no hay que copiar nada a mano tras cada cambio.
