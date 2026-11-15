# Subida a YouTube (privada) · Cabra Beats

Estado: **REQUIRES_USER** (necesita que autorices tu canal una vez) · script `scripts/youtube-subir.py` · coste 0 €.

## Qué hace
Sube SOLO los archivos que le nombres, siempre como **privados** y marcados como contenido sintético. Si es audio, crea un vídeo con una imagen fija. No sube dos veces lo mismo (huella sha256). Máximo 5 por ejecución.

## Preparación (una sola vez)
1. Entra en https://console.cloud.google.com con tu cuenta del canal y crea un proyecto (nombre libre, p. ej. «Island Crew Media»).
2. Menú **APIs y servicios → Biblioteca** → busca **YouTube Data API v3** → **Habilitar**.
3. **APIs y servicios → Pantalla de consentimiento de OAuth** → tipo **Externo** → rellena nombre y tu correo → en **Usuarios de prueba** añade tu propio correo de Google.
4. **Credenciales → Crear credenciales → ID de cliente de OAuth** → tipo **Aplicación de escritorio** → **Descargar JSON**.
5. En el Terminal:
```
mkdir -p ~/IslandCrewAI/youtube
mv ~/Downloads/client_secret_*.json ~/IslandCrewAI/youtube/client_secret.json
chmod 600 ~/IslandCrewAI/youtube/client_secret.json
```
Nunca pegues ese archivo en un chat.

## Uso
Ensayo sin subir nada:
```
cd ~/Downloads/island-crew-web
python3 scripts/youtube-subir.py --seco "/Volumes/T5 EVO/IslandCrewAI/musica/SONG_002_completa_v1.wav"
```
Subida real (la primera vez se abre el navegador para autorizar):
```
python3 scripts/youtube-subir.py --titulo "Island Crew · Canción de verano" "/Volumes/T5 EVO/IslandCrewAI/musica/SONG_002_completa_v1.wav"
```
Después entra en YouTube Studio → Contenido, revisa y decide si la haces pública.

## Límites conocidos (verificar en la documentación oficial de YouTube)
- La cuota gratuita de la API permite pocas subidas al día.
- Con la app en modo «pruebas», el permiso puede caducar a los 7 días: el script vuelve a pedir autorización.
- Los proyectos de API sin auditar pueden forzar que los vídeos queden privados; es compatible con este flujo.
- YouTube puede limitar la monetización del contenido repetitivo o genérico: sube solo lo aprobado.
