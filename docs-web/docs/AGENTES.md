# Centro de operaciones de Island Crew (30 agentes en el registro inicial; 32 roles en Agent OS)
Estado honesto: **hoy no hay agentes ejecutándose.** Esto es el registro y las reglas (`src/lib/agents/registry.ts`, con tests). Un agente "trabaja" solo cuando una plataforma lo ejecuta y deja registro verificable.

## Qué existe
- 30 agentes con misión, indicador, modo de autonomía por defecto (verde/ámbar/rojo) y fase de activación.
- Prioridad = (Impacto×Confianza)/(Esfuerzo×(1+Riesgo)).
- Reglas duras: no se completa sin evidencia; ámbar/rojo exigen aprobación del fundador; detección de tareas duplicadas.

## Fase 1 (arranque, 5 agentes): CEO, Mercado, Analítica, Automatización, Auditor
Entregable: informe diario con datos reales (si falta el dato: "no disponible"). Necesita: una plataforma de ejecución programada y dónde guardar tareas (tabla en Supabase o hoja).

## Pendiente de decisión del fundador
Plataforma (tareas programadas de Claude, n8n, Make o propia), presupuesto mensual y nivel de autonomía. Sin eso no se activa nada.

## Agent OS (SQL 60 + /admin/agentes) — actualizado 2026-10-10
- **Implementado, pendiente de pruebas con tu cuenta:** registro persistente de los 32 roles (AGENT-001…032, admite hasta 400), tareas con los 9 estados, reglas duras en la base de datos (nada pasa a DONE sin evidencia; ámbar/rojo no pasan a RUNNING/DONE sin aprobación humana; BLOCKED exige motivo; máximo 3 intentos), ciclo idempotente por hora (Europe/Madrid), presupuesto diario, parada de emergencia, auditoría y panel.
- **El ciclo actual no usa IA:** cuenta denuncias, candidaturas sin responder, negocios sin verificar, etc., crea tareas internas (modo verde) y escribe un informe. Cuando un dato no existe pone «no disponible».
- **No hay ejecución automática.** Arranca en pausa. La programación horaria (pg_cron) está en el SQL como comentario y solo se activa con la frase exacta del fundador: «Sí, activa el informe diario con CEO Digital, Analítica y Auditor, solo con recomendaciones y sin acciones externas.»
- **Catálogo de 400 roles:** existe (`src/lib/agents/catalog.ts` y SQL 61). Los 32 registrados son los activables; el resto es catálogo de referencia.
- **Ensayo del ciclo (SQL 74):** el botón «Simular ciclo (sin guardar nada)» de /admin/agentes muestra qué haría el ciclo sin escribir nada (solo admin).
- **Borradores con IA:** cadena gratuita Groq → Gemini → OpenRouter (hace falta una clave en Vercel). Son texto: nunca cuentan como evidencia y nunca publican ni contactan.
- **CABRA (fase 1):** enrutador determinista a propuestas y enlaces; solo para el administrador. No es un modelo autónomo.
- **Cabras por sección (Curro, Tertulio, Gofio, Baifo, Tenderete, Sosiego):** chat público con IA y datos reales; memoria solo de etiquetas de interés (SQL 75), nunca del texto.
- **Pendiente:** ejecución de roles con IA y herramientas (decisión de proveedor, presupuesto y autonomía), memoria versionada del proyecto, almacén de evidencias, alertas, pruebas de carga y de recuperación en Supabase real.
