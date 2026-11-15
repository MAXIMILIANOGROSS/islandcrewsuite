# Island Crew Work, Life & Opportunity — auditoría breve y experimento mínimo

Fecha: 2026-10-09. Estado: propuesta del fundador pendiente de validar con usuarios reales. Todo lo marcado (H) es una hipótesis, no un dato.

## 1. Qué existe hoy (comprobado en el repositorio)
- Perfil/CV con PDF y varios idiomas (`/crearcurriculum`, `cvPdf.ts`), entrevista simulada (`interview.ts`), asistente (`/api/assistant`), swipe de empleo y matches, mensajes.
- Island Crew World en `/mundo/real` con misiones, puntos y ranking (SQL 38, 51, 52).
- Island Crew Network en `/network` (SQL 53, 54): perfil, feed, contactos, mensajes, avisos.
- `pricing_plans` y `subscriptions` en base de datos con **precios de ejemplo** (Plus 7,99 € marcado como ejemplo). No hay cobro real activado ni proveedor de pagos en el código.
- `/precios` es solo para empresas y dice que aún no hay planes fijos. Eso es correcto y se mantiene.

## 2. Las tres funciones de mayor impacto (H)
1. Preparar CV y candidatura para un puesto concreto (ya existe CV; falta adaptarlo a una oferta).
2. Práctica de entrevistas con feedback (existe la base en `interview.ts`).
3. Ofertas verificadas con origen, fecha de revisión y denuncia (existe `job_vacancies`; falta el estándar de verificación).

## 3. Experimento comercial más pequeño (hecho)
Pregunta: ¿pagarían los trabajadores 9,99 €/mes por Crew Plus?
- Página `/crew-plus` con encuesta honesta: "Todavía no cobramos nada". Una respuesta por usuario autenticado.
- Guarda: ¿lo pagarías? (sí/depende/no), función más útil, importe máximo opcional, si quiere aviso. No guarda correo ni datos personales.
- SQL 55. Resumen para ti (solo SQL Editor): `select plus_interest_summary();` con la clave de servicio, o las consultas comentadas en el archivo.
- Criterio de decisión (H, ajústalo): con al menos 100 respuestas de trabajadores reales, si menos del 10 % dice "sí" y menos del 25 % "sí o depende", NO construir Plus tal como está; cambiar la oferta o el precio. Si supera esos umbrales, siguiente paso: preventa real con cobro (requiere proveedor de pagos, aviso legal y IVA, que no están hechos).
- Cómo conseguir respuestas sin inventar tracción: compartir el enlace con trabajadores de hostelería de Corralejo en persona y por grupos, con consentimiento.

## 4. Lo que NO se ha hecho (y por qué)
- Plan financiero a 12 meses: sin datos de conversión reales cualquier cifra sería inventada. Se hace después de las primeras 100 respuestas, con tres escenarios.
- Precios de Business/Hiring/Academy (49–99/149/199 €): son hipótesis del prompt; faltan entrevistas con empresas.
- Cobros, suscripciones, IA de pago, Benefits, Academy: no existen todavía.
- Revisión jurídica: obligatoria antes de cualquier IA que clasifique candidatos y antes de cobrar (consumidores, IVA, desistimiento).

## 5. Próximos 15 días (validación)
1. Compartir `/crew-plus` con 30–50 trabajadores y recoger 100 respuestas.
2. 10 entrevistas de 15 min a trabajadores y 5 a dueños de negocio de Corralejo (qué pagarían, qué usan hoy).
3. Decidir con los umbrales de arriba. Registrar la decisión en `docs/DECISIONES.md`.
