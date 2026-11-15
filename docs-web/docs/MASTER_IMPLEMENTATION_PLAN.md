# MASTER IMPLEMENTATION PLAN

Ordenado por dependencias y riesgo. Cada fase termina con tests y actualización de `IMPLEMENTATION_STATUS.md`.

| Fase | Contenido | Estado | Bloqueo |
|---|---|---|---|
| 1 Auditoría y línea base | `MASTER_AUDIT.md`; 559 tests y `tsc` limpios | HECHA (parcial: falta build y lint) | Configurar ESLint; ejecutar `next build` y E2E |
| 2 Fundamentos | Permisos en servidor comprobados en SQL 65/66; tokens visuales ya en `docs/design-system.md` | EN CURSO | Auditar RPC antiguas una a una |
| 3 Producto web | Mensajes (hecho: responder/leído/borrar/denunciar/moderar) → reacciones y adjuntos → salas y comunidades → chat de negocio | EN CURSO | Correr SQL 65 y 66 |
| 4 Inteligencia y agentes | Registro de señales (Ojo de Dios) → historial persistente de LA CABRA | NO EMPEZADA | Worker desplegado y frase de activación |
| 5 Integraciones | Voz/vídeo, automatizaciones | BLOQUEADA | Decisión: LiveKit gratis / Jitsi / WebRTC 1 a 1 |
| 6 Mundo interactivo | Calidad visual lejana, NPC fijos, prueba multijugador, puerto y Lobos | EN CURSO | Verificar con dispositivos reales |
| 7 Operaciones | Scheduler, monitorización, catálogo de repos, marketing | NO EMPEZADA | Infraestructura y credenciales |

## Siguiente bloque exacto

Reacciones en mensajes (tabla `net_message_reactions` + 2 funciones + botones), sobre el mismo patrón de SQL 65/66. Después, adjuntos con Supabase Storage (bucket privado, URL firmadas).
