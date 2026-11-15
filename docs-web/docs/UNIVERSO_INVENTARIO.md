# Island Crew Universe · inventario real (2026-10-10)

Una sola cuenta (Supabase Auth) sirve a web, mundo y red. No hay app móvil nativa de Island Crew en este repositorio.

## IMPLEMENTADO Y VERIFICADO (por el fundador en producción)
- Cuenta única y sesión compartida web ↔ /mundo/real ↔ /network.
- Network: perfil, publicaciones, reacciones, comentarios, contactos, bloqueos, mensajes, avisos.

## IMPLEMENTADO, PENDIENTE DE PRUEBAS CON CUENTAS REALES
- Empleos verificados, candidaturas, gestión por el negocio (SQL 56).
- Ranking v2 y misión 1 con puntos del servidor (SQL 52, 57).
- Experiencia/formación declaradas, perfil público, editar/compartir/ocultar (SQL 58).
- Imágenes en publicaciones, bucket privado (SQL 59).
- Puente mundo ↔ red (este commit): pestaña «Network» en la bitácora del juego con feed real, ofertas verificadas reales y «Compartir un momento» solo tras confirmar el texto.

## DISEÑADO, NO IMPLEMENTADO
- Multijugador en tiempo real (avatares sincronizados, grupos). Presencia «En la zona ahora» ya existe (voluntaria, informativa, no autoritativa, sin movimiento). Hoy el mundo es de un jugador; los «amigos» del juego son una lista, no presencia. Requiere servidor de estado (p. ej. Supabase Realtime o servidor dedicado) y validación autoritativa. Primer paso propuesto: presencia (quién está en la zona) con Realtime Presence, sin movimiento.
- Registro común de lugares (places) enlazando negocio ↔ mapa ↔ juego ↔ vacante. Hoy los lugares del juego y business_accounts son tablas separadas.
- Misiones de negocio y misión «de prueba» vinculada a una vacante real (la candidatura siempre explícita y sin puntuación de juego como criterio).
- NPC con IA conectados a datos autorizados.
- Eventos con esquema versionado entre módulos (hoy se usan RPC y triggers puntuales).
- Vídeo, voz, grupos, eventos de comunidad, páginas de empresa públicas.

## BLOQUEADO / PENDIENTE DE DECISIÓN
- Cobros reales (hasta tener empresa real).
- App móvil (no existe en este repositorio).
- Motor Unreal: el mundo actual es Three.js en la web; si hay un proyecto Unreal aparte, no está en este repositorio.
- Revisión legal: privacidad, condiciones, RGPD, moderación.

## Primer flujo completo que ya funciona (con la parte web del mundo)
1. Entras con tu cuenta y exploras /mundo/real; la misión 1 te da 100 puntos del servidor.
2. En la bitácora → «Network» ves tu feed real y las ofertas verificadas reales.
3. Editas el texto sugerido, eliges audiencia y publicas; aparece en /network y en tu perfil público.
4. Desde allí sigues por mensajes, perfil y /empleos.
