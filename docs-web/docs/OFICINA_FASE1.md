# Oficina · Fase 1 — auditoría, delegación y contrato de datos

## 1. Auditoría (estado real, sin suposiciones)
- **Agentes**: NO existen en la base de datos. Son 43 perfiles (30 originales + 13 de YouTube Studio) en `src/lib/oficina/agentes.ts` sobre un único LLM compartido. Las tareas guardan `agente` como texto.
- **Tablas** (SQL 87–89): `office_tasks`, `office_log`, `office_settings`, `office_kb`. Escrituras solo por funciones `security definer` o service role; lectura solo del administrador dueño (RLS).
- **Ciclo** (`/api/oficina/ciclo`, cron de GitHub Actions cada 15 min): reintentos con espera (15/30/60 min, máx. 3), idempotencia (pendiente→en_curso), atascadas >20 min → bloqueada, presupuesto diario, resumen diario. Nunca completa tareas.
- **Carencias antes de esta fase**: no había delegación, ni conexiones, ni latido, ni verificación, ni contrato de datos. "24/7" NO está demostrado: falta una ejecución real (ver §6).
- **Delegación hoy**: solo CIRO → agente, por reglas de enrutado (`enrutar`), no por IA. Marketing → Tecnología NO existe y no se ha forzado.

## 2. SQL 90 (preparado y validado en una base PostgreSQL local de prueba; NO ejecutado en producción)
Archivo `TODO_CORRER_90_OFICINA_DELEGACION.sql` (reversión: `TODO_REVERTIR_90_...`). Decisiones:
- Se amplía `office_log` (agente, connection_id, payload, idempotency_key) en vez de crear `agent_events` paralela.
- `office_connections` (tarea, origen, destino, estado, dirección, cierre). Un agente no puede conectarse consigo mismo; sin duplicados por (tarea, origen, destino).
- Disparador `office_sync_conexion`: abre/actualiza/cierra la conexión y registra el evento en la misma transacción que la tarea. En curso = active; pendiente/revisión/aprobación/bloqueada = paused; completada = completed; fallida = failed; cancelada = cancelled.
- `verificado` solo es true cuando el CEO completa la tarea (verificación humana).
- `office_heartbeat`: lo escribe el ciclo (service role) en cada ejecución.
- RLS: lectura solo del administrador dueño; ninguna escritura desde el cliente.
- El código desplegado funciona igual sin el SQL 90 (el latido se ignora).

## 3. Pruebas ejecutadas
- SQL: aplicado 87→90 y 90 repetido sin error; creación/estados/cierre de conexión; verificado solo al completar; autoconexión, duplicados y verificado sin completada rechazados; no administrador y otro dueño sin acceso; anon sin acceso; escritura directa denegada.
- Código: `tests/oficina-delegacion.test.mjs` (estados de conexión, regla de conexión, latido, estado real del agente).

## 4. Contrato de datos para la oficina 3D: `select office_snapshot();`
JSON: `servidor_ahora`, `latido {ultimo_ciclo_at, antiguedad_s, estado: ok|sin_senal|desconocido}`, `tareas[]` (id, agente, area, nivel, estado, parent_id, delegada_por, verificado, intentos, error, tiene_resultado, instruccion≤120, fechas), `conexiones[]` (id, task_id, from_agente, to_agente, status, direction, fechas), `eventos[]` (últimos 50: tipo, agente, task_id, connection_id, detalle, at). No incluye resultados completos, prompts ni claves. El estado del agente se deriva con `estadoReal()` (src/lib/oficina/delegacion.ts).
Ejemplo real de conexión: `{"status":"completed","direction":"one-way","from_agente":"ciro","to_agente":"marketing"}`.

## 5. Despliegue
1. Revisar el SQL 90 y probarlo primero en un proyecto Supabase de pruebas (o rama).
2. Ejecutarlo en producción solo tras esa prueba. Guardar la reversión.
3. Esperar un ciclo y comprobar `latido: true` en la respuesta del endpoint y `office_snapshot()`.

## 6. Pendiente antes de la Fase 2
- Demostrar el ciclo con una tarea real de extremo a extremo (encolar → Actions → en revisión) y con el navegador cerrado.
- Delegación entre agentes (Marketing → Tecnología) y consolidación por CIRO: requieren que el resultado del LLM proponga una subtarea y que el CEO la apruebe; aún no implementado.
- Tiempo real (Supabase Realtime) y detección de agentes sin actividad más allá del latido global.
