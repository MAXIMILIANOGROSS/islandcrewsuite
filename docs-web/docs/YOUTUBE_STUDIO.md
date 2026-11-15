# Island Crew YouTube Studio

Segunda oficina virtual de Island Crew, dedicada a YouTube. Base: [youtube-agent-skill](https://github.com/Jakeschincariol/youtube-agent-skill) (MIT, copia de la licencia en `THIRD_PARTY/youtube-agent-skill.LICENSE`).

## Auditoría del repositorio original
Skill de Claude con scripts Python deterministas (hooks, títulos, EDL de cortes, capítulos, retención, atípicos), 21 fórmulas de gancho y reglas de trabajo. No incluye base de datos, interfaz ni OAuth de YouTube.

## Qué está implementado
- `src/lib/youtube/*`: port a TypeScript de gancho, título, edición, capítulos, retención y atípicos, con tests de paridad frente a los scripts originales (`tests/youtube.test.mjs`).
- 13 agentes (`src/lib/youtube/agentes-yt.ts`): productor, investigador, guionista, títulos y miniatura, arte, realizador, editor, Shorts, SEO, retención, competencia/viralidad, comunidad y auditor. Forman parte de la plantilla de 43 de la oficina (`AGENTES_YT` los lista aparte) y tienen su propia sala «YouTube Studio» en el plano 2D, la vista isométrica y la 3D. Coordinados por CIRO, con las reglas comunes (no inventar, nada se publica sin aprobación humana, sin métricas inventadas) añadidas por `promptDe`.
- `/youtube-studio`: herramientas en el navegador (sin subir datos), ficha de canal en `localStorage`.

## Qué NO está (fases siguientes, sin simular)
- Proyectos, biblioteca y memoria de voz en base de datos (requiere SQL y separación por canal con RLS).
- YouTube Data/Analytics por OAuth opcional. Nunca publicación automática.
- FFmpeg/Remotion, audio y vídeo; planes y costes.
- Flujo multiagente con dependencias reales de tareas desde CIRO.

## Limitaciones
- La clasificación de fórmulas de gancho usa vocabulario en inglés (con apoyo de palabras en español).
- Las puntuaciones son guía de revisión, no predicción de visitas.
- Los agentes son perfiles de prompt, no IAs independientes; trabajan solo en la oficina administrativa.

## Nota técnica
En la base de datos las tareas de estos agentes se guardan con el área `crecimiento` (la restricción de `office_tasks.area` admite 4 áreas); la sala `youtube` existe solo en la interfaz (`areaDb()` hace la conversión).
