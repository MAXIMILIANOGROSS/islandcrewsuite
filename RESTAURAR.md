# Restaurar la fábrica desde cero · Restore everything

Este repositorio guarda **todo el código** de las fábricas (Carta Viva, Publicaciones, Anuncios, Cabra Beats y sus motores de música, voz y vídeo), la suite, el Centro de inteligencia y los instaladores.
No guarda lo que es pesado o secreto; se recupera así:

| Pieza | Dónde está | Cómo se recupera |
|---|---|---|
| ACE-Step 1.5 (música) | https://github.com/ACE-Step/ACE-Step-1.5 · commit `ca1e85fe9430179831e6bc6be790c332190a3866` | `git clone` y `git checkout` de ese commit |
| Modelos de ACE-Step (~11 GB) | Carpeta `checkpoints` (Hugging Face: ACE-Step) | Se descargan con el propio ACE-Step en el primer arranque |
| RVC (voz clonada) | https://github.com/NevilPatel01/RVC-WebUI-MacOS · commit `61446231eb0d6def840cd2a3ba05d48d5cb8e69e` | `git clone` |
| Kokoro (voz) | paquete `kokoro` de PyPI | `pip install kokoro` en un entorno nuevo |
| Ollama | https://ollama.com | instalador oficial |
| ffmpeg | https://ffmpeg.org | instalador oficial o `brew install ffmpeg` |
| Claves (Gemini, Groq, YouTube, Meta) | **Nunca están en GitHub** | Se vuelven a pegar en la pantalla «Conexiones» y en el asistente |
| Clave privada de licencias | **Nunca en GitHub** | Copia de seguridad aparte (disco externo / gestor de contraseñas) |
| Música, cartas y vídeos creados | Disco externo T5 EVO, carpeta `IslandCrewAI` | Copia del disco; no caben en GitHub |

## Pasos
1. Clona este repositorio.
2. Instala Python 3.11, ffmpeg y los motores de la tabla.
3. Ejecuta `scripts/suite/construir-usb.sh` y `scripts/suite/comprimir-usb.sh` para generar los paquetes del pendrive.
4. Instala con `Instalar-Mac.command` (Mac) o `instalar.ps1` (Windows).
5. Pega tus claves en «Conexiones».

## Contenido
- `scripts/` · todo el código de fábricas, suite, instaladores, vídeo, voz, YouTube.
- `fabrica-local/` · el trabajador y planificador local de la fábrica de música.
- `docs-web/` · documentación de la web islandcrew.es.
