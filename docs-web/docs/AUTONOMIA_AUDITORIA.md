# Auditoría de autonomía · Island Crew (2026-11-02) · Fase A

Esto es una auditoría del CÓDIGO. No hay evidencia de producción aquí: para pasar de «hay código» a «funciona» falta mirar los registros reales (Supabase, GitHub Actions, el latido de la Oficina). Estados: CÓDIGO PRESENTE (hay implementación y tests, no verificado en producción) · PARCIAL · NO HECHO · BLOQUEADO (depende de algo externo).

| # | Criterio | Estado | Evidencia en el repo | Bloqueo / falta |
|---|----------|--------|----------------------|-----------------|
| 1 | Agentes ejecutan tareas reales | CÓDIGO PRESENTE | Ciclo 24/7 (`oficina-ciclo.yml` → `/api/oficina/ciclo` → `correrCiclo`), delegación, mentes, cola `office_tasks` | Depende de GitHub Actions (facturación) y de la IA configurada (`LLM_*`) |
| 2 | Tareas sobreviven a interrupciones | PARCIAL | Reclamo atómico, recuperación y latido (`/api/latido`, 503 si el ciclo tiene >45 min) | Sin prueba en producción de reanudación real |
| 3 | Coordinación sin trabajo duplicado | PARCIAL | `loopGuard`, `delegacion`, ids estables (`inst-…`) | No medido |
| 4 | Oportunidades comerciales reales | PARCIAL | Radar de negocios, tendencias, noticias, embudo de leads | Sin leads reales registrados (tú mismo lo dijiste) |
| 5 | CRM con leads reales | CÓDIGO PRESENTE | `/admin/crm`, `/admin/leads`, `embudoLeads.ts`, `ventas` | Vacío hasta que haya leads |
| 6 | Envío autorizado | PARCIAL | `emailSaliente.ts`, autorizaciones, aprobación delegada | Sin envío masivo automático (decisión tuya) |
| 7 | Respuestas disparan seguimiento | NO VERIFICADO | — | Falta comprobar el buzón/entrada de respuestas |
| 8 | Marketing medible | PARCIAL | `atribucion`, `metricas`, `publicidad` | Publicaciones públicas dependen del Mac (worker) y de tokens Meta/YouTube |
| 9 | Ingeniería detecta y corrige | CÓDIGO PRESENTE | `autonomous-engineering.yml`, `docs/AUTONOMIA_INGENIERIA.md`, parches con reglas y PR | Requiere `GITHUB_DISPATCH_TOKEN` y permisos de PR |
| 10 | Cambios probados antes de producción | CÓDIGO PRESENTE | `ci.yml`, 338 archivos de test, verificación de producción tras fusionar | — |
| 11 | Costes medidos y controlados | PARCIAL | `office_costes`, `CostesTab`, cuotas de IA | Presupuesto por proveedor no verificado |
| 12 | El aprendizaje mejora la ejecución | NO VERIFICADO | `/api/oficina/aprendizaje`, motor de evolución | Sin evidencia de efecto medible |
| 13 | Panel ejecutivo con datos reales | PARCIAL | `/despacho-de-direccion`, `/oficina` | Sin marca de frescura por métrica en todos los paneles |
| 14 | La oficina 3D refleja operaciones | PARCIAL | `world_events` (SQL 140), luces por sala, analizadores solo con eventos reales | Solo 3 de 16 tipos de evento tienen emisor completo |
| 15 | Parada de emergencia | CÓDIGO PRESENTE | `src/lib/oficina/control.ts`, «Detener oficina» | Paradas independientes por área: no verificadas |
| 16 | Opera sin coordinación manual | NO CUMPLIDO | — | Hoy hay 4 bloqueos: GitHub Actions, IA, el Mac (disco y worker), tokens Meta/YouTube |

## Bloqueos reales conocidos (a 2026-11-02)
1. Disco interno de la Mac con ~1,5 GB libres: la fábrica de música se niega a generar con <4 GB.
2. No hay proceso del subidor de publicaciones en marcha en la Mac (visto con `ps`).
3. (Descartado) Ollama SÍ tiene modelo: `qwen2.5:7b` (4,7 GB), comprobado con `ollama list` y la API local el 2026-11-02. Mi aviso anterior fue un error de inferencia.
4. GitHub Actions puede estar bloqueado por facturación; no verificado.
5. Tokens de Instagram/Facebook caducan cada pocas semanas.

## Siguiente paso recomendado
Medir antes de construir: ejecutar las consultas de comprobación (último ciclo real, tareas hechas/fallidas en 7 días, publicaciones por canal) y rellenar la columna «evidencia de producción».
