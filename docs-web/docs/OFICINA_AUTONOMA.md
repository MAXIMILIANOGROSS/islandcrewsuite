# Oficina virtual de Island Crew — entrega de reparación y autonomía

Estado a 2026-10-14. Distingo siempre: **implementado**, **probado** (tests automáticos locales o prueba manual del dueño), **configurado** y **pendiente**.

## 1. Qué se hizo

| Área | Implementado | Cómo se comprobó |
|---|---|---|
| Parada de emergencia + panel de salud | Botón DETENER/Reanudar, estado, alertas, historial de ciclos (`/oficina` → Control y salud) | Tests de lógica; el dueño probó el panel |
| Ciclo fiable | Bloqueo único de ciclo en BD, log de ciclos (`office_ciclos`), el ciclo respeta la parada, errores de configuración no se reintentan | Tests de lógica; ciclo manual probado por el dueño |
| Tareas ↔ entregables | Cada tarea guarda entregables con versión y sha256 (idempotente) | Tests + visor en la tarea |
| Investigador | Búsqueda web real (Exa; Serper/Tavily como alternativa). Fuentes y URLs solo del buscador | Tests + prueba del dueño |
| Analista de leads | Análisis determinista (duplicados, incompletos, seguimiento ≥3 días); no envía datos personales al modelo | Tests |
| Productor creativo | Genera texto y revisión con el kit de marca. No genera imágenes | Tests |
| Director de operaciones | Analiza la cola de tareas sin IA y propone; no crea ni reasigna | Tests |
| Libro de costes | Registra llamadas por tarea/agente | Tests |
| Informe diario del CEO | Generado desde datos reales; auto en el ciclo tras la hora de resumen; también manual | Tests + prueba del dueño |
| Permisos por agente | Definidos en código (`permisos.ts`), comprobados en servidor; 3 niveles de autonomía; un agente no puede cambiar sus permisos ni saltarse la parada | Tests |

## 2. Migraciones SQL
87 a 101 ejecutadas (97–99 y 100–101 confirmadas por el dueño; 100 → costes/tarifas true, 101 → informes true).

## 3. Variables de entorno (Vercel)
`SUPABASE_SERVICE_ROLE_KEY` (clave **service_role**, nunca la anon), `CRON_SECRET`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, y `EXA_API_KEY` (o `SERPER_API_KEY` / `TAVILY_API_KEY`).

## 4. Cron
GitHub Actions cada 15 min llama a `/api/oficina/ciclo`. No se ha verificado directamente la ejecución del workflow; se infiere de las filas nuevas en `office_ciclos`.

## 5. Limitaciones honestas
- Los tokens son **estimados** (el proveedor no los devuelve). El coste en € solo aparece si hay una tarifa registrada en `office_tarifas`; ahora no hay ninguna.
- El informe no se envía por email.
- Productor creativo no genera imágenes.
- Los permisos no se editan desde la interfaz (solo en código).
- El Director solo propone.
- No hay envío de mensajes reales ni gasto automático.

## 6. Checklist de pruebas manuales A–I (con servicios reales)
- **A. Parada:** DETENER → lanzar ciclo → debe negarse; Reanudar → funciona.
- **B. Ciclo:** "Ejecutar ciclo ahora" crea fila en Últimos ciclos; dos a la vez → el segundo se bloquea.
- **C. Entregables:** una tarea completada muestra su entregable con versión.
- **D. Investigador:** orden de mercado → entregable con URLs reales; sin clave de búsqueda → tarea bloqueada con mensaje claro (sin reintentos).
- **E. Leads:** análisis sin datos personales en el resultado.
- **F. Productor:** pieza de texto con el kit de marca; no promete imágenes.
- **G. Director:** informe de cola con tareas atascadas/duplicadas.
- **H. Costes:** aparecen llamadas por agente; sin tarifa, el € figura como "sin tarifa".
- **I. Informe diario:** se genera una vez al día y coincide con las tareas reales.

## 7. Siguientes mejoras sugeridas
Cargar tarifas reales; UI de permisos; envío del informe por email (con aprobación); contar tokens reales si el proveedor los ofrece; verificar el workflow de GitHub Actions.
