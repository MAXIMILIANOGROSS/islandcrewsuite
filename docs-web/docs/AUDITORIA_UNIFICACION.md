# Auditoría de unificación — Island Crew

Fecha: 2026-10-09. Fase 1 (auditoría) y fase 2 (mapa) del plan de unificación. Solo inspección del repositorio: no se ha tocado producción. Lo que no se ha podido comprobar figura como **desconocido**. Estado de este documento: **propuesta, pendiente de aprobación del fundador**.

Complementa `docs/auditoria-ecosistema.md` (2026-10-07), que sigue vigente para identidad, empleo, vivienda y market.

## 1. Qué existe (comprobado en el repo)

**Stack.** Next.js 15.5, React 18, TypeScript, Three.js 0.169, `@react-three/fiber` 8 y `@react-three/drei` 9 (ya instalados), MapLibre, Supabase, jsPDF, QRCode, Resend, web-llm. Tests: 440 de 440 pasan (`node --test`) y `tsc` limpio, a fecha de hoy.

**Rutas públicas con página (resumen).** Producto y marca: `/`, `/inicio`, `/producto`, `/vision`, `/islas`, `/recorrido`, `/precios`, `/invertir`, `/blog`. Juego: `/mundo`, `/mundo/real`, `/mundo/jugar`, `/mundo/downtown`, `/mundo/panorama`, `/mundo/avatar`, `/explora`, `/lugar/[id]`. Empleo y empresas: `/swipe`, `/matches`, `/mensajes`, `/crearcurriculum`, `/cv/*`, `/empresas`, `/empresa/*`. Vivienda y market: `/housing/*`, `/marketplace/*`. Vida y bienestar: `/vida`, `/vida/alma`, `/vida/planes`. Administración: `/admin/*` (18 secciones). APIs: `assistant`, `cv-send`, `goat-chat`, `hiring`, `lead-notify`, `legal-notify`, `legal-resolve`, `life-council`, `life-listen`, `my-cv`, `npc`, `npc-group`, `places`, `soul-chat`, `soul-council`.

**Datos de lugares** (`public/data`): `corralejo-places.json`, `corralejo-places.overture.json`, `corralejo-businesses.json`, `corralejo-osm.raw.json`, `fuerteventura-places.json`, `fuerteventura-coast.json`, `lobos-coast.json`, `zones/`, y `asset-registry.json` con política de licencias comprobada por test.

**Documentación**: unos 40 documentos en `docs/` (≈155 KB), entre ellos `design-system.md`, `game-design-gdd.md`, `art-direction-world.md`, `island-crew-world-architecture.md`, `island-crew-world-content-rights.md`, `island-crew-location-privacy.md`, `ASSET-LIBRARY.md` y `AGENTES.md`.

**Agentes**: 32 en `src/lib/agents/registry.ts` (30 + Accesibilidad + Licencias). Solo son especificación; ninguno se ejecuta solo (el informe diario no está activado).

## 2. Hallazgos y contradicciones

