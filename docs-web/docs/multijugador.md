# Island Crew World — multijugador (web)

Estado: ACTIVADO por defecto en `/mundo/jugar` y `/mundo/downtown` (visto bueno legal indicado por el fundador). Se desactiva con `?multi=0` u `?offline=1`. Sin chat libre ni voz.

## Qué hay
- Presencia en tiempo real por Supabase Realtime (canal `world-corralejo-1`, mensajes broadcast; sin tablas ni almacenamiento).
- Se ve a otros jugadores caminar (interpolación a 5 Hz), con su alias encima. Máximo 24 visibles.
- Saludo con la tecla G. No hay chat libre ni voz.
- El mundo ya es compartido por construcción: reloj, horarios, estados de negocio y eventos salen de la hora y la fecha reales.

## Límites honestos
- No es servidor autoritativo: cada cliente decide su posición. Vale porque nada con valor real depende de ello (reputación, trabajo y resultados son ficción local y no dan XP).
- Una sola instancia. Con más de ~24 jugadores simultáneos hay que repartir en instancias (`WORLD_CHANNEL(n)`).
- Reputación/trabajo compartidos entre jugadores (que otro jugador te recomiende, que un restaurante recuerde a varios jugadores) exigen backend con tablas y RLS: siguiente fase.

## Para el abogado antes de abrirlo
- RGPD: posiciones y alias en tiempo real (efímeros, no se guardan); información al usuario; base legal.
- Mayoría de edad / menores, moderación y denuncia de jugadores, bloqueo.
- Chat de texto y voz: diferidos hasta tener moderación y revisión legal.
- Alias: nunca nombre real ni id de cuenta; filtro de caracteres (`cleanAlias`).
