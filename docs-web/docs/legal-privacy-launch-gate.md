# Island Crew — Legal & Privacy Launch Gate y decisiones de stack

Estado del documento: borrador técnico. **No es asesoramiento jurídico**; cada punto marcado "revisión legal" lo decide un profesional del mercado donde se opere.

## A. Regla
Island Crew no se abre a usuarios reales hasta completar revisión legal y de privacidad. Técnicamente terminado ≠ legalmente listo. Mientras tanto se puede construir y probar con datos ficticios, usuarios de prueba y staging.

Estados oficiales: `TECHNICALLY_READY → PRIVACY_REVIEW_PENDING → LEGAL_REVIEW_PENDING → SECURITY_REVIEW_PENDING → APPROVED_FOR_STAGING → APPROVED_FOR_BETA → APPROVED_FOR_PUBLIC_LAUNCH`.

## B. Estado real hoy (comprobado en el repo)
| Área | Existe | Falta |
|---|---|---|
| Aceptación de términos | `terms_acceptances`, `legalVersions.ts` | Consentimientos separados por finalidad |
| Derechos RGPD | `privacy_requests`, `PrivacyRequestForm`, `deletion_log`, `/eliminar-cuenta` | Proceso operativo documentado (plazos, responsable) |
| Cookies | `CookieConsent`, `ThirdPartyScripts` | Inventario de proveedores y base legal por evento de analítica |
| Visibilidad de datos | RLS por tabla; `/u/[id]` solo con sesión; `identity_card` sin email/teléfono | Clasificación formal PUBLIC/REGISTERED/EMPLOYERS_ONLY/PRIVATE/RESTRICTED y Privacy Center |
| Empleo | `employment_records` con confirmación de ambas partes | Revisión de rol (conexión vs intermediación) y de qué ve cada empleador |
| Puntos / XP | XP solo suma; puntos separados; beneficios **apagados** | Revisión de programa de puntos antes de activar canjes |
| Matching | `compatibility.ts`, swipe/matches | Documento de profiling (datos, finalidad, explicación, impugnación) |
| Retención | — | `data-retention-policy.md` |
| Flags legales | `gamification_flags` (goals, next_action, benefits) | `launch_gate` con una fila por área y `legal_status` |

**Aviso:** el sitio ya está publicado en `islandcrew.es` y el registro está abierto. Si hay personas reales registrándose, el gate ya está incumplido en la práctica. Recomendación: confirmar quién se ha registrado y, hasta la revisión, mantener apagado lo más sensible (transacciones reales de Market, puntos canjeables, matching a empleadores, registros de empleo con datos reales).

## C. Áreas que quedan bloqueadas hasta revisión
1. **RGPD:** bases jurídicas por tratamiento, minimización, finalidad, conservación, derechos, encargados, transferencias internacionales (Supabase, Vercel, Resend: DPA y región pendientes de comprobar).
2. **Consentimientos separados:** términos; privacidad; publicar perfil; visibilidad ante empleadores; comunicaciones comerciales; uso para matching; personalización; cookies/analítica; programa de puntos. Nada de "acepto todo".
3. **Datos laborales:** CV, experiencia, salario, disponibilidad, historial, referencias, documentos de identidad. Nunca se publica un dato solo porque exista.
4. **Gamificación:** XP, niveles, reputación, rankings, puntos, caducidad, recompensas, partners, referidos, valor económico, mecánicas promocionales.
5. **Matching/profiling:** art. 22 RGPD y Reglamento de IA (posible alto riesgo en selección de personal; fechas de aplicación por verificar con el abogado). Sin rasgos protegidos.
6. **Marketplace:** compraventa, alquiler, pagos, depósitos, reembolsos, disputas, reseñas, fraude, responsabilidad de plataforma, impuestos, consumidores, bienes prohibidos, moderación.
7. **Seguro:** Island Crew no es aseguradora; solo vía corredor/MGA autorizado. Legal aprueba distribución, textos, exclusiones, siniestros, precio y comisión.
8. **Empleo:** plataforma de conexión vs agencia/intermediario; qué se puede cobrar y comunicar; "solo conectamos" no elimina obligaciones por sí solo.
9. **Vivienda:** publicación, contacto, intermediación, propietarios/agencias, anuncios externos, comisiones, leads, visitas, acuerdos.
10. **Analítica, cookies y terceros:** tabla `evento / dato / finalidad / retención / proveedor / base`, e inventario `proveedor / finalidad / datos / país / DPA / retención / subencargados`.
11. **Documentos legales:** términos, privacidad, cookies, avisos de consentimiento, reglas de Market y comunidad, términos de empleador, propietario/agencia, partner y recompensas. Los borradores técnicos no sustituyen revisión profesional.

