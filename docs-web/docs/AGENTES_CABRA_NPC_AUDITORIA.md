# Auditoría honesta: Agent OS, CABRA y NPC

Fecha: 2026-10. Estado según el código, no según el diseño.

## Agent OS (real)
- Ciclo `aos__cycle`: determinista, sin IA. Cuenta observaciones y crea tareas por reglas (auditor, ceo).
- Arranca en pausa. El programador (pg_cron) solo se activa con tu frase exacta.
- 32 roles registrados en base de datos; el catálogo de 400 roles existe (catalog.ts y SQL 61). docs/AGENTES.md lo describía desactualizado.
- Borradores con IA (Groq → Gemini → OpenRouter): solo texto, nunca es evidencia, nunca publica ni contacta.
- Nuevo (SQL 74): "Simular ciclo" muestra qué haría el ciclo sin escribir nada (0 escrituras, solo admin).

## CABRA (real, fase 1)
- Router determinista hacia propuestas y enlaces. No es un LLM autónomo.

## NPC (real)
- Memoria y estado viajan con el cliente y se sanitizan en servidor. No hay memoria por jugador guardada en base de datos.

## No probado en producción
- SQL 63–74 sin ejecutar en tu Supabase real. Tablas ausentes aparecen como "no disponibles" en el ensayo.
- Llamadas LiveKit, multijugador GPS/pasos y `next build` completo.

## Pendiente
- Memoria de NPC por jugador en base de datos; recomendación de empleos reales por NPC.
- Asistente de borradores para locales (respuestas en /empresa/mensajes), siempre revisado antes de enviar.
