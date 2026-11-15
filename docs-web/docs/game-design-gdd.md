# Island Crew World — Game Design + Technical Architecture Blueprint

> Borrador de diseño. Nada de esto está construido salvo lo indicado en "Estado actual". Las notas de proyecto de abajo mandan sobre el resto del documento.

## Frases de la primera página
- "No diseñamos misiones para que el jugador tenga algo que hacer. Diseñamos un mundo que hace que el jugador quiera descubrir qué hacer."
- "Cada calle debe poder generar una historia."
- "Cada persona puede convertirse en una oportunidad."

## Notas de proyecto (críticas, prevalecen)
1. **Dos capas separadas.** Ficción: dinero, habilidades 0–100, ascensos y reputación del personaje dentro del juego. Realidad: vacantes, solicitudes y entrevistas verificadas por el backend. El dinero del juego no es dinero real ni se presenta como tal. XP ≠ reputación ≠ puntos. El progreso real lo concede el backend por acciones reales, nunca por pasear. No se gamifica a la persona: se reconoce su progreso real.
2. **Negocios y personas reales solo con consentimiento firmado y revisado.** Si no, ficticios y marcados. Un NPC no representa a una persona real sin su permiso. Ningún NPC dice condiciones laborales reales que el negocio no haya publicado.
3. **Alcance.** Primero el vertical slice mínimo en la web (ya existe): una calle, un negocio, una oportunidad real, una conversación. Unreal, Motion Matching, Mass y microservicios esperan a que los datos de uso lo justifiquen. Supabase cubre el backend inicial (`hotspots`, `job_vacancies`).
4. **IA generativa:** el estado (dinero, contratos, progreso) lo controla siempre el juego, nunca el modelo. NPC con IA hablando como un negocio real queda apagado hasta consentimiento y revisión legal.
5. Alternativa no 3D siempre disponible (`/mundo` lista y mapa).

## Visión
Videojuego social de exploración en primera persona donde el mundo real es jugable. Empieza en Corralejo → Fuerteventura → Canarias. El progreso es mejorar tu posición en un mundo social y económico, no subir de nivel para combatir.

## Principio principal: vertical slice
1 zona (Corralejo), 10–20 NPC, ~10 negocios, 5–10 oportunidades, 1 sistema de conversación, 1 de trabajo, 1 economía, ciclo día/noche, 1 de reputación, 1 progresión. Si funciona en 1 km², se escala.

## Core loop
Explorar → observar → descubrir → acercarse → interactuar → conversar → descubrir oportunidad → decidir (aceptar, preguntar, rechazar, guardar, volver luego, recomendar) → actuar → consecuencia → progresar → explorar más.

## Jugador
Identidad (nombre, apariencia, idioma) y estado (dinero, energía, reputación, habilidades, relaciones, trabajos, vivienda, inventario, contactos, oportunidades).

## Sistemas
- **Habilidades profesionales/sociales (0–100):** hostelería, atención al cliente, cocina, idiomas, ventas, organización, liderazgo, tecnología, marketing, turismo.
- **Reputación y red:** trabajo → reputación → contactos → oportunidades → mejores trabajos → mayor ingreso.
- **Relaciones por NPC:** confianza, respeto, afinidad, historial, experiencias compartidas. Se guarda `relationship_score`, eventos importantes, flags y última interacción; no conversaciones completas.
- **Trabajo:** tareas, decisiones, presión, calidad, tiempo, relaciones, recompensa. Observar → decidir → actuar; sin simulador tedioso.
- **Economía:** ingresos, gastos, alquiler, comida, transporte, ocio, ahorro. Sin regalar dinero; que se sienta, no que se estudie.
- **Vivienda progresiva:** habitación → compartido → apartamento → casa → propiedad.
- **Tiempo y clima:** 1 h real ≈ 4–6 h de juego; amanecer a noche; viento visualmente importante en Fuerteventura.
- **Misiones por datos (no hardcodeadas):** MissionID, título, objetivos, requisitos, recompensas, diálogo, actores, lugares, estados, consecuencias. Tipos: Discovery, Opportunity, Life (cadenas como "conoces a Juan → te recomienda").
- **Eventos del mundo:** NPCEvent, BusinessEvent, JobEvent, SocialEvent, EconomicEvent, TravelEvent. Estados de negocio: OPEN, BUSY, SHORT_STAFFED, CLOSED, HIRING, EVENT.
- **Negocio como entidad de datos:** id, tipo, ubicación, reputación, empleados, abierto, contratando.
- **NPC:** identidad, personalidad, horario, necesidades, relaciones, memoria, habilidades, empleo, diálogo, objetivos. IA en tres niveles: GOAP/Utility, máquina de estados, animación y navegación.
- **Diálogo:** estado del juego → gestor de diálogo → (modelo) → validación de seguridad y lore → jugador. Un manager no ofrece trabajo a quien ya trabaja 60 h.

