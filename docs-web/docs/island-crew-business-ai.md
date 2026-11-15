# Business AI — diseño y límites

Estado: **diseño; NO implementar sin revisión legal (RGPD, Reglamento de IA, empleo).** Revisión profesional obligatoria antes de usuarios reales.

## 1. Recomendación por fases
- **Fase A (MVP):** *Business Knowledge* estructurado + FAQ con **respuestas sacadas solo de esos datos** + cuestionario de pre-selección con **preguntas fijas** definidas por el negocio. Sin conversación libre generativa sobre contratación.
- **Fase B (tras validar y revisar):** asistente conversacional que **solo recupera y reformula** datos configurados («No tengo esa información. Puedes preguntarle al negocio.»).
- **Fase C:** resumen estructurado para el empleador de las respuestas del candidato, **sin puntuación de persona**.

## 2. Base de conocimiento (`business_knowledge`)
Campos: descripción, horarios, ubicación, idiomas, cultura, beneficios *declarados*, vacantes y requisitos, preguntas de entrevista, políticas, FAQ, estado de cada dato (`confirmed` / `unknown`), fecha de última revisión y quién lo aprobó. **Si un campo no existe, la IA no responde sobre él.**

## 3. La IA NO puede
Inventar salarios, condiciones, contratos, horarios, requisitos, beneficios, puestos ni decisiones de contratación; presentar un resultado como decisión definitiva; ocultar criterios; inferir o usar rasgos protegidos o sensibles (raza, religión, orientación sexual, salud, discapacidad, ideología, diagnósticos psicológicos, biometría); analizar emociones, voz, rostro o tono para valorar candidatos.

## 4. Resultado de pre-selección
Etiquetas descriptivas, no veredictos: «Respuestas completas», «Faltan datos», «Coincide con requisitos declarados», con el **porqué** (qué requisito y qué respuesta). El empleador revisa y decide; el candidato puede ver, corregir y pedir revisión humana.

## 5. Control del negocio
Reclamar y verificar su perfil; editar conocimiento; activar/desactivar IA y «contratando»; retirar contenido; ver y exportar conversaciones; recibir informe de «preguntas sin respuesta» para completar datos.

## 6. Seguridad y supervisión
Registro de conversaciones y de respuestas, informe de alucinaciones, escalado a humano, límites de uso y coste, detección de abuso, moderación. Pruebas de seguridad de IA (inyección de instrucciones, fuga de datos de otros usuarios, respuestas inventadas) **antes** de cualquier piloto.

## 7. Legal a revisar
Rol de Island Crew (conexión vs intermediación), art. 22 RGPD, transparencia hacia el candidato, base jurídica y retención de respuestas, Reglamento de IA (alto riesgo en selección de personal; prohibición de reconocimiento de emociones en el trabajo; fechas de aplicación **a confirmar**), derechos de acceso/rectificación/oposición, proveedores de IA y transferencias internacionales.

## 8. Demos
Con **negocios ficticios etiquetados**. Nunca representar a un negocio real sin su autorización.