## D. Arquitectura que pide el gate (todo ⏳, nada construido aún)
- `consent_records(id, user_id, consent_type, version, accepted, timestamp, source, policy_version, metadata)`: específico, versionado, auditable, revocable.
- Separación `profile_data / public_profile_data / employer_visible_data / private_data`; niveles de empleador: público, empleador registrado, empleador autorizado (relacionado con candidatura), privado.
- `/settings/privacy` (Privacy Center): visibilidad, comunicaciones, personalización, datos guardados, solicitudes de derechos, eliminación.
- `launch_gate(area, legal_status, approved_by, approved_at, notes)` + flags: `production_legal_gate`, `gamification_public`, `employment_public`, `marketplace_transactions`, `points_rewards`, `employer_matching`, `housing_leads`, `insurance_protection`. Por defecto **apagados**; se encienden por área cuando `legal_status = APPROVED`.
- Documentos: `data-retention-policy.md` (retención por categoría), proceso DSAR operativo y proceso de incidentes de seguridad/privacidad.

## E. Checklist de lanzamiento (no declarar READY hasta marcar todo)
Producto · Seguridad · Privacidad · RGPD · Consentimientos · Empleo · Vivienda · Marketplace · Gamificación · Pagos · Seguro (si se activa) · Analítica · Documentos · Retención/eliminación · DSAR · Incidentes.

## F. Stack de referencia: decisión crítica
Principio: la sensación premium sale de sistema de diseño + movimiento con propósito + feedback + ilustración + tipografía + estados + rendimiento, no del número de librerías. Cada dependencia se justifica (licencia, mantenimiento, tamaño, seguridad).

| Herramienta | Decisión | Motivo |
|---|---|---|
| Figma + Dev Mode/MCP | Sí, para tokens y pantallas clave | Fuente única de diseño; requiere que tú me conectes el archivo. Hoy no hay Figma enlazado. |
| shadcn/ui | Solo como referencia/primitivas puntuales (Dialog, Popover) | Hay 7 modales caseros; Radix resuelve accesibilidad. No como identidad visual: el estilo propio se conserva. |
| Motion | Sí, acotado | Level-up, progreso y transiciones. Con `prefers-reduced-motion`. |
| TanStack Query | Después | Útil cuando Home y chat compartan caché; añadirlo antes es complejidad sin dolor medido. |
| Phosphor Icons | Sí, en la fase de design system | Hoy se usan emojis en menús y badges, sin librería de iconos. Cambiar es decisión de marca (los emojis son parte del tono actual). |
| Rive | Reservado para el Goat, cuando exista el sistema de estados | Hoy hay 3 cabras; primero unificar. |
| Lottie | Solo celebraciones puntuales | Evitar duplicar con Rive. |
| Blender | Solo si se decide un Goat 3D | Ya existe `three`/R3F; antes medir si aporta valor y coste de bundle. |
| Playwright + axe + Lighthouse | Sí, primero | Cero E2E y cero auditoría de accesibilidad hoy; es lo que más riesgo reduce. |
| Storybook | Opcional | Solo cuando haya tokens y primitivas estables. |

Orden propuesto de adopción: Playwright + axe/Lighthouse → tokens → primitivas (Dialog/Toast/Skeleton) → Motion → Phosphor → Figma ↔ código → Rive/Lottie → TanStack Query → Storybook.

## G. Principio
Técnicamente ambicioso, pero privacy-first, trust-first, legalmente consciente, transparente y centrado en el usuario. La velocidad de lanzamiento nunca va por encima de seguridad, privacidad y confianza.
