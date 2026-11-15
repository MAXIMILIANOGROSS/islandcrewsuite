# Island Crew World — UX

## Principios
1. **Exploración opcional, nunca obligatoria.** Todo lo que se hace caminando en el mapa debe poder hacerse con **lista, búsqueda y filtros**. Acceder a un trabajo no puede depender de moverse por un mundo.
2. **Móvil primero**, sin depender de gestos: cada gesto tiene botón equivalente.
3. **Fallback siempre:** si el mapa o un panel no carga, la lista funciona.
4. **Nunca inventar:** cada hotspot muestra su procedencia (verificado / aportado por usuario / partner / externo / estimado / no disponible) y la fecha de comprobación.
5. Movimiento solo si explica o confirma; `prefers-reduced-motion` respetado; sin sonido por defecto.

## Pantallas del MVP «Corralejo 2D»
| Pantalla | Móvil | Escritorio |
|---|---|---|
| Mundo (mapa + lista) | Mapa a pantalla completa, hoja inferior con lista y filtros (Trabajo, Vivienda, Market, Crew); botón «Ver como lista» | Mapa + panel lateral derecho (negocio, vacantes, vivienda) |
| Negocio | Ficha: estado (HIRING…), horario, vacantes, cultura, verificación; botones «Ver vacantes», «Preguntar», «Enviar perfil», «Guardar» | Misma ficha en el panel lateral |
| Cuestionario | Pasos cortos (experiencia, disponibilidad, idiomas, jornada, incorporación) con barra de progreso y «Salir» | Igual en modal |
| Resultado | «Tu respuesta se ha enviado. **El negocio decide**»; sin porcentaje de «persona válida» | Igual |
| Walk to Work | Ruta ordenada de negocios que contratan, distancia aproximada **solo si hay dato real**, con alternativa «ver lista» | Ruta sobre el mapa + lista |

## Estados obligatorios
Carga: esqueleto con la forma real. Vacío: explica qué probar («No hay negocios que contraten en esta zona: amplía la zona o ver Market»). Error: lenguaje humano + reintentar. Sin conexión / baja velocidad: modo lista.

## Goat
Aparece en onboarding, primer negocio explorado, resultado enviado y subida de nivel. Estados: idle, happy, encouraging, thinking, surprised, celebrating, level-up, success. Nunca bloquea el contenido ni es el único canal.

## Accesibilidad
Teclado completo (mapa navegable por lista de hotspots), lector de pantalla con descripciones textuales de cada punto, alto contraste, objetivos ≥ 44 px, alternativa no espacial, subtítulos si hay audio.

## Medición (sujeta a consentimiento donde corresponda)
`world_opened`, `zone_entered`, `hotspot_viewed`, `business_opened`, `prescreen_started/completed`, `job_applied`, `housing_viewed/saved`, `crew_created`, `list_view_used` (para saber cuánta gente prefiere lista).
