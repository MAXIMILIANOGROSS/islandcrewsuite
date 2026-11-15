# Derechos de contenido del mundo

Estado: diseño. **No se asume derecho de reutilización sobre nada.** La revisión de licencias la hace un profesional.

## Regla
Cada pieza de contenido (mapa, panorámica, foto, logo, marca, edificio, avatar, voz, *likeness*, datos de negocio, contenido de usuarios) se registra con su origen y derechos. Sin registro, no se publica.

## `WorldContentSource`
`id`, `source` (propio / negocio / partner / usuario / mapa abierto / externo), `rights` y `license` (texto y enlace), `contributor`, `captured_at`, `expires_at`, `attribution` (texto obligatorio a mostrar), `status` (pending / approved / rejected / expired / withdrawn), `reviewed_by`. Cada `Hotspot` y cada `Panorama` apuntan a una fuente; si está caducada o retirada, el contenido se oculta automáticamente.

## Fuentes y cautelas (a verificar con abogado y en los términos vigentes)
- **Mapa base:** OpenStreetMap con MapLibre es una opción técnica habitual; exige atribución (ODbL). Teselas: elegir proveedor cuyos términos permitan el uso comercial.
- **Street View / Google:** no se copian ni se descargan imágenes; no se hace *scraping*. Solo uso mediante el producto oficial y sus condiciones, si se decide.
- **Panorámicas de terceros** (por ejemplo, comunidades abiertas): revisar licencia concreta y requisitos de atribución/compartir igual.
- **Fotos propias o de negocios:** autorización escrita; los logos y marcas solo con permiso del titular.
- **Contenido de usuarios:** términos que concedan la licencia necesaria y mecanismo de retirada.

## Consentimiento del negocio
Un negocio real aparece solo si **reclama y verifica** su perfil, **acepta** su presencia y controla su información, su avatar de IA y su estado de contratación, y puede retirarse. Nunca se crean propietarios virtuales ni perfiles de negocios reales sin su autorización. Para demos: negocios ficticios etiquetados.

## Estados de fiabilidad visibles al usuario
verified · user_submitted · partner · external · estimated · AI-generated · unavailable.
