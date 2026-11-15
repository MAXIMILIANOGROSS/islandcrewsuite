# Auditoría Fase 0 · Business Radar (30-oct-2026)

Ruta real: `/admin/radar` (no existe `/dashboard/business-radar`). Solo lectura del repositorio `island-crew-web`.

## Qué existe y funciona (con pruebas)
- CRM: `crm_prospects`, `crm_interactions` (RLS sin políticas, solo clave de servicio). API `/api/admin/crm` con paginado, filtros y `?puntos=1`.
- Escaneo OSM de las 8 islas por lotes (≤300), deduplicado por `osm_id` y por nombre+zona.
- Mapa MapLibre con capa GeoJSON (hasta 5000 puntos).
- Puntuación explicable (prioridad de trabajo, no probabilidad), contacto preparado (nunca envío automático).
- Asistente de mensajes (es/en/it/de) y chat de la cabra: solo redactan borradores.
- 60 agentes (cabras), Oficina virtual, scheduler y colas existentes: se reutilizan, no se duplican.
- ~326 ficheros de test; suite completa en verde antes de esta fase.

## Qué NO existe
- Multi-tenant: no hay `tenant_id` en ninguna migración. Requiere cambio estructural y aprobación.
- Rutas de visita, seguimiento automático, informe semanal, reescaneo programado, centro de salud.
- Facturación/ingresos reales: no hay datos; ningún indicador puede mostrarse como real.

## Riesgos
- GitHub Actions detenido por facturación de la cuenta (no es un fallo de código).
- Disco del Mac casi lleno en ocasiones.
- La validación de teléfonos es solo de formato.

## Fase 1 (esta entrega): verificación asistida
Toco: `src/lib/radar/verificacion.ts`, `/api/admin/radar-verificacion`, `/admin/radar/verificacion`, SQL 135. No toco: puntuación, escaneo, contacto.
Riesgo: fusión equivocada → mitigado: solo archiva y guarda instantánea para revertir.
Prueba: `tests/radar-verificacion.test.mjs`.

## Siguiente
Rutas de visita → seguimiento → informe semanal → reescaneo → salud → embudo.
