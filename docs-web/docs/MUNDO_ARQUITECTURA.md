# Island Crew World — arquitectura del motor y del mundo

Estado: octubre 2026. Motor actual: **three.js 0.169 en el navegador** (Next.js 15). Decisión: no migrar a Unreal/Unity sin una prueba de viabilidad (se perderían web, cuentas y carrera). Un cliente Unreal independiente sería un proyecto aparte que se conectaría por API.

## Capas
1. **Reglas (puras, con tests)**: `src/lib/kitchen/*`, `src/lib/carrera/*`. Recetas, casos, puntuación, cocción (`coccion.ts`), carrera. No dependen de three.js.
2. **Aspecto (render)**: `src/components/KitchenWorld.tsx` y `src/lib/kitchen/{props,vapor}.ts`. Solo dibuja el estado que dan las reglas.
3. **Recursos**: `public/kitchen/{furn,food,tex}` (CC0: Kenney, Poly Haven). Créditos en `/creditos` y `LICENSE-*.txt`.
4. **Huecos de aspecto**: `src/lib/mundo/capas.ts`. Cada fachada, suelo o interior es un hueco con fuente `procedural`, `cc0` o `foto-propia`.
5. **Perfiles de calidad**: `src/lib/mundo/perfiles.ts` (bajo, medio, alto): resolución, sombras, reflejos y vapor según dispositivo.

## Ya hecho en la cocina 3D
Texturas PBR (azulejo, acero), modelos decorativos, reflejos de entorno, sombras suaves, vapor sobre fogones y plancha, comida que cambia de color con el fuego, perfiles de calidad.

## Pendiente (en este orden)
- Medir FPS reales por dispositivo y ajustar perfiles; capturas antes/después.
- Personajes con animación (cocinero, camarero, freganchín) y manos en primera persona. Base CC0: Quaternius.
- Interacciones físicas (abrir nevera, recoger y llevar objetos).
- NPC con estados y rutas.
- Audio espacial.
- **Corralejo con fotos propias (se deja para el final, quizá meses).**

## Cómo añadir Corralejo cuando haya fotos
1. Hacer fotos de frente, con luz pareja, sin personas ni matrículas identificables. Anotar dirección y fecha.
2. Convertirlas a texturas (diffuse; rough y normal opcionales) con Blender o similar, 1k–2k, JPG.
3. Copiarlas a `public/mundo/corralejo/` y editar el hueco correspondiente en `capas.ts`: `fuente: "foto-propia"`, `texturas`, `autor`, `licencia`, **`permisoCaptura: true`**.
4. Si falta algo de lo anterior, el hueco sigue usando el aspecto genérico (lo comprueba `huecoValido` y `tests/mundo-capas.test.mjs`).
5. Añadir el crédito en `/creditos`. No afirmar que una reproducción es exacta si no está contrastada.

## Cliente Unreal (opción futura)
Solo si se quiere realismo de videojuego comercial. Requisitos: ordenador potente, prueba de viabilidad, API de Island Crew para cuenta, carrera y misiones, y revisión de licencias (Unreal, MetaHuman, Fab). Las reglas puras de `src/lib` se reutilizarían como servicio.