| # | Hallazgo | Evidencia | Gravedad |
|---|---|---|---|
| H1 | **Dos paletas en conflicto.** El sistema de diseño vigente usa marino #0A1A33, amarillo #FFD400, crema #FDFBF4 y arena #F4E3B8. El prompt propone azul atlántico #103B4A, turquesa #31B7B0, arena #E8D8B7, blanco cálido #F7F4EC, coral #FF725E y grafito #202B30. | `docs/design-system.md`, `src/lib/brand/tokens.ts` | Alta (decisión de marca) |
| H2 | **Tres sistemas de misiones/actividades.** `crew/missions.ts` (decisiones por arquetipo), `quests.ts` (objetivos del HUD, "primeros pasos") y el SQL `38_MISIONES_JUEGO`. No consta un contrato común (id, requisitos, éxito/fallo, estado de publicación). | `src/lib/crew/missions.ts`, `src/lib/quests.ts` | Alta |
| H3 | **Varias capas de NPC.** `npc/cast`, `personas`, `deep`, `emergent`, `factory`, `group`, `soul/*`, `/npc-factory`. No consta una ficha única por NPC con id estable que alimente juego, web y panel. | `src/lib/npc/*` | Alta |
| H4 | **Varias fuentes de lugares.** Hay al menos cinco ficheros de lugares/negocios. Comprobado el 2026-10-09: el maestro `corralejo-places.json` (453 lugares) lo usan juego, mapa, `/lugar/[id]`, sitemap y asistente; 320 ids son de OSM (`osmn/osmw/osmr`) y 133 son UUID de Overture. 320 de los 360 lugares de `fuerteventura-places.json` dentro de Corralejo comparten id con el maestro. **Riesgo:** 26 lugares fusionados (OSM + Overture) llevan UUID aunque tengan origen OSM, así que su id podría cambiar al regenerar. Mitigación: test con instantánea de ids. | `public/data/*`, `scripts/build-unified-venues.py` | Alta |
| H5 | **Muchas rutas que se solapan.** `/mundo`, `/mundo/jugar`, `/mundo/real`, `/mundo/downtown`; y `/vision`, `/producto`, `/islas`, `/recorrido` cuentan partes de lo mismo. | listado de rutas | Media |
| H6 | **Analítica sin esquema del universo.** Los eventos que existen son genéricos (`page_view`, `app_click`, `lead_created`, `pricing_view`, `partner_click`, `referral_click`, `experiment_*`). Ninguno de los eventos propuestos (`recorrido_web_iniciado`, `juego_iniciado`, etc.) existe. | búsqueda de `track(` | Media |
| H7 | **Estado de funciones sin registro central.** Los estados `disponible / demostración / en desarrollo` se escriben a mano en el manifiesto del recorrido y en textos sueltos. | `public/recorrido/manifest.json` | Media |
| H8 | **Imágenes del recorrido.** Son ilustraciones de marca reutilizadas (`hero*.jpg`, `cocina.jpg`, `eventos.jpg`); algunas escenas repiten imagen. No son capturas del juego. Origen confirmado por el fundador: generadas por él con una herramienta de IA; ya registradas en `asset-registry.json` como propias. Falta confirmar las condiciones de uso comercial de esa herramienta. | `public/recorrido/manifest.json` | Media |
| H9 | **Archivo gigante.** `RealTownWorld.tsx` (≈239 KB, 867 líneas largas) concentra el mundo jugable. Riesgo de mantenimiento. | `src/components` | Media |
| H10 | **Verificación visual pendiente.** Los cambios de marca de HUD, vestuario, decisión de crew, avatar y bienvenida pasan tipos y tests, pero **no se han visto renderizados**. | — | Media |

Lo que **no** es un problema: `@react-three/fiber` y `drei` ya están instalados, así que no hace falta añadir ninguna librería 3D. Colyseus y otras dependencias externas no se han adoptado.

## 3. Prioridades (propuesta)

1. **P1 — Decidir paleta (H1).** Ver D-001 en `DECISIONES.md`.
2. **P1 — Contrato de lugar y de NPC (H3, H4).** Primero documentar los ids que ya existen y qué fichero manda; después, validación por test.
3. **P2 — Contrato común de misión (H2)** como tipo TypeScript más un test, sin migrar todavía las misiones actuales.
4. **P2 — Registro de estado de funciones (H7):** un único archivo que alimente web y recorrido.
5. **P2 — Esquema de analítica (H6):** definir solo eventos de funciones reales.
6. **P3 — Registrar procedencia de imágenes (H8).**
7. **P3 — Trocear `RealTownWorld.tsx` (H9)** por módulos, con tests de no regresión.

## 4. Primer conjunto de cambios verificables

Todos reversibles, sin tocar producción y sin dependencias nuevas:

- C1. `src/lib/universe/status.ts`: registro único de estado de funciones + test que impide que el manifiesto del recorrido use un estado no registrado.
- C2. `src/lib/universe/contracts.ts`: tipos `Place`, `Npc`, `Quest` (campos del prompt, secciones 4–6) sin migrar datos.
- C3. Test que lista los ids de lugares de cada fichero de `public/data` y falla si hay duplicados dentro de un mismo fichero.
- C4. Registrar en `asset-registry.json` la procedencia de las imágenes del recorrido, cuando el fundador confirme su origen.

## 5. Plan de pruebas

Existente: 440 tests de lógica. Falta: pruebas visuales (capturas) de las pantallas restyled, Lighthouse móvil sobre `/recorrido` y `/mundo/real`, revisión de accesibilidad (contraste AA, teclado) y prueba con `prefers-reduced-motion`.

## 6. Riesgos

Marca incoherente si no se decide H1; contenidos contradictorios entre NPC, web y misiones (H2–H3); derechos de imágenes sin confirmar (H8); promesas de la web por delante del juego (H7); disco del Mac casi lleno (1,1 GiB libres) que ya bloqueó builds.
