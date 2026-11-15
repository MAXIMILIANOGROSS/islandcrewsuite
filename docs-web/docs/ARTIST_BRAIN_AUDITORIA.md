# Cabra Artist Brain · auditoría y estado

## Lo que ya existía (reutilizado)
Motor de síntesis del navegador (`src/lib/music/`: motor, generador de 6 estilos, WAV), tonalidad/escala, efectos, arreglos por secciones, asistente de producción con 16 cerebros de estilo (`artistas.ts`), 25 cerebros musicales con estados honestos (`cerebros.ts`), equipo de las 85 cabras (`equipo.ts`), evaluación de letras (`evaluacion.ts`), fábrica de música del Mac (ACE-Step), biblioteca viva (SQL 139), cola de tareas (`beats_tasks`, SQL 137).

## Lo que falta (según el documento)
Conocimiento estructurado, prosodia española, estados expresivos, memoria con pgvector, MIDI, crítica independiente con tres evaluadores, experimentos con línea base y regresiones, proyectos autónomos con aprobación, centro de control completo.

## Fase 1 (esta entrega)
IMPLEMENTADA y probada en local: `src/lib/beats/artista.ts`, `src/app/api/admin/beats/artista/route.ts`, `src/components/ArtistaCerebro.tsx`, SQL 141, `tests/artista-brain.test.mjs`. No verificada en producción hasta ejecutar el SQL 141 y desplegar.

## Decisiones de diseño
- La personalidad son 8 parámetros de comportamiento creativo; cada uno cambia valores concretos de generación (escalas permitidas, compases, arreglo por secciones).
- Un cambio de identidad exige una nota de 12+ letras y crea una versión nueva; restaurar también crea una versión nueva. El historial nunca se borra.
- Los cambios «por aprendizaje» no se aceptan todavía: solo los hace un humano, hasta que existan evaluaciones reales (fase 7-8).
- No se instala LangGraph ni se usa fine-tuning: el orquestador y la cola actuales cubren esta fase.
