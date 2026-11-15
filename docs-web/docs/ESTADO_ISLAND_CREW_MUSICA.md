# Estado de Cabra Beats y la Fábrica (actualizado 2026-11-04)

Etiquetas: IMPLEMENTADO (código hecho y con tests) · PROBADO EN EL MAC (visto funcionando) · PENDIENTE · PARCIAL.

## Hecho
- Subida a YouTube desde cada caja de canción, con enlace real y aviso «ya subida»: PROBADO EN EL MAC (3 vídeos subidos el 2026-11-04).
- Solo cuenta como «subida» lo que tiene enlace registrado: IMPLEMENTADO.
- Canciones sin repetir; discos de 10 con título viral y capítulos numerados: IMPLEMENTADO.
- Vídeo lírico: IMPLEMENTADO (solo canciones nuevas con letra guardada; las antiguas se suben como vídeo normal).
- Autoría «IA creada por Maximiliano Olmos Sánchez para música y cine» en la descripción de cada vídeo y en la imagen (franja, si Pillow está instalado): IMPLEMENTADO.
- Arte por isla: universo visual propio (color, luz y silueta) para las 8 islas, en portadas de canción y de disco: IMPLEMENTADO (falta revisar a ojo).
- Biblioteca con audiolibros y vídeos con su enlace de YouTube: IMPLEMENTADO.
- Biblia de 200 personajes, relaciones, continuidad y piloto: IMPLEMENTADO (falta pulsar «Cargar mi Biblia»).
- Kitchen: recetas validadas, escenas con duración según la narración, tomas desde la biblioteca, Pexels y Pixabay: IMPLEMENTADO (falta el primer vídeo real en el Mac).

## Pendiente
- Vídeo estilo cine coherente con la letra (tomas libres de Pixabay/Pexels elegidas por las palabras de cada estrofa, montadas con ffmpeg, con el crédito del autor): PENDIENTE.
- Portada de isla conectada como imagen del vídeo de YouTube: PENDIENTE.
- Voz de meditaciones guiadas y podcast: PENDIENTE.
- Whisper para alinear la letra a la voz: PENDIENTE (opcional).
- Biblia viva, fases 6 a 9; Kitchen World Edition completa; jingles de 30 y 60 s; Shorts y miniaturas de canciones: PENDIENTE.

## Island Crew TV (plató virtual con secciones)
- IMPLEMENTED / TESTED LOCALLY: lógica en `src/lib/tv/motor.ts` (escaleta, agrupación de noticias, puerta editorial, guion sin invención, tiempo, plan del programa) con `tests/tv-motor.test.mjs`.
- IMPLEMENTED (sin probar en producción): plató con videowall, tomas por sección, clic en marcos para subir foto, panel «Island Crew TV» en `/podcast-studio/studio` (ensayo en pantalla con voces del navegador y radio con `beats_library`).
- NOT VERIFIED: GDELT y Open-Meteo (`/api/admin/tv`) no se pudieron llamar desde el entorno de desarrollo; hay que probarlos en Vercel.
- BLOCKED: emisión en directo a YouTube y audio en vivo (LiveKit). Las noticias aprobadas y la escaleta se guardan solo en el navegador (sin tablas SQL nuevas).
- Licencias: Open-Meteo gratuito = uso no comercial; AEMET OpenData necesita clave gratuita.
