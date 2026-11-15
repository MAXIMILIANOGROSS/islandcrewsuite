# CABRA BEATS · Auditoría Fase 1 y estado (1-nov-2026)

## Qué ya existía y se reutiliza (no se duplica)
- 60 cabras = 43 de la Oficina + 17 de Growth & Excellence (`TODOS` en `src/lib/oficina/agentes.ts`). Son perfiles de prompt sobre el mismo modelo, no procesos independientes.
- YouTube Studio: 13 agentes, herramientas en `/youtube-studio` (`src/lib/youtube/*`). Sin OAuth, sin publicación, sin proyectos en base de datos (ver `docs/YOUTUBE_STUDIO.md`).
- Estudio musical del navegador: `src/lib/music/*` (secuenciador, motor Web Audio, exportación WAV) en `/musica`. Sin voz.
- IA gratuita: `getProvider()`; límite de uso: `limiteGlobal`.
- Auditoría de licencias de música: `docs/AUDITORIA_MUNDO_MUSICA.md` (evita AGPL/BY-SA).

## Qué se construye en esta entrega (real y comprobable)
- `src/lib/beats/equipo.ts`: reparte funciones musicales entre las 60 cabras sin tocar sus perfiles (7 departamentos, determinista).
- `brief.ts`: Creative Director (idea → ficha: tipo, idioma es/en/de/it, género, BPM, tonalidad, estructura, instrucción para motor).
- `evaluacion.ts`: comprobaciones objetivas de la letra (idioma, longitud, estribillo, marca). No finge medir calidad musical.
- `motores.ts`: estado honesto de motores. `licencia.ts`: trazabilidad; nada nace autorizado para uso comercial.
- SQL 136 (`beats_projects`), API `/api/admin/beats`, panel «Cabra Beats» en la Oficina.

## Qué NO existe todavía (no se simula)
- Generación de canciones con voz: ACE-Step necesita GPU, no corre en Vercel. Ninguna canción con IA se ha generado.
- Autonomía de las cabras (propuestas, orquestador de tareas, memoria evolutiva), integración con YouTube por OAuth, biblioteca de audio en almacenamiento, vídeo.

## Siguiente (por orden)
1. Probar ACE-Step en tu Mac (comprobar chip y memoria) y escribir el adaptador `MusicGenerationProvider` hacia un worker local opcional.
2. Propuestas de las cabras (`origin = propuesta_cabra`) con aprobación tuya, usando el sistema de tareas existente.
3. Biblioteca de audio + versiones. 4. Enlace con YouTube Studio (proyectos compartidos, sin publicar solo).

## Riesgos
Licencia de modelos y pesos (revisar uno a uno), coste de GPU, calidad de pronunciación en alemán/italiano, derechos de lo generado.

## Mente de los creadores (cerebros) — estado
- `src/lib/beats/mente.ts`: hook score, guardia de originalidad (solo texto), curva de atención, efectos de atención, curva emocional, comparación de idiomas, mutación (máx. 2 variables), reglas con confianza/evidencia, Consejo de hits (pesos 20/15/15/15/10/10/10/5; desacuerdo ≥25 puntos → revisión). TESTED con `tests/cabra-beats-mente.test.mjs`. Son heurísticas de texto: no predicen éxito.
- `src/lib/beats/cerebros.ts`: los 25 cerebros con estado honesto (8 probados, el resto pendiente/sin probar/necesita YouTube).
- Sala «Cabra Beats · Creación musical» añadida a la oficina visual (suelo y rótulo; sin cabras nuevas: siguen siendo 60).
- No hay SQL nuevo. Pendiente: memoria persistente (tablas), melodía/armonía (music21), mezcla/mastering, HeartMuLa, YouTube.
