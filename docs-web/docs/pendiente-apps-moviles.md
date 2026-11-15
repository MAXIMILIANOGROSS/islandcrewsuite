# Pendiente para cuando se trabaje en las apps móviles (Island Crew)

Dejado preparado el 2026-10-07. Las RPC de Supabase ya sirven igual para web y móvil.

1. Flujo "Reclamar mi local real" (RR. HH./representante): pantallas móviles de buscar local OSM, formulario de reclamación y "Mis solicitudes". RPC: venue_claims (ver supabase/TODO_CORRER_36_LOCAL_REAL.sql). Web: /empresa/mi-local.
2. CV en locales verificados: botón "Dejar CV" (RPC drop_cv, tabla cv_drops). Solo en locales reclamados y verificados.
3. PvP solo ≥18: consentimiento (tabla pvp_consent, SQL 34). Sin consentimiento + edad verificada no hay PvP.
4. Chat / voz / café con conversación: bloqueado hasta revisión legal escrita (moderación, menores, privacidad, grabación de voz).
5. Verificación de reclamaciones: hoy manual por admin (/admin/claims); falta proveedor de identidad.
6. PvP en tiempo real: servidor en subdominio de islandcrew.es (ver docs/pvp-diseno.md). Visto bueno del abogado dado por teléfono el 2026-10-07; pendiente dejarlo por escrito.
