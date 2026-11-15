# Ecosistema de chat: evaluación de repositorios y decisión de arquitectura

Fecha: 2026-10-10. Los 19 repositorios se descargaron como copia superficial (última versión) en un espacio de trabajo aparte, **sin instalar ni ejecutar nada**. Los datos de licencia son los que se ven en el archivo de licencia o en `package.json`; donde dice «a verificar» no se ha podido confirmar leyendo solo la cabecera (varios proyectos mezclan una parte libre con carpetas «enterprise» de pago).

## Qué tipo de pieza es cada uno

| Proyecto | Tipo | Licencia observada | Tamaño | Último commit | Uso en Island Crew |
|---|---|---|---|---|---|
| Supabase | Plataforma (ya la usamos) | Apache-2.0 | 1,4 GB | 2026-10-09 | **Ya integrada**: Postgres, auth, Realtime. Es la base de toda la mensajería. |
| Vercel AI SDK | Librería | Apache-2.0 | 155 MB | 2026-10-09 | Candidata para el asistente con streaming si se amplía; hoy `src/lib/llm.ts` ya abstrae el modelo. |
| LiveKit | Servidor + SDK | Apache-2.0 | 8 MB | 2026-10-09 | Candidata para voz/videollamada. Requiere LiveKit Cloud o un servidor propio: coste y credenciales pendientes. |
| LangGraph | Librería (agentes) | MIT | 20 MB | 2026-10-10 | Referencia para flujos de agentes; el Agent OS actual ya tiene cola y aprobación humana. |
| assistant-ui | Componentes React | MIT | 161 MB | 2026-10-10 | **No** se incorpora: el proyecto prohíbe librerías de UI nuevas y el chat actual se resuelve con los componentes propios. |
| LibreChat | App completa de chat IA | MIT | 111 MB | 2026-10-06 | Solo referencia de funciones (historial, adjuntos). No se despliega: duplicaría cuentas y conversaciones. |
| AnythingLLM | App completa (RAG) | MIT | 108 MB | 2026-10-09 | Referencia para memoria/documentos de la IA. No se despliega. |
| Open WebUI | App completa de chat IA | Licencia propia («Open WebUI License») | 68 MB | 2026-09-21 | Licencia con condiciones propias: **no copiar código**; revisar antes de cualquier uso. |
| LobeChat | App completa | Apache (cabecera) / MIT (package.json) | 369 MB | 2026-10-10 | Solo referencia. |
| Dify | Plataforma de agentes | Apache (cabecera, con condiciones adicionales a verificar) | 201 MB | 2026-10-10 | Solo referencia. |
| Flowise | Constructor visual de flujos | a verificar (hay carpeta enterprise) | 74 MB | 2026-08-13 | No necesario. |
| n8n | Automatización | «Sustainable Use License» (no es código abierto libre) | 374 MB | 2026-10-09 | No se integra en el código; sería un servicio externo opcional, con revisión de licencia. |
| Mattermost | Chat de equipos (app completa) | `LICENSE.enterprise` presente: a verificar | 782 MB | 2026-10-09 | No encaja: otro servidor, otras cuentas. |
| Rocket.Chat | Chat de equipos (app completa) | MIT en el núcleo; carpetas enterprise: a verificar | 311 MB | 2026-10-09 | No encaja: duplicaría cuentas. |
| Zulip | Chat con hilos (app completa) | Apache | 201 MB | 2026-10-09 | Referencia de diseño de hilos y respuestas. |
| Element Web | Cliente Matrix | **AGPL-3.0** | 136 MB | 2026-10-09 | **No copiar código**: obligaría a publicar el código de Island Crew. |
| Synapse (matrix-org) | Servidor Matrix | Apache | 48 MB | **2023-12-13** | Repositorio desactualizado (el proyecto sigue en otra organización); no usar esta copia. |
| Chatwoot | Atención al cliente (app completa) | MIT en el núcleo; carpeta enterprise: a verificar | 303 MB | 2026-10-09 | Referencia de bandeja de soporte para negocios. |
| FreeScout | Soporte por email (app completa) | **AGPL-3.0** | 61 MB | 2026-10-10 | **No copiar código**. |

## Decisión

1. **Una sola mensajería, la que ya existe** (Supabase + tablas `net_*`, SQL 53/54/58/59). Instalar Mattermost, Rocket.Chat, Zulip, Element o Chatwoot a la vez crearía varios sistemas con cuentas, almacenamiento y notificaciones duplicados, justo lo que se quiere evitar.
2. **No se copia código de proyectos AGPL, con licencia propia o «enterprise»** (Element, FreeScout, Open WebUI, n8n, partes de Mattermost/Rocket.Chat/Chatwoot/Flowise). Se toma solo la idea de producto.
3. **Lo ya hecho (SQL 65):** responder a un mensaje, indicador de leído («✓✓ Leído»), borrar un mensaje propio y denunciar uno recibido, todo con control en servidor, límites anti-spam (20 mensajes/min, 10 denuncias/día) y pruebas.

## Estado real de las capacidades pedidas

| Capacidad | Estado |
|---|---|
| Mensajes privados entre conectados, bloqueo, notificaciones, límite anti-spam | IMPLEMENTADO (SQL 54), en producción |
| Responder, leído, borrar, denunciar | IMPLEMENTADO, **sin verificar en producción** hasta correr el SQL 65 |
| Revisión de denuncias por el equipo | IMPLEMENTADO (SQL 66, `/admin/denuncias`), incluye ver la foto denunciada; sin verificar en producción |
| Reacciones y fotos adjuntas en mensajes (6 emojis; JPG/PNG/WebP 5 MB; bucket privado `net-dm`) | IMPLEMENTADO (SQL 67), **sin verificar en producción** |
| Hilos, adjuntos que no sean imagen, mensajes de voz | PENDIENTE |
| Presencia en línea y «escribiendo…» | PENDIENTE (hay presencia del mundo por Supabase Broadcast; no está en el chat) |
| Salas y comunidades | PENDIENTE |
| Chat de negocio con clientes / atención al cliente | PENDIENTE |
| Asistente IA con acceso limitado al contexto autorizado | PARCIAL: `/api/assistant`, `/api/cabra`, Agent OS; falta el historial persistente por usuario |
| Voz y videollamada | BLOQUEADO por decisión de proveedor (LiveKit Cloud o servidor propio: coste y credenciales) |
| Retención y borrado de datos (RGPD) | PENDIENTE: definir plazos; el borrado de mensajes hoy es lógico (se oculta el texto) |
| Registro de auditoría de operaciones de administración | PARCIAL: existe en Agent OS; no cubre todavía moderación de chat |

## Seguridad aplicada en SQL 65

- Todas las funciones son `security definer` con `search_path` fijo, exigen sesión y comprueban bloqueo y conexión en servidor; no se confía en nada que mande el cliente.
- Solo el autor borra; solo el destinatario denuncia; la respuesta solo puede citar un mensaje de la misma conversación.
- La tabla de denuncias tiene RLS activado y sin acceso directo para `anon` ni `authenticated`.
- La IA no lee conversaciones privadas: ninguna función de agentes toca `net_messages`.

## Siguiente paso

Correr `TODO_CORRER_65_MENSAJES_RESPUESTA_LEIDO.sql` en Supabase, desplegar y probar con dos cuentas conectadas. Después: pantalla de moderación de denuncias y reacciones/adjuntos en mensajes.
