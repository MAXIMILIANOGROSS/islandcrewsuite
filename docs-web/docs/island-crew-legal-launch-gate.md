# Legal Launch Gate — extensión para Island Crew World

El documento base está en `legal-privacy-launch-gate.md`. Esta extensión añade las áreas que introduce World. **Ninguna se activa a usuarios reales hasta que su estado sea `APPROVED_FOR_BETA` o superior** y su interruptor esté encendido.

## Áreas nuevas para `launch_gate` (se añadirán con una migración cuando se construya)
`world_exploration`, `world_content_rights`, `business_presence` (negocios reales en el mundo), `business_ai`, `virtual_interviews`, `avatars`, `location_data`, `social_presence`, `world_analytics`.

## Qué debe revisar un profesional
RGPD (bases, minimización, retención, derechos, encargados, transferencias), datos de empleo, perfilado y decisiones automatizadas, Reglamento de IA (selección de personal, prohibiciones; fechas **a confirmar**), derechos de imagen/contenido/mapas, consentimiento de negocios, privacidad de ubicación, cookies/analítica, seguridad social (bloqueo, denuncia, moderación), puntos y recompensas, Market, seguros (solo vía corredor/MGA autorizado), rol de Island Crew en empleo y vivienda.

## Estados oficiales
`TECHNICALLY_READY → PRIVACY_REVIEW_PENDING → LEGAL_REVIEW_PENDING → SECURITY_REVIEW_PENDING → APPROVED_FOR_STAGING → APPROVED_FOR_BETA → APPROVED_FOR_PUBLIC_LAUNCH`. No se pasa a público sin completar los gates.

## Modo de desarrollo
Permitido: construir, diseñar, probar con **datos ficticios**, staging, usuarios internos. No permitido: asumir aprobación, activar públicamente, recoger datos reales innecesarios, usar datos laborales reales sin base y documentación, activar recompensas económicas o transacciones reales sin revisión.
