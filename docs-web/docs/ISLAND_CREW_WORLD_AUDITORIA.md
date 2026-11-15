# Island Crew World — Auditoría (Prompt 00)

Fecha: 2026-10-16. Alcance: lectura del repositorio. NO se ha ejecutado el juego ni medido FPS; todo lo marcado "verificado" significa verificado en código y en la batería de tests (911 pasan), no jugado.

## Motor y arquitectura
- Web: Next.js 15 + three 0.169 + @react-three/fiber/drei. Decisión (usuario): seguir en la web. No hay Unity/Unreal.
- Mundo principal: `src/components/RealTownWorld.tsx` (937 líneas, casi todo en un único componente/efecto), ruta `/mundo/real`. Prototipo antiguo: `FirstPersonWorld.tsx` (calle pequeña, `/mundo/jugar`).
- Datos reales: `public/data/*` (OSM Corralejo, costa de Fuerteventura y Lobos, negocios, nombres de calles). `src/lib/geo.ts` convierte a mundo 3D.
- Lógica de apoyo en `src/lib/`: avatar, crew (misiones, encuentros, trajes), npc (cerebro, personas, chat), downtown, venues, lobos, cars, ships, sfx, world*, lfg (recompensas), gamesync.

## Inventario (según código)
| Área | Estado | Notas |
|---|---|---|
| Mundo de Corralejo desde OSM (edificios, calles, costa, puertas de negocios) | Implementada, no jugada aquí | Fachadas procedurales, no modelos hechos a mano. |
| Primera persona (WASD + ratón, pointer lock, salto) | Implementada | Existe también control táctil (`TouchControls`). |
| Moto, coche, bici, barco, nadar, Isla de Lobos | Implementada parcialmente | Existen en código; sin medir. Buceo propiamente dicho: no consta. |
| NPC (≈144 peatones, patinadores, perros, gaviotas) y chat con personas | Implementada | Cuerpos simples (`figure`), animación básica. Chat con IA/estructurado en `npc/`. |
| Interacción (E, puertas, recoger, hablar) | Implementada, pero no unificada | Lógica repartida en el mismo componente, sin un sistema común reutilizable (Prompt 05 pendiente). |
| Restaurantes/locales interiores | Implementada parcialmente | `venues.ts` (283 líneas): interiores genéricos con mesas, barra, caja, almacén. Interior de cocina profesional: no. |
| Misiones de hostelería | Implementada, simple | 3–4 pasos tipo "recoge → sirve → cobra" (`venues.ts`). Sin reglas de evaluación ni errores observables. |
| Cocina (lomo a la pimienta), barista, coctelería | No implementada | Solo existen recetas en `/chef` (texto). |
| Academy → juego → resultado verificable | No implementada | No hay contrato ni adaptador. |
| Audio | Implementada (sintetizada con WebAudio: mar, gente, motor, pájaros) | Sin grabaciones reales ni mezcla por categorías. |
| Progresión | Parcial: XP/misiones (`lfg`, `game_complete_mission` RPC) | Falta anti-duplicado verificado y separación recreativo/profesional. |
| Guardado | Parcial: localStorage + RPC | Sin pantalla de continuar partida. |
| HUD | Parcial: `components/hud`, paneles sueltos | Muchas ventanas independientes. |
| Calidad gráfica | Estilo low-poly/procedural, sin PBR real ni perfiles gráficos | Hay `finish()` para materiales y HDR. |

## Riesgos
1. Monolito: un componente de ~940 líneas con cierres enormes. Cada fase nueva aumenta el riesgo de romper lo que funciona. Hay que extraer módulos (interacción, misiones, restaurantes) antes de añadir cocina.
2. Licencias de assets: `public/world/CREDITS.txt` indica Michelle/Soldier (Mixamo) y ejemplos de three.js "revisar licencias antes de uso comercial". Hay que resolverlo antes de monetizar.
3. Realismo AAA: no alcanzable con presupuesto cero en navegador. Objetivo realista: estilo cuidado tipo las capturas de cocina estilizada (no fotorrealismo).
4. Rendimiento en móvil: 144 NPC + edificios procedurales no medidos.
5. Edificios y locales: son reales en OSM; los interiores y personal son ficticios. Mantener la etiqueta "demo/ficticio".

## Plan por fases (cada una cierra con tests y prueba manual)
0. Esta auditoría + medir FPS/memoria reales en móvil y escritorio.
1. Extraer del monolito: sistema de interacción único y gestor de misiones con datos separados (Prompts 01, 05, 08).
2. Cocina interactiva con reglas deterministas: lomo a la pimienta, evaluación y resultado repetible (Prompt 09), como módulo aparte.
3. Contrato Academy ↔ juego: id de sesión, rúbrica versionada, resultado validado en servidor y sin duplicados (Prompt 12).
4. Servicio de sala y cafetería (Prompts 10, 11) reutilizando el sistema de fases.
5. Pulido: HUD y menús (14), audio (15), progresión (16), rendimiento (17), QA (18), revisión final (19).
Los Prompts 02, 03, 04, 06, 07 y 13 ya tienen base; se tratan como mejoras sobre lo existente, no como reconstrucción.

## Criterios de aceptación de esta fase
- Inventario entregado: sí. Estado de compilación: build y 911 tests correctos en `main`. Ejecución del juego: pendiente de prueba manual y medición.
