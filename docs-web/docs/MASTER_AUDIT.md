# MASTER AUDIT — Island Crew (2026-10-10)

Línea base medida en esta sesión. Estados: NOT_STARTED, IN_PROGRESS, BLOCKED, IMPLEMENTED_UNVERIFIED, VERIFIED (VERIFIED = comprobación reproducible). Completa `docs/UNIVERSO_INVENTARIO.md` y `docs/NETWORK_ESTADO.md` (que siguen vigentes) en vez de duplicarlos.

## Línea base verificada

| Comprobación | Resultado | Cómo repetirla |
|---|---|---|
| Tests unitarios | 564 pasan, 0 fallan | `node --experimental-strip-types --test tests/*.test.mjs` |
| TypeScript | Sin errores en `src/` (queda un error en `.next/types/routes.d.ts`, generado y obsoleto) | `npx tsc --noEmit -p .` |
| ESLint | **No configurado** (`next lint` pide configurarlo) | `npx next lint` |
| Build de producción | **No verificado en esta sesión**; Vercel despliega en cada push (los despliegues recientes cargan en islandcrew.es) | `npx next build` |
| Tests E2E / accesibilidad | Playwright y axe instalados; **no ejecutados** en esta sesión | `npm run test:e2e` |

Stack confirmado: Next.js ^15.5.27, React ^18.3.1, Tailwind ^3.4.10, TypeScript 5, Supabase JS, Three.js 0.169, MapLibre, WebLLM, Resend, jsPDF. `@react-three/fiber` y `drei` están en `dependencies` (preexistentes; no se añadieron nuevas).

## Estructura real

- ~170 páginas en `src/app` (listado completo con `find src/app -name page.tsx`), 24 rutas API en `src/app/api`, 64 migraciones `TODO_CORRER_*.sql` (copiadas a `supabase/`), 112 archivos de test.
- Sin `middleware.ts`: la protección de rutas es en cliente (`IcGate`, `useSession`) y **la autorización real está en funciones SQL `security definer` con RLS cerrada**. Es coherente, pero toda página sensible depende de que su RPC compruebe permisos (revisado en los módulos tocados hoy).
- Sin `vercel.json` ni workflows de GitHub: **no hay ningún scheduler desplegado**.
- Variables de entorno usadas: Supabase (URL, anon key), `LLM_*`/`CHAT_MODEL`/`COUNCIL_MODEL`/`ANTHROPIC_API_KEY` (proveedor de IA), `RESEND_API_KEY`, `AISSTREAM_API_KEY`, `FIRMS_MAP_KEY`, `MAPILLARY_TOKEN`, `NEXT_PUBLIC_MAP_*`, `NEXT_PUBLIC_PVP_WS_URL`. No se encontraron claves en el código.
- Rama `app-nativa-preview` en GitHub: contiene muchas carpetas ocultas de herramientas de IA (`.adal`, `.agents`, `.augment`…) en la raíz; hay que revisarlo antes de cualquier uso. **No existe app móvil nativa en `main`.**
- Panel de administración existente: `/admin` con agentes, cabra, torre, denuncias, identidad, negocio, npcs, verificaciones, world, housing, marketplace, leads, claims, gamification, dashboard.

## Inventario de módulos

| Módulo | Estado | Evidencia | Pendiente |
|---|---|---|---|
| Cuenta única y sesión | VERIFIED por el fundador en producción | `useSession`, Supabase Auth | Sin tests automáticos de autorización E2E |
| Network (perfil, feed, reacciones, comentarios, contactos, bloqueo) | VERIFIED en producción (según `UNIVERSO_INVENTARIO.md`) | SQL 53/54/58/59, `NetworkApp.tsx` | Grupos, eventos, páginas públicas de empresa |
| Mensajes: responder, leído, borrar, denunciar, reacciones y fotos | IMPLEMENTED_UNVERIFIED | SQL 65 y 67, `tests/mensajes65.test.mjs` | Correr SQL 65, 66 y 67 y probar con 2 cuentas |
| Moderación de mensajes denunciados | IMPLEMENTED_UNVERIFIED | SQL 66, `/admin/denuncias`, `tests/moderacion66.test.mjs` | Correr SQL 66; probar como administrador |
| Empleo (ofertas verificadas, candidaturas) | IMPLEMENTED_UNVERIFIED | SQL 56 | Probar con cuentas reales de empresa y candidato |
| Mundo real Corralejo (/mundo/real) | IN_PROGRESS | Three.js; fachadas de ladrillo en todas las casas; kit Downtown 3D cerca del jugador; calles; audio procedural; verificado hoy por captura en `/mundo/vista` | Casas lejanas aún en tonos arena, no ladrillo rojo; kit 3D no revisado de cerca |
| Mundo: ubicación, pasos, jugadores en vivo | IMPLEMENTED_UNVERIFIED | `livegeo.ts`, `liveLayer.ts`, SQL 64 | Probar con dos dispositivos reales; correr SQL 64 |
| NPC propios | IMPLEMENTED_UNVERIFIED | SQL 63, `/npc-factory` | Sin posición fija en el mapa |
| LA CABRA / Agent OS / 400 agentes | IMPLEMENTED_UNVERIFIED, **ciclo automático BLOQUEADO a propósito** | SQL 60–62, `/api/cabra`, `/api/agentes-ejecutar`, `/admin/agentes` | Falta la frase de activación; sin worker desplegado |
| Ojo de Dios / FOMO | IN_PROGRESS | `/fomo`, `FomoClient.tsx` | Sin registro de señales con procedencia ni fuentes conectadas |
| Recorrido narrativo | IMPLEMENTED_UNVERIFIED | `/recorrido`, `ScrollStory.tsx`, `ScrollFlight3D.tsx` | Comprobar móvil, movimiento reducido y alternativa sin WebGL |
| Voz y videollamada | NOT_STARTED / decisión pendiente | Ver `docs/CHAT_ECOSISTEMA_REPOS.md` | Elegir LiveKit gratis, Jitsi o WebRTC 1 a 1 |
| Catálogo de 10.000 repositorios | NOT_STARTED | — | Tabla + importador con la API de GitHub |
| Marketing multicanal | NOT_STARTED | — | Sin credenciales de ninguna red |
| App móvil | NOT_STARTED en `main` | rama `app-nativa-preview` | Auditar la rama antes de nada |
| Pagos | BLOCKED | `UNIVERSO_INVENTARIO.md` | Falta empresa real |

## Cinco carencias de mayor prioridad

1. **Verificación reproducible**: no hay ESLint, ni build ni E2E ejecutados de forma rutinaria. Sin esto ninguna función puede pasar a VERIFIED.
2. **Nada corre solo**: no existe scheduler/worker desplegado (Agent OS, informe diario y Ojo de Dios dependen de uno).
3. **SQL 63–66 sin aplicar en producción** (confirmación pendiente): las funciones nuevas no existen hasta correrlos.
4. **Mundo real**: la calidad visual de lejos y la prueba multijugador real siguen sin verificar.
5. **Moderación y RGPD**: política de retención de mensajes y borrado definitivo sin definir (hoy el borrado es lógico).
