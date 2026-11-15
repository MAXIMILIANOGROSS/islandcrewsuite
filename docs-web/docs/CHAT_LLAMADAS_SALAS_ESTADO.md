# Chat, llamadas, salas y negocio — estado (SQL 65–72)

Fecha: 2026-10-10. Sistema único de mensajería: tablas `net_*` de Supabase. No se desplegó ninguna app de chat externa.

| SQL | Qué añade | Verificado |
|---|---|---|
| 65 | Responder, ✓✓ Leído, borrar y denunciar mensajes directos | Tests + ejecución real en PostgreSQL 16 (con stubs de auth/storage) |
| 66 | Moderación de denuncias de mensajes (solo admin) | Ídem |
| 67 | Reacciones y fotos adjuntas (bucket privado `net-dm`) | Ídem. Corregido: el borrado de la foto lo hace la app con la API de Storage (Supabase no permite DELETE por SQL en storage) |
| 68 | Salas públicas de texto | Ídem |
| 69 | Permiso de llamadas de voz/vídeo (LiveKit): `net_call_access` | Ídem; endpoint y botón con tests. **Llamada real sin probar** |
| 70 | Chat de negocio con clientes (locales partner) | Ídem (staff simulado con stub de `business_has`) |
| 71 | Listado de fotos huérfanas + política de borrado solo admin (`/admin/limpieza`) | Ídem |
| 72 | Salas privadas por invitación (solo a contactos) | Ídem |

## Lo que NO está verificado
- Ningún SQL 63–72 se ha ejecutado todavía en el Supabase real del proyecto.
- Llamadas LiveKit con dos cuentas reales; cámara/micrófono en móviles.
- Políticas reales de `storage.objects` (en la prueba son stubs).
- `next build` completo y E2E con navegador.

## Operación
- Variables de Vercel: `LIVEKIT_URL` (wss://…), `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` (marcar como Sensitive).
- Límites de llamadas: 20 por hora y persona; corte automático a los 30 min; token caduca a los 35 min.
- Privacidad: el local solo ve el nombre público de Network del cliente. Nada de lo privado se envía a IA.
- Pendiente: política de retención de mensajes, voz/vídeo con grabación (no hay ni se prevé), cola de moderación de chats de negocio.
