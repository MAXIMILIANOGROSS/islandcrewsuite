# Island Crew — Plan de negocio y modelo financiero (hipótesis)

> Todas las cifras son **hipótesis de trabajo**, no datos verificados. Ningún ingreso está garantizado. Sustituir por datos reales tras cada validación.

## Estrategia: validar primero en Corralejo
Fase 1 (0–6 meses): una sola zona, 3 líneas. Ampliar a otros municipios solo si se cumplen los umbrales de abajo. Pospuesto: pagos de experiencias, reservas, marketplace de terceros, expansión a otras islas.

## Líneas de ingreso (formato: oportunidad · problema · solución · ingreso · coste/dependencias · riesgo · métrica · siguiente paso)
**A. Locales (Directorio verificado + CVs)** — Problema: los locales de temporada reciben candidatos por canales dispersos. Solución: ficha reclamada, recepción de CVs con consentimiento, panel básico. Ingreso: plan de pago (hipótesis 29 €/mes). Dependencias: verificación manual, soporte. Riesgo: baja disposición a pagar. Métrica: % de locales reclamados que pagan tras 60 días. Siguiente paso: contactar 20 locales del mapa y ofrecer 3 meses gratis a cambio de feedback. 
**B. Life & Work Plus (suscripción)** — Problema: recién llegados sin red. Solución: planes, hábitos, comunidad, Hablar. Ingreso: 7,99 €/mes (precio de ejemplo ya en `plans.ts`, no validado). Riesgo: retención baja. Métrica: retención a 90 días. Siguiente paso: lista de espera real con 50 personas antes de cobrar.
**C. Empleo (publicación destacada)** — Ingreso por oferta destacada. Riesgo: pocas ofertas. Métrica: ofertas/mes. Siguiente paso: medir ofertas reales ya recibidas.
**D. Experiencias / reservas / pagos** — POSPUESTO: requiere Stripe Connect, T&C, seguros e IVA; no se simula nada.
**E. Patrocinio / publicidad local** — Solo con etiqueta "patrocinado" y sin datos personales ni de bienestar. Pospuesto hasta tener tráfico medido.
**F. Contenidos (guías, citas verificadas)** — Apoya SEO, no es ingreso directo.

## Escenarios a 36 meses (precios hipótesis: local 29 €/mes, Plus 7,99 €/mes; sin churn modelado)

| Escenario | Mes | Locales de pago | Suscriptores Plus | MRR (€) | ARR (€) |
|---|---|---|---|---|---|
| Conservador | 12 | 2 | 10 | 138 | 1,655 |
| Conservador | 24 | 14 | 65 | 911 | 10,930 |
| Conservador | 36 | 25 | 120 | 1,684 | 20,206 |
| Base | 12 | 8 | 40 | 552 | 6,619 |
| Base | 24 | 39 | 270 | 3,288 | 39,460 |
| Base | 36 | 70 | 500 | 6,025 | 72,300 |
| Ambicioso | 12 | 20 | 120 | 1,539 | 18,466 |
| Ambicioso | 24 | 100 | 810 | 9,372 | 112,463 |
| Ambicioso | 36 | 180 | 1500 | 17,205 | 206,460 |

Lectura honesta: aun en el escenario ambicioso, Corralejo solo da ~200 k€ de ARR; un negocio de varios millones exige repetir el modelo en más zonas/islas **después** de demostrar retención y disposición a pagar. No se debe asumir.

## Métricas que deciden seguir o parar
Locales reclamados ≥ 15 en 90 días · ≥ 20 % de ellos pagan · retención Plus a 90 días ≥ 40 % · CAC < 3 meses de ingreso (CAC y LTV: **sin datos aún**, medir).

## Privacidad
Los datos de bienestar (Life & Work: diario, hábitos, conversaciones) **nunca** se comparten con empleadores, locales ni anunciantes; las analíticas comerciales usan eventos agregados sin ese contenido.

## Riesgos principales
Disposición a pagar (mercado), dependencia de datos OSM (calidad, licencia ODbL: atribución obligatoria), RGPD/ LSSI (revisión legal pendiente), coste de IA, concentración en temporada.


---
## Actualización: modelo financiero ejecutable (`src/lib/finance/model.ts`, `node --experimental-strip-types scripts/finance-report.mjs`)
HIPÓTESIS, no previsiones. Planes: Free · Pro 49 €/mes · Growth 119 €/mes (mezcla 80/20), Plus 7,99 €/mes, pagos 3 %, IA 3 €/empresa/mes, soporte 4–6 €/empresa/mes.

| Escenario | Empresas de pago m12/m24/m36 | ARR m36 | Equilibrio mensual | Capital máx. | Margen bruto m36 |
|---|---|---|---|---|---|
| Conservador | 25 / 90 / 180 | ≈ 165 k€ | mes 11 | ≈ 17 k€ | 85 % |
| Base | 70 / 300 / 700 | ≈ 644 k€ | mes 15 | ≈ 20 k€ | 87 % |
| Ambicioso | 150 / 700 / 1.500 | ≈ 1,5 M€ | mes 11 | ≈ 50 k€ | 89 % |

**Advertencias que el modelo NO oculta:** (1) el fundador no cobra sueldo el primer año en ningún escenario y el coste de personal es bajo: con sueldo real el capital necesario sube y el equilibrio se retrasa; (2) no incluye impuestos sobre beneficios, IVA, autónomos/cuotas ni coste legal inicial; (3) 700–1.500 empresas de pago exceden el tejido comercial de Corralejo: requieren Fuerteventura y Canarias (fase 2–3), por eso el ambicioso depende de expansión no demostrada; (4) la baja mensual (2,5–4 %), el CAC (130–180 €) y la mezcla de planes son suposiciones sin datos; (5) facturación ≠ beneficio ≠ valoración. Ejemplos ilustrativos del prompt (100×49, 500×79, 1.500×99) no se suman ni son previsiones.

**Hipótesis a validar antes de invertir:** disposición a pagar ≥ 29 €/mes (entrevistas a 30–50 negocios), contactos atribuibles por negocio/mes, conversión prueba→pago, churn real a 90 días, coste real de soporte e IA.

## Respuesta en formato de dirección (los 9 puntos)
1. **Oportunidad:** ser el canal medible que lleva clientes y candidatos a negocios locales de Corralejo. 2. **Problema:** los negocios no saben qué canal les trae clientes ni dónde encontrar personal de temporada. 3. **Solución prioritaria:** ficha reclamada + contactos atribuibles + CVs con consentimiento + panel con estadísticas (el asistente y /lugar/[id] ya traen tráfico y datos). 4. **Ingreso:** Pro/Growth por suscripción tras piloto gratuito. 5. **Coste/dependencias:** verificación manual, soporte, datos OSM (ODbL), IA (~3 €/empresa). 6. **Riesgo principal:** que los negocios no paguen sin resultados atribuibles. 7. **Métrica:** nº de contactos atribuibles por negocio piloto en 60 días y % que paga. 8. **Siguiente paso:** pilotos con 10–20 locales del mapa; medir contactos reales (necesita tabla de eventos en Supabase). 9. **Aplazar:** reservas/pagos de experiencias, comisiones, expansión a otras islas, Intelligence.
