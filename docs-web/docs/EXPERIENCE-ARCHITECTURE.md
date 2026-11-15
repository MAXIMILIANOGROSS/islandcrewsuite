# Island Crew · Arquitectura de la experiencia

Idea de producto: **no estoy mirando un mapa, estoy entrando en el mundo.** Todo parte de un lugar (Corralejo), no de un formulario.

## Principios (no negociables)
1. **Real o etiquetado.** Cada dato es real (con su fuente), una sugerencia declarada, o algo «en el juego». Nunca cifras inventadas: sin «12 personas ahora» hasta tener un contador real.
2. **Estado visible de cada integración** (`src/lib/integrations.ts`): activo · parcial · planificado. La portada lo muestra.
3. **Empezar sin registro.** Intención + intereses viven en el dispositivo (`ic_explora_v1`). La cuenta se pide cuando aporta algo.
4. **Privacidad por defecto.** La ubicación se redondea a ~110 m, se usa solo en el dispositivo y no se envía ni guarda. Nunca se muestra la posición de otras personas.
5. **Confianza.** Etiquetas: «dato real», «recomendado para ti», «oferta», «oferta de empleo», «en el juego», «patrocinado» (reservado; aún no hay patrocinio).
6. **Economía después de la experiencia.** Primero «¿qué puedo hacer?», luego la transacción.

## Navegación (5 secciones)
Explorar `/explora` · Descubrir `/explora#hoy` · Crew `/mundo/real?open=gente` · Oportunidades `/swipe` · Mochila `/explora/mochila`.

## Módulos y dónde viven
| Módulo | Código | Datos | Estado |
|---|---|---|---|
| Portal inmersivo | `app/explora`, `components/explora/ExploraScene` | hora de Canarias, Open-Meteo | activo |
| Intención + intereses | `lib/explora.ts` (INTENTS, INTERESTS) | local | activo |
| Hoy en Corralejo | `lib/explora.ts` `buildToday` | clima, mar, sol, empleo, ofertas partner | activo |
| Cerca de ti | `app/explora` | `public/data/corralejo-places.json` (OSM/Overture) | activo |
| Mochila / Pasaporte | `app/explora/mochila`, `lib/explora-profile.ts` | `loadCrew()` (Legacy) | parcial |
| Business Hub | SQL 48, `app/empresa/panel`, `components/VenueOffers` | Supabase (RPC) | parcial |
| Mundo 3D | `components/RealTownWorld` | OSM | activo |
| Multijugador | `lib/worldNet.ts` | Supabase Realtime | parcial |

## Escalado por destino
Un destino es datos, no código: centro geográfico, `places.json`, capa OSM, reglas de zona (`lib/canary.ts`) y su lista de negocios partner (claimed_venues por `osm_id`). Corralejo → Fuerteventura (`lib/fuerte.ts`) → Canarias.

## Siguientes entregas (por valor/riesgo)
1. Contador de presencia real (Realtime presence) para «personas explorando ahora».
2. Fecha en cada hito (diario real) y sincronización de Mochila en servidor.
3. Experiencias con fotos/vídeo autorizados por el negocio y ficha inmersiva.
4. Reservas con pago (pasarela + revisión legal turística) tras 3–5 partners reales.
5. Notificaciones útiles y poco frecuentes (web push), con consentimiento.
6. Carriles de recomendación aprendidos de la actividad real (hoy: reglas por intereses).

## Accesibilidad
Navegación por teclado y foco visible, etiquetas ARIA, `prefers-reduced-motion`, botón de texto grande, contraste alto en navegación y tarjetas.
