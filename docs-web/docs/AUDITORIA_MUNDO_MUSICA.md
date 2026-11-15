# Auditoría: juego FPS multijugador y música (Island Crew World)

Fecha: 2026-10-11. Licencias leídas de la página pública de cada repo; no es asesoría legal. Fechas de último commit no disponibles en las páginas leídas (mantenimiento NO VERIFICADO).

## Motor real del proyecto
Web: Next.js 15 + three.js 0.169 + @react-three/fiber, no Godot/Unity/Unreal. Mundo FPS en `src/components/FirstPersonWorld.tsx` (258 líneas, three directo), lógica en `src/lib/fps.ts`, `src/lib/downtown/*`, `src/app/mundo/*`. Red: Supabase Realtime (broadcast) en `src/lib/worldNet.ts` + `src/app/mundo/jugar/page.tsx`; LiveKit solo para llamadas.

## FPS (todos Godot → incompatibles con el stack web)
| Repo | Licencia | Veredicto |
|---|---|---|
| MilkAndBanana01/godot-fps-template | CC0-1.0 (assets Kenney) | No aplicable (Godot). Referencia de controles |
| TheDahoom/FPS-Multiplayer-Template | MIT (assets MIT/CC0; sonidos Freesound sin licencia indicada) | No aplicable. Referencia de arquitectura servidor/cliente |
| IYanel-DEV/FirstPerson-Multiplayer, toffesource/FPS-MP (Godot 3.1), devloglogan/MultiplayerFPSTutorial (294★), jonathaneeckhout/godot-fps-multiplayer (BSD-2), unfa/liblast (MIT, archivado → Codeberg) | MIT / MIT / MIT / BSD-2 / MIT | No aplicable |
| AetherRadar/operation-steel-tide | MIT + assets CC0 y CC BY 4.0 | No aplicable; es un shooter |
| PiePieDesign/eta-multiplayer | **LICENSE.md no legible; "assets no son abiertos"** | Descartar |
Los enlaces de «topics» no son repos. Ningún código Godot se puede ejecutar en la web actual sin cambiar de motor, lo cual el propio prompt prohíbe sin justificación.

## Música
| Recurso | Licencia | Decisión |
|---|---|---|
| Tone.js | MIT, 14,7k★ | Compatible. **No usado todavía**: el motor propio con Web Audio cubre piano/secuenciador sin dependencia |
| midi-js-soundfonts | código MIT; FluidR3_GM **CC BY 3.0**; MusyngKite y FatBoy **CC BY-SA 3.0** | Evitar BY-SA (obligaciones de compartir igual). FluidR3 posible con atribución, pesado |
| nbrosowsky/tonejs-instruments | código MIT; muestras **CC BY 3.0** | Posible con atribución visible |
| html-midi-player | BSD-2; depende de Magenta | Innecesario |
| ryohey/signal | MIT, 3.6k commits | Referencia de piano roll |
| maelangallais/Piano | MIT; sonidos sin licencia indicada | Referencia |
| MusicLab (zubenelakrab) | MIT, **pero usa Strudel (AGPL-3.0)** | **No integrar** |
| Strudel (Codeberg), strasbeat, chiptune-synth | **AGPL-3.0** | **Descartar** (obligaría a publicar Island Crew) |
| vast-websynth, cmraible/websynth | MIT | Referencias |
| waveform-playlist | MIT, peer deps tone | Futuro (edición multipista) |
| wavesurfer.js | BSD-3 | Futuro (forma de onda) |
| heartbeat (abudaan) | sin licencia, sin mantener | Descartar |
| MTG/jsap, midi-parser-js, WebAudioXML, web-audio-samples, osc.js, WAAX, ffmpeg.wasm (núcleo LGPL/GPL), Wave.js, arduino-audio-tools | **No se pudo leer la licencia** | NO VERIFICADO → no se integran |

## Decisión técnica
Sin sonidos de terceros: el piano usa **síntesis propia con Web Audio** (cero dependencias, cero licencias de muestras). Exportación WAV propia (`src/lib/music/wav.ts`), sin ffmpeg. Si más adelante se quieren muestras reales, solo CC0/CC BY con atribución.

## Estado de la implementación
- COMPLETADO Y PROBADO (tests): `notas.ts` (frecuencias, mapa de teclado), `proyecto.ts` (modelo, validación, eventos, límites), `wav.ts` (codificador).
- PENDIENTE: motor de audio de navegador (voces polifónicas, sustain), pantalla del estudio, guardado en Supabase (SQL), piano/estudio en el mundo 3D Downtown, colaboración, exportación desde la UI.

## Multijugador existente (hallazgos, sin cambios hechos)
- Es difusión por Supabase Realtime sin servidor autoritativo; las posiciones no se guardan.
- Solo se activa con `?multi=1` (decisión previa: pendiente de revisión legal).
- No hay punto de aparición distinto por jugador (hipótesis a confirmar al ejecutarlo).
- Causa raíz del «no funciona»: NO DETERMINADA; hipótesis principal, que se entra sin `?multi=1`.
