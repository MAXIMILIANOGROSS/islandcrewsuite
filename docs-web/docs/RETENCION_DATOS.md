# Retención de datos de Network, salas, llamadas y chat de negocio

Principio: guardar lo mínimo y solo el tiempo necesario. Estado: SQL 73 + página `/admin/limpieza`. La purga es MANUAL (no hay planificador desplegado) y siempre en dos pasos: calcular y confirmar.

| Dato | Cuándo se purga | Excepción |
|---|---|---|
| Mensaje directo borrado por su autor | N días tras borrarlo (30/90/180/365) | Si tiene denuncia abierta, se conserva hasta resolverla |
| Mensaje de sala borrado | Ídem | Ídem |
| Chat de negocio cerrado por el local | N días tras cerrarlo | — |
| Registro de llamadas | 30 días | — |
| Invitaciones a salas privadas sin responder | 30 días | — |
| Fotos adjuntas sin mensaje ni publicación | Tras 1 día (limpieza de huérfanas) | — |

No se purga: mensajes vivos, denuncias abiertas, historial de moderación resuelto. Las llamadas no se graban ni se transcriben. Nada de lo privado se envía a IA sin autorización.

Pendiente: aviso de retención dentro de la política de privacidad pública, y automatizar la purga cuando exista planificador (con registro de lo purgado).
