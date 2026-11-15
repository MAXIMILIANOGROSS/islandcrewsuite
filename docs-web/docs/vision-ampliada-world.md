# Island Crew World — visión ampliada (guardada tal cual la planteó el fundador)

Frase guía: «No vienes a jugar una partida. Vienes a vivir unos días en Corralejo.»

## 7 pilares
Mundo (explorar Corralejo) · Personas (NPC + jugadores) · Trabajo (profesiones y oportunidades) · Conversación (relaciones y decisiones) · Descubrimiento (lugares, secretos, tesoros) · Economía (dinero, objetos, intercambio) · Tiempo real (eventos y mundo vivo).

## Capas del mundo
1 Lugares · 2 Personas · 3 Oportunidades · 4 Jugadores · 5 Tiempo · 6 Estado del mundo.

## Estado actual frente a la visión (honesto)
| Idea | Estado |
|---|---|
| Primera persona, calle, restaurante interior, caminar/correr/saltar | Hecho (web, three.js) |
| Reloj, horarios, estados de negocio, eventos, rumores | Hecho (`worldsim.ts`) |
| Entrevista dentro del mundo, memoria de Marta, reputación/habilidades de juego | Hecho (`sim.ts`) |
| Turno de camarero: comanda, cocina, bandeja, servir, cobrar | Hecho |
| Progreso de juego (nivel, dinero de juego, descubrimientos, contactos) | Hecho (`gameprog.ts`), separado del XP real |
| Brújula, audio ambiente, manos, farolas, playa y embarcadero | Hecho |
| Multijugador de presencia (ver, saludar) | Prototipo tras `?multi=1` |
| Oficina Island Crew con tablón de ofertas reales y Market | Hecho (panel; la sala 3D con zonas aún no) |
| Teléfono virtual («Corralejo ahora»), mensajes de NPC | Falta |
| Pasaporte Island Crew (historial: trabajos, habilidades, descubrimientos, contactos, logros) | Falta (los datos ya existen en parte) |
| Misiones 001-008 (bienvenida, registro, examen de manipulador) | Falta |
| Puestos de cocina y recepción jugables | Falta |
| Objetos perdidos / tesoros / colecciones / rareza diaria procedural | Falta |
| Trueque y mercado entre jugadores | Falta (exige backend y revisión legal) |
| Vacantes limitadas y competencia entre jugadores | Falta (backend compartido) |
| Relaciones graduadas con NPC (conocido→aliado, rival) | Parcial (un valor numérico) |
| Clima que cambia misiones, transporte, emprendimiento | Falta (fases tardías) |

## Reglas de nuestro propio proyecto que prevalecen sobre esta visión
- El progreso de juego (XP, dinero, nivel, rarezas) es ficción y vive aparte del XP/reputación/puntos reales de la plataforma. Sin rankings de XP.
- Las ofertas reales y las del juego conviven en el mundo, cada una etiquetada como REAL o JUEGO (ver decisión al final).
- Lo que el jugador «consigue» en el juego no es una oferta ni un empleo reales.
- Sin chat libre ni voz hasta tener moderación y revisión legal.

## Puntos para el abogado antes de abrir
- Caza del tesoro con recompensas y eventos con premios (promociones/sorteos, bases legales).
- Objetos aleatorios y rarezas: confirmar que no encajan como «loot box» mientras no haya pago.
- Intercambio entre jugadores y dinero de juego: que no tenga valor económico ni sea convertible.
- Datos de jugadores en tiempo real, menores, moderación y denuncia.
- Negocios y personas reales dentro del mundo (consentimiento, imagen, marcas).

## Fases propuestas
- **F1 (ahora)**: Oficina como sala 3D (recepción, panel de empleo, tablón), misiones 001-004 de llegada y registro, Pasaporte.
- **F2**: examen de manipulador (misiones 006-008), puesto de cocina jugable, teléfono con «Corralejo ahora».
- **F3**: objetos perdidos y tesoros diarios, colecciones, rumores con pistas, más locales y NPC con horarios.
- **F4**: backend compartido: vacantes limitadas, recomendaciones entre jugadores, reputación por ámbito, trueque con confirmación de ambos.
- **F5**: eventos semanales, caza del tesoro, equipos, clima y transporte; emprendimiento mucho más tarde.

Indicador de éxito del MVP: que alguien quiera quedarse otros 10 minutos y volver mañana.

## Decisión del fundador: todo real y virtual
Las ofertas de trabajo reales y el Market SÍ se mezclan con el juego (tablón de la Oficina, teléfono, misiones Q011 y Q012). Reglas: cada elemento se etiqueta REAL o JUEGO; los resultados dentro del juego nunca equivalen a una contratación real; el progreso de juego sigue separado de la reputación real. Punto para el abogado: mezcla de ofertas reales con misiones de ficción.
