# IMPLEMENTATION STATUS (2026-10-10)

Fuente de verdad del estado por módulo: ver tabla de `docs/MASTER_AUDIT.md`. Resumen de lo cambiado en esta sesión:

| Cambio | Archivos | Tests | Estado |
|---|---|---|---|
| Fachadas de ladrillo y ventanas en todas las casas de Corralejo; esconder cajas viejas bajo el kit; mayor radio del kit | `src/components/RealTownWorld.tsx`, `src/lib/downtown/style.ts` | `tests/downtown.test.mjs` | Verificado visualmente en `/mundo/vista` (captura); casas lejanas en arena |
| Ventanas del kit sin cuadrados blancos | `public/world/downtown/Kit.glb`, `Kit_White.glb` | — | IMPLEMENTED_UNVERIFIED (sin captura posterior) |
| Vista pública `/mundo/vista` | `src/app/mundo/vista/page.tsx` | — | VERIFIED (carga en producción) |
| Mensajes: responder, leído, borrar, denunciar | `TODO_CORRER_65_*.sql`, `NetworkApp.tsx` | `tests/mensajes65.test.mjs` | IMPLEMENTED_UNVERIFIED |
| Moderación de mensajes denunciados | `TODO_CORRER_66_*.sql`, `src/app/admin/denuncias/page.tsx` | `tests/moderacion66.test.mjs` | IMPLEMENTED_UNVERIFIED |
| Reacciones y fotos adjuntas en mensajes; corrección de ambigüedad `read_at` de SQL 65 | `TODO_CORRER_67_*.sql`, `NetworkApp.tsx`, `src/lib/netReactions.ts`, `admin/denuncias/page.tsx` | `tests/mensajes67.test.mjs` | IMPLEMENTED_UNVERIFIED |
| Evaluación de 19 repos de chat | `docs/CHAT_ECOSISTEMA_REPOS.md` | — | Hecho |

Pruebas: 564 pasan, 0 fallan. Servicios realmente conectados: Supabase, Vercel (autodeploy), Resend (clave usada en rutas). Procesos activos: ninguno programado.