## Guion de misiones 001–020 (resumen)
001 Llegada sin tutorial artificial · 002 primer NPC local · 003 primera oportunidad (★ 1 OPORTUNIDAD, [E] HABLAR) · 004 primer día de trabajo · 005 conocer al equipo · 006 segundo restaurante, decisión de dejar el trabajo · 007 El Ancla: requisito de habilidad no cumplido · 008 mejorar · 009 recomendación · 010 hotel · 011 elegir trayectoria sin bloqueo permanente · 012 contacto/networking · 013 evento local · 014 decisión entre tres ofertas (no solo salario) · 015 ascenso · 016 abrir actividad propia · 017 vida social · 018 descubrir la isla · 019 el viaje · 020 la vida que has construido (sin "YOU WIN").
Los nombres de negocios de ejemplo son ficticios.

## Arquitectura técnica objetivo (largo plazo)
Cliente Unreal Engine 5: World Partition, Nanite, Lumen, Virtual Shadow Maps, Niagara, PCG (distribuye, los artistas controlan), Smart Objects + NavMesh, Motion Matching, Mass para multitudes, LOD de NPC (0–20 m completo, 20–50, 50–100, 100+ impostor), audio por capas (ambiente, negocios, jugador). Backend por servicios (identidad, mundo, negocios, empleos, social, economía, inventario, progresión, analítica, notificaciones), base de datos separada en jugador / mundo / analítica. Estado de oportunidades servido en vivo desde servidor. Objetivo 60 fps. Multijugador solo después: single-player online → mundo social compartido → persistente.

## Real vs juego (privacidad y moderación)
Separar identidad de juego e identidad laboral real. No guardar documentos, datos bancarios ni conversaciones privadas innecesarias. Moderación de jugadores, diálogos de NPC, negocios y oportunidades; antifraude con estados Verified / Pending / Suspended. Aplicar a una oportunidad real lleva al flujo real con consentimiento.

## Telemetría y métricas
Eventos: PLAYER_ENTER_BUSINESS, PLAYER_TALK_NPC, PLAYER_DISCOVER_OPPORTUNITY, PLAYER_ACCEPT_JOB, etc. Métricas: discovery rate, interaction rate, opportunity conversion, exploration rate, return rate, social depth. KPI principal: **Meaningful Discovery Rate** (descubrimientos significativos por hora).

## Fases
0 Preproducción (6–10 semanas) · 1 First Playable: 1 calle, 1 restaurante, 1 NPC, 1 oportunidad, 1 conversación, 1 trabajo · 2 Vertical Slice (zona costera, 5 restaurantes, 1 hotel, 3 tiendas, 20–30 NPC, 10 oportunidades, economía, relaciones, día/noche, audio, clima, save) · 3 Alpha (2–4 h) · 4 Beta (10+ h) · 5 Live World.
MVP real: Corralejo 1 km², 50–100 NPC secundarios + 10 importantes, 10–15 negocios, 20 oportunidades, 5 categorías de trabajo, 20 misiones principales y 50 secundarias.
No hacer al principio: MMO, conducción avanzada, combate, armas, cientos de km, VR, metaverso, construcción ilimitada.

## Posicionamiento
"A real-world life exploration game": no un juego de trabajos. Las oportunidades del mundo virtual pueden conectarse con las reales, y eso lo convierte de juego en plataforma, siempre con consentimiento, verificación y moderación.

## Estado actual (octubre 2026)
Construido en la web: mapa 2D, caminar 2D, primera persona (three.js) con HUD y vacantes reales, negocios verificados, reclamación de negocio, vacantes, telemetría mínima de World (`world_events`, SQL 27). Vertical slice en el navegador (`/mundo/jugar`, lógica en `src/lib/sim.ts`): calle, encargada ficticia en un local de demo con [E] HABLAR a ≤2,5 m con línea de vista, entrevista por fases con evaluación por factores, memoria del NPC, habilidades y reputación de juego (guardadas en el navegador, no en el backend), reloj y luz día/noche, viento, peatones según la hora y mundo que no se congela al hablar. Interior del restaurante (puerta abierta, barra, mesas, clientes, camarero) y turno de trabajo en el mundo (mesas piden atención, [E] ATENDER, resultado excelente/correcto/flojo que cambia reputación y habilidades de juego; un turno de prueba bien hecho pasa a contrato). Mundo vivo (`src/lib/worldsim.ts`): horario de la encargada por franja (prepara, trabaja, descansa, se va), restaurante abierto de 09:00 a 00:00 con estados CLOSED/QUIET/OPEN/BUSY según hora y eventos, demanda que decide cuántos clientes se ven, evento de fin de semana de turismo (más gente y mesas más rápidas), economía básica derivada, rumores que se descubren al no ser contratado, registro por canales y panel de desarrollador (`?dev=1`, solo admin). No construido: dinero y precios, eventos, audio, grafo social, NPC con rutinas completas, fotorrealismo, Unreal.
