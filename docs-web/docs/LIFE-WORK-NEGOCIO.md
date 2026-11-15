# Island Crew Life & Work · Modelo de negocio (borrador de trabajo)

> Todas las cifras de este documento son **supuestos o simulaciones**, no datos ni previsiones. Hoy no hay ingresos ni cobro activo. Esto es planificación de negocio, no asesoramiento legal, fiscal ni financiero: revisar con gestoría y abogado antes de cobrar.

## 1. Resumen ejecutivo
Cuatro motores de ingreso que no dependen de monetizar el sufrimiento: **B2C** (Plus/Pro/Worker Pass), **Profesionales** (comisión por sesión + suscripción opcional), **B2B** (Business Wellbeing, Recruit Pro, Job Boost) y **Marketplace** (sesiones, Academy, microproductos, eventos, partners). Regla: ayuda básica gratis para siempre; se cobra por herramientas extra, acceso a profesionales y servicios a empresas.

## 2. Qué existe hoy (hecho) y qué no
- **Hecho:** sección `/vida` (escucha, check-in, mapa, misiones, caminos, oportunidades, mapa de vida), catálogo de precios editable (SQL 49), páginas `/vida/planes` y `/empresa/bienestar` (informativas, sin compra), cuadro `/admin/negocio` con datos reales de pagos (hoy ceros) y economía unitaria.
- **No hecho (necesita decisiones externas):** proveedor de pagos y webhooks (Stripe u otro: cuenta, claves y alta fiscal), facturación electrónica/IVA (asesor fiscal), verificación y contratos con profesionales (requisitos legales de servicios regulados, p. ej. psicología), cursos/Academy, eventos, partners, panel de empresa con encuestas voluntarias.

## 3. Tensión de diseño que hay que resolver
Life & Work guarda todo **solo en el dispositivo** (máxima privacidad). Plus promete «historial» entre dispositivos y B2B promete analítica agregada. Ambas cosas requieren datos en servidor. Solución propuesta: (a) sincronización **opt-in y cifrada de extremo a extremo** para Plus; (b) la analítica de empresa sale de **encuestas voluntarias y anónimas separadas**, con mínimo k = 10 respuestas, nunca de conversaciones ni diarios. Los datos de bienestar son sensibles (RGPD): exigir evaluación de impacto y consentimiento explícito antes de construirlo.

## 4. Economía unitaria (supuestos editables en `economics.ts`)
Margen por venta = precio − comisión de pago − parte del profesional − infraestructura − soporte. Ejemplo de sesión de 40 €: 34 € profesional / 6 € Island Crew (15 %, configurable) antes de costes de pago y soporte, que se comen parte de esos 6 €. Por eso las sesiones solas no son el negocio: el MRR de suscripciones y B2B sostiene la base. Hay alerta de rentabilidad por producto.

## 5. Simulación hipotética (no previsión)
1.000 Plus × 7,99 € + 100 Pro × 19,99 € + 50 empresas × 99 € ≈ **14.939 € MRR** + variable. Es un escenario de modelado; la conversión real de gratis a pago suele ser una fracción pequeña y no la conocemos todavía.

## 6. Hitos (se avanza solo con datos reales)
Usuarios de pago: 100 → 500 → 1.000 → 5.000 → 10.000. Empresas: 10 → 50 → 100 → 500. Medir qué producto convierte antes de construir el siguiente.

## 7. Roadmap
- **30 días:** correr SQL 49; validar con 10–20 personas si pagarían por Plus y qué incluiría; entrevistas con 5 negocios sobre Business Wellbeing; elegir proveedor de pagos y consultar gestoría.
- **90 días:** cobro de una sola suscripción (Plus) + Job Boost para negocios; webhook que escribe `orders`/`subscriptions`; cancelación en un clic; primer panel B2B con encuestas voluntarias.
- **6–12 meses:** sesiones con 3–5 profesionales verificados; Academy con 2–3 cursos; Worker Pass con partners locales reales.
- **3 años:** más destinos con la misma plataforma (catálogo y precios por destino).

## 8. Riesgos principales y mitigación
- **Legal:** servicios regulados (psicología) → solo profesionales colegiados verificados, sin presentar la IA como terapia; datos sensibles → consentimiento y evaluación de impacto; facturación/IVA → asesor fiscal.
- **Confianza:** cualquier uso de datos de bienestar para vender, segmentar o presionar destruye el producto → separación técnica ya aplicada y vigilada con tests.
- **Mercado:** disposición a pagar de trabajadores de temporada con ingresos ajustados es incierta → B2B y marketplace compensan; nunca bloquear ayuda básica.
- **Ejecución:** demasiados frentes → un solo producto de pago primero.

## 9. KPIs
MRR, ARR, churn 30 d, ARPU, conversión, CAC, LTV, margen bruto, ingresos por producto y por destino (el cuadro ya devuelve «—» para lo que aún no se mide). Métrica de impacto: personas que identifican una opción y dan un primer paso.

## 10. Confianza y supuestos
Confianza en el diseño del producto: media-alta. Confianza en cualquier cifra económica: **baja** hasta tener ventas reales. Supuestos clave: se puede cobrar a trabajadores por herramientas extra; los negocios pagan por contratar y por bienestar; se consigue una pasarela de pagos y profesionales verificados.

## 11. Próximas acciones
1) Elegir pasarela y crear cuenta (decisión tuya). 2) Hablar con gestoría sobre IVA/facturación y con abogado sobre profesionales y datos de bienestar. 3) Pilotar Plus con una lista de espera real antes de construir el checkout.
