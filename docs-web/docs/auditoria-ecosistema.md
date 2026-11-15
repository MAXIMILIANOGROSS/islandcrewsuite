# Auditoría del ecosistema Island Crew (paso 1 de /BUILD_ISLAND_CREW_ECOSYSTEM)

Fecha: 2026-10-07. Solo inspección; lo no comprobado figura como **desconocido**.

## 1. Lo que YA existe (no se reconstruye)
- **Identidad única**: `auth.users.id` + `profiles`, `user_roles`, `trust_signals`, `business_accounts/members/audit`, `employment_records`. `src/lib/identity.ts` (roles, permisos de empresa, insignias solo si verificadas).
- **Empleo web**: swipe, matches, mensajes, empresas, vacantes, CV (`cv`, `crearcurriculum`), landings `/trabajo-en/*`.
- **Vivienda y Market**: housing_*, market_*, crew_market_*.
- **Gamificación real**: xp_events idempotente, points_ledger, badges, niveles, objetivos (docs/island-crew-product-architecture-audit.md).
- **Verificación**: funciones Supabase verify-company-website / verify-email-confirm / verify-location; `/verificar*`, `/cuenta/identidad`.
- **Mundo (esta fase)**: `/mundo/jugar`, `/mundo/real` (OSM), carrera simulada, entrevistas, 230 negocios ficticios.
- **Admin, notificaciones, push, email (resend)**.

## 2. Huecos frente al master prompt
| Área | Estado |
|---|---|
| SSO web+móvil+juego | Misma cuenta Supabase en web y juego. Apps móviles: **desconocido** (repos aparte). |
| Passport VERIFIED / SELF_DECLARED / GAME_EARNED / EMPLOYER_CONFIRMED | Existe `trust_signals` (solo verificado) y flags de juego, **sin un modelo unificado de estados**. |
| Real vs simulado | Ya separado en el juego (SIMULADA/PRÁCTICAS/OPORTUNIDAD_REAL). Falta el mismo campo en datos web. |
| Estados de empresa DISCOVERED…PARTNER | No existe; hoy solo empresa verificada sí/no. |
| Reputación dividida | Solo reputación de turnos en el juego. |
| API v1 / eventos de dominio | No hay capa API versionada; RPC directas desde el cliente (62). Sin bus de eventos. |
| Aprendizaje/cursos reales, CMS, analítica unificada, CI/CD | Parcial o inexistente (4 ficheros de test; sin CI conocido). |
| Moneda real vs de juego | Separadas por diseño (no hay dinero real en el juego). |

## 3. Duplicaciones / riesgos
- Dos motores de progreso: `ic_game_v1` (juego) y `xp_events` (web). Deben seguir separados; el puente es EMPLOYER_CONFIRMED/verificado, nunca el XP de juego.
- `/mundo/jugar` (calle procedural) y `/mundo/real` (OSM) conviven; unificar tras validar.
- Estilos inline masivos (ver auditoría de producto).
- Archivo suelto en la raíz con nombre de texto: borrar.

## 4. Plan incremental (núcleo primero)
1. **Passport**: una vista/RPC `ic_passport()` que agrupe cada hecho con su estado (VERIFIED, SELF_DECLARED, GAME_EARNED, EMPLOYER_CONFIRMED) y origen. Sin datos nuevos sensibles.
2. **Estados de empresa** en `business_accounts` (DISCOVERED→PARTNER) + etiqueta REAL/SIMULADA en ofertas.
3. **Eventos de dominio** (tabla `domain_events`) alimentando XP/reputación.
4. **API v1** (`/api/v1/*`) sobre RPC, para móvil.
5. Reputación dividida, aprendizaje, CMS, CI.
Cada paso con tests y revisión legal (RGPD, datos de CV, entrevistas reales).
