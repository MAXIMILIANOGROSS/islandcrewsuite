# Island Crew Suite · guía del propietario (no va en el pendrive)

## Montar el pendrive

1. `bash scripts/suite/construir-usb.sh` — crea `/Volumes/T5 EVO/IslandCrewAI/pendrive/Island Crew Suite - USB` (≈430 MB). Las descargas quedan en caché en `_descargas`.
2. Copia **el contenido completo** de esa carpeta a un pendrive formateado en **exFAT** (Windows y Mac lo leen).

## Dar licencias

`python3 scripts/suite/emitir-licencia.py "Casa Cecilia" carta,publicaciones [AAAA-MM-DD]`

- Imprime el texto de licencia y lo guarda en `/Volumes/T5 EVO/IslandCrewAI/licencias/emitidas/`.
- Una licencia por local. Sin fecha = no caduca.
- La **clave privada** está en `/Volumes/T5 EVO/IslandCrewAI/licencias/clave-privada.txt`. Haz dos copias fuera del pendrive; si la pierdes, no podrás emitir licencias que acepten los programas ya entregados. Nunca la copies al pendrive.
- Si algún día cambias la clave, hay que volver a construir y repartir el pendrive.

## Qué está probado y qué no

- Mac Apple Silicon: instalación en un usuario limpio simulado, asistente, licencia, y creación de vídeo, web, QR y flyer con el ffmpeg incluido. Probado.
- Windows: **no probado**. Hay que hacer una instalación en un Windows limpio antes de entregar a clientes.
- Mac con Intel: incluido, sin probar.
- Fábricas incluidas: Carta Viva y Publicaciones. Música no está en esta versión (necesita un motor de IA de varios GB y equipo potente).
- Publicaciones: probada la creación del calendario sin clave de IA (textos básicos), las piezas y el paquete diario; los textos con IA no se han probado con una clave real.
