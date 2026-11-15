# Island Crew — Auditoría de arquitectura de producto

Fecha: 2026-10-06. Alcance: repositorio `island-crew-web` (Next.js 15 + Supabase). Solo lectura: no se ha cambiado arquitectura. Todo lo que aquí figura se ha comprobado en el código; lo que no se pudo comprobar está marcado como **desconocido**.

## 1. Arquitectura actual
- Next.js 15 App Router, React 18, TypeScript, Tailwind 3 instalado, Supabase (Postgres + Auth + RLS + RPC `SECURITY DEFINER`). Despliegue en Vercel desde `main`.
- ~226 archivos `.ts/.tsx`; 38 migraciones/SQL; 62 RPC distintas llamadas desde el cliente; 4 ficheros de tests (`node --test`, 29 tests, solo lógica pura).
- Dependencias pesadas: `three`, `@react-three/fiber`, `@react-three/drei` (cabra 3D, cargada con `dynamic` sin SSR), `jspdf`, `qrcode`, `resend`.
- No hay `middleware.ts`, ni `error.tsx`/`loading.tsx` por ruta, ni `next/image` (0 usos, 38 `<img>`), ni TanStack Query, ni Zod, ni librería de iconos.
- Variable de entorno: `NEXT_PUBLIC_SUPABASE_KEY`. `.env.local` está ignorado por git (correcto).

## 2. UX actual
- Web de marketing + app web (housing, Market, Crew, chat, nivel, objetivos). Navegación por `Nav` + `Wrap` común a las páginas de cuenta; menús desplegables (`NavSelect`) en Market e identidad.
- Descubrimiento público existente: `/trabajo-en/*`, `/personal-hosteleria/*`, `/housing/viviendas`, `/marketplace`, `/u/[id]` (este último exige sesión).
- No existe una Home personalizada tras login: la portada es de marketing.

## 3. Design system actual
- Estilo neo-brutalista propio: INK `#0A1A33`, YEL `#FFD400`, CREAM `#F4E3B8`, PAPER `#FDFBF4`.
- Kit compartido `@/components/housing/ui` (Wrap, h1, h2, card, btn, ghost, input, sel, Notice, Tag…), pero **1.318 `style={{}}` inline** y colores literales repetidos (`#0A1A33` ×92, `#FFD400` ×45, `#FDFBF4` ×24, más rojos de error sueltos). Tailwind está instalado y se usa en ~94 archivos: conviven dos sistemas.
- **No hay tokens** (ni CSS variables ni theme de Tailwind alineado con la paleta), ni dark mode, ni Figma conectado (desconocido), ni Storybook.

## 4. Gamificación actual (construida en las últimas sesiones)
- XP: `xp_events` (idempotente por `(sujeto, kind, ref)`), solo suma; `points_ledger` separado; `badge_catalog`/`badges_awarded`; `level_info` calcula nivel (7 niveles persona, 6 empresa) con **constantes dentro de SQL**.
- `levels_sync` (pull, al abrir `/nivel`) y `goals_sync` (al abrir `/objetivos`) otorgan XP desde hechos reales.
- `goals_catalog` editable (XP ≤ 500), `gamification_flags` (goals, next_action, benefits), `gamification_events` (4 eventos), `/admin/gamification`.
- Beneficios: tabla vacía y apagada a propósito.
- Lo pedido que **no existe**: motor de eventos de dominio, reglas de XP en tabla, tabla de niveles editable, flags para points/badges/goat/level-up, Home personalizada, Journeys, reputación estructurada, Goat con estados, animación de level-up, historial para explicar "por qué este nivel".

## 5. Modelo de datos actual
- Un solo `auth.users.id` como identidad; `profiles`, `housing_profiles`, `user_roles`, `trust_signals`, `business_accounts/members/audit`, `employment_records`.
- Dominio housing: `properties`, `housing_*` (grupos, mensajes, visitas, alertas, acuerdos…); Market: `market_items/orders/rentals/reviews/disputes/handovers/wanted`, `crew_market_*`.
- Observabilidad: `events` (analítica de producto), `housing_events`, `security_incidents`, `deletion_log`, `terms_acceptances`.

## 6. Journey de usuario actual
Descubrir → registro → onboarding (perfil / tipo de usuario) → CV / swipe / housing / Market. El "volver al punto exacto tras registrarse" existe en parte (`/login?next=`), sin comprobar en todas las acciones protegidas (**desconocido**, requiere prueba E2E).

## 7–10. Market, Housing, Empleo, Crew
- **Market:** compra/venta/alquiler/"Busco", reseñas, disputas, entregas, categorías. Sin pagos, sin protección/seguro.
- **Housing:** perfiles, viviendas, favoritos, intereses, visitas, alertas, grupos de 1–4. El pipeline de 10 estados pedido (Saved→Rented) **no está modelado como una sola máquina de estados**: existen piezas (`property_favorites`, `property_interests`, `housing_visits`, `housing_cases`) sin un estado único por oportunidad.
- **Empleo:** CV, swipe, matches, `employment_records` confirmado por ambas partes. No hay entrevistas/aplicaciones como journey unificado (**desconocido** si `swipe/matches` cubre candidatura).
- **Crew:** grupos de 1–4, invitaciones, encuestas, acuerdos, mensajes de grupo, Market compartido en Crew.

