# Auditoría de la productora autónoma (Fase 1) · estados honestos

Evidencia = lo que hay en el repositorio y en los tests locales. Nada está marcado «VERIFICADO EN PRODUCCIÓN» porque no se ha comprobado desde aquí.

| Función | Estado | Evidencia |
|---|---|---|
| Canciones y jingles (cola `fabrica_cola`, worker del Mac) | PROBADO LOCALMENTE | scripts/fabrica-worker.py, fabrica-musica.py, tests |
| Jingles 5/20 s, perfiles, evaluador, firmas | PROBADO LOCALMENTE | src/lib/beats/jingles.ts, jingleEval.ts, firmas.ts (SQL 155 sin ejecutar) |
| Audiolibros (esquema, capítulos, narración, meditaciones) | PROBADO LOCALMENTE | audiolibro.ts; voz Kokoro sin instalar, respaldo `say` |
| Vídeo lírico por canción | PROBADO LOCALMENTE | scripts/video-lirico.py (sincronía aproximada) |
| Subida a YouTube privada + programación | IMPLEMENTADO | scripts/youtube-subir.py |
| Analítica de YouTube | BLOQUEADO hasta reautorizar y activar la API | youtube-analytics.py; impresiones/CTR sin verificar |
| Media HQ (estado, ajustes, parada) | IMPLEMENTADO (SQL 154 sin ejecutar) | api/admin/media/hq |
| Fábrica creativa y Storyverse (ideas, versiones, derivaciones, personajes) | PROBADO LOCALMENTE (SQL 156 sin ejecutar) | fabricaCreativa.ts, tests |
| Puntuación de calidad de 100 puntos con bloqueos críticos | PROBADO LOCALMENTE (solo la regla; sin conectar al pipeline) | controlCalidad.ts |
| Instagram, Facebook, TikTok, LinkedIn, Spotify: publicación | PENDIENTE (permisos, cuentas profesionales y revisión de apps sin verificar) | — |
| Vídeo cinematográfico, Shorts editados, miniaturas automáticas | PENDIENTE | solo vídeo lírico y portadas |
| Control de calidad de audio automático (picos, silencios, LUFS) | PENDIENTE de conectar | loudnorm y compactación de silencios existen en el worker |
| Revisor independiente | PENDIENTE: hoy la nota la pone una persona |
| Coste por obra e ingresos atribuibles | PENDIENTE (todo es coste cero; no hay medición) |

Siguiente fase: conectar `evaluarQC` a la cola (obra → estados del pipeline → bloqueo/publicación), medir audio real con ffmpeg y mostrar el resultado en Media HQ.
