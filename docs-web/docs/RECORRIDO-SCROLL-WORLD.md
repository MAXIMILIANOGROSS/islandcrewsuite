# Recorrido por scroll (scroll-world)
Fuente: https://github.com/oso95/scroll-world (licencia MIT, copiada en `public/scroll-world/LICENSE.txt`). Es una *skill* de agente + un motor JS de scroll-scrub.

## Qué se ha integrado
- Motor: `public/scroll-world/scrub-engine.js` (sin dependencias, sin cambios).
- Página: `/recorrido`, que lee `public/recorrido/manifest.json`. Con `ready:false` (estado actual) muestra las escenas en texto; con `ready:true` y un `clip` por sección monta el vuelo de cámara.
- Skill completa en `.claude/skills/scroll-world/` para ejecutarla en Claude Code.

## Qué NO está hecho (y por qué)
Los clips y las imágenes de escena se **generan con IA de pago** (Higgsfield + Monid; unos 27 USD por una cadena de 6 escenas, según su README) y requieren tus cuentas y créditos. Yo no puedo contratar ni gastar créditos, así que no hay vídeo todavía.

## Cómo generarlo (en tu ordenador, con Claude Code)
1. Instala Monid y Higgsfield CLI e inicia sesión (`higgsfield auth login`), y `ffmpeg`.
2. En el repo: pide "usa la skill scroll-world para Island Crew" con estas 5 escenas: Llegada (playa de Corralejo), Explora (calles y locales), Oficina Island Crew (Downtown), Empleo (CV), Life & Work (calma/hábitos). Estilo: diorama isométrico cálido, paleta del sitio (turquesa, amarillo #FFD400, azul noche #0a1a33).
3. Copia los clips a `public/recorrido/`, rellena `clip`/`still` en el manifest y pon `"ready": true`.
Presupuesto: confírmalo antes; yo no ejecuto gastos.