## 11. Chat actual
`housing_messages` y `housing_group_messages`; `ChatView` único. Tarjetas contextuales dentro del mensaje (propiedad/oferta/Market): **no verificado**.

## 12. Analítica actual
`lib/analytics.ts` inserta en `events` (solo captura; sin cálculos). No hay herramienta de terceros. Los eventos pedidos (`job_hired`, `employment_month_*`, `housing_success`…) existen sólo en parte.

## 13. Deuda técnica
Dos sistemas de estilos; 1.318 estilos inline; páginas muy grandes (`crearcurriculum`, `housing/grupo/[id]`, `cuenta` >25 KB); sin `error.tsx`/`loading.tsx`; sin cache de servidor en cliente (cada página repite `supabase.from(...)`); 10 usos de `confirm/prompt/alert` nativos; constantes de niveles dentro de SQL; 4 ficheros de test sin E2E.

## 14. Deuda UX
Sin Home post-login; estados vacíos y de carga heterogéneos; formularios de Market con `select` sin unificar; la cabra existe en tres implementaciones (`Goat.tsx` SVG, `GoatMascot3D`, `GoatViewer3D`) sin sistema de estados común.

## 15. Deuda de accesibilidad
Solo 69 atributos `aria-`; 18 menciones de `prefers-reduced-motion`; contraste del amarillo sobre crema sin medir; foco visible y teclado en dropdowns y modales **no auditados con herramienta** (axe/Lighthouse no se han ejecutado). Modales propios (`position: fixed`) en 7 componentes sin primitiva común.

## 16. Deuda de rendimiento
0 `next/image` (38 `<img>`, sin lazy ni dimensiones declaradas → riesgo CLS/LCP); `three` en el bundle de la ruta donde se use; sin `loading.tsx`; sin presupuesto de rendimiento definido; no se ha medido LCP/INP (**desconocido**).

## 17. Riesgos de seguridad
- RLS + RPC con decisiones en servidor: buen patrón, pero **no hay auditoría RLS completa** de las 38 migraciones (pendiente).
- Clave VAPID privada escrita como comentario en `.env.local` local (no versionado): **rotarla** y moverla a secret del servidor.
- `business_member_add` / `employment_create` permiten saber si un email existe (enumeración): decisión de producto + legal.
- Subida de ficheros (fotos Market/housing): validación de tipo/tamaño en servidor **no verificada**.
- Sin rate limiting general fuera de las RPC nuevas.

## 18. Duplicaciones
- Tres cabras (SVG, mascota 3D, visor 3D).
- Dos sistemas de estilo (inline neo-brutalista y Tailwind).
- Siete implementaciones de capa fija (modales/toasts/banners) sin primitiva.
- Notificaciones ya unificadas en `housing_notifications` (nombre histórico, mantener).
- XP/niveles: **una sola** implementación (SQL), sin duplicado en cliente. Bien.
- Cálculo de progreso: `levels_sync` (hechos de nivel) y `goals_sync` (objetivos) leen los mismos hechos con dos funciones distintas → riesgo de divergencia. Ver Recomendación.

## 19. Arquitectura recomendada
1. **Conservar** Next + Supabase + RPC servidor-autoridad + XP idempotente + notificaciones unificadas + `housing/ui`.
2. **Tokens como CSS variables** (`:root`) mapeadas en `tailwind.config.ts`; migrar `housing/ui` a tokens y dejar de añadir colores literales. Migración gradual por pantalla, no big-bang.
3. **Motor de eventos de dominio** en BD: tabla `domain_events` + `xp_rules` + `levels` editables + función única `gamification_apply(event)`; `levels_sync` y `goals_sync` pasan a leer las mismas reglas.
4. **Home personalizada** (`/inicio`) con una única "next best action" calculada en servidor.
5. Primitivas de UI únicas: Dialog, Toast, Skeleton (accesibles). Evaluar Radix Dialog antes que escribir otra.
6. Goat como sistema: un solo componente con estados; Rive/Lottie **solo si** se mide valor.
7. TanStack Query: justificado únicamente cuando la Home personalizada y el chat compartan caché; no antes.
8. Mide antes de optimizar: axe + Lighthouse + Playwright sobre 5 flujos críticos.

## 20. Roadmap recomendado
- **P0:** tokens + Dialog/Toast/Skeleton + `error.tsx`/`loading.tsx` + `next/image` en listados + Home con next-best-action + reglas de XP/niveles en tabla + audit RLS + rotar VAPID.
- **P1:** Journeys (empleo/housing/Crew/Market) con máquina de estados única; match score explicable; reputación estructurada; E2E Playwright; accesibilidad con axe.
- **P2:** Island Points + partners (con revisión legal), Goat avanzado, experimentos A/B, recomendaciones.
