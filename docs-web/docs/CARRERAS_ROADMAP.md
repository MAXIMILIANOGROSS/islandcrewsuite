# Island Crew World · Carreras de hostelería

Estado real a 16-10-2026. Lo que existe, lo que falta y qué recursos externos hay pendientes de verificar.

## Ya implementado (con tests)
- Motor de carreras por datos (`src/lib/carrera/motor.ts` + `datos.ts`): 56 habilidades, 39 puestos en 9 familias (cocina, sala, bar, recepción, pisos, economato, mantenimiento, eventos, dirección), 33 misiones.
- Nivel de habilidad deducido de evidencias en misiones distintas; repetir la misma misión no sube el nivel. Una infracción crítica anula las evidencias del intento.
- Ascensos con requisitos de habilidades, misiones y platos distintos; cambio de rama por puestos de entrada conservando habilidades; guardado versionado que rechaza datos dañados.
- Misión jugable de Freganchín (`fregadero.ts`, 3 turnos) dentro de la cocina 3D.
- Cada plato servido en la cocina 3D cuenta como misión distinta (`plato:<receta>`).
- Pantalla `/carrera`.

## Jugable hoy
Freganchín → Auxiliar de cocina → Ayudante de cocina.

## Definido como datos, aún sin misión jugable
Cocinero de partida en adelante y las ramas de sala, bar, recepción, pisos, economato, mantenimiento, eventos y dirección. Las misiones están marcadas «pendiente» y bloquean el ascenso.

## Pendiente (en este orden)
1. Misiones de auxiliar de cocina (mise en place, etiquetado, reposición).
2. Varias comandas simultáneas y turno completo (cocinero de partida).
3. NPC con tareas y asignación (segundo de cocina).
4. Sala y barra con el mismo motor.
5. Integración con Academy y Talent solo cuando existan interfaces y estén probadas.
6. Personajes y animaciones (modelos 3D con licencia verificada).

## Recursos externos: estado de licencias
Ninguno está incorporado todavía. Antes de usarlos hay que abrir la página oficial de cada uno, copiar la licencia exacta y guardar la evidencia.

| Recurso | Lo que indica tu documento | Estado |
|---|---|---|
| Quaternius Universal Base Characters / Animation Library | CC0 | Sin verificar por mí |
| Kenney | Packs mayoritariamente CC0 | Verificar pack a pack |
| Poly Haven | CC0 | Sin verificar por mí |
| OpenGameArt, Sketchfab | Varía por recurso | Verificar uno a uno |
| Restaurant for Monsters | MIT (código y recursos) | Verificado en la auditoría anterior |
| Restaurant Game Canvas JS | MIT en código; imágenes y sonidos de terceros | Verificado; no se copian recursos |
| MiniBistro, RecipeRush, OpenKitchen | Licencias mixtas o no claras | No se usan |

Las hojas de personajes Island Crew (Chef Goat, Dog Cook, Golden Dog, Bird Chef) son material propio y son la referencia visual para los cocineros del equipo.

## Servicio de varias comandas (16-10-2026)
Jugable: «Servicio de ocho comandas» (misión servicio-ocho, cocinero de partida) y un calentamiento de tres. Las comandas llegan escalonadas, cada una con plazo, prioridad y alergia; se atienden en paralelo (Q/E o panel). Es una versión reducida, no 30 comandas. Pendiente: misión «devolucion-coccion», que mantiene bloqueado el ascenso a cocinero de partida.

## Academia Virtual (16-10-2026)
Ruta /mundo/academia. Jugable: 3 lecciones de diálogo en inglés (atender una mesa, alergia, reclamación) con respuestas explicadas, reintentos que restan, omitir, voz del navegador (speechSynthesis) y tarjetas de vocabulario con cajas de repaso. Cada lección es una misión de camarero (academia-ingles-*) que deja evidencia en Mi carrera; una respuesta crítica anula la nota. Escenas procedurales propias (mar con isla y restaurante), sin modelos de terceros. Cocina: panel de pasos y ficha de ingrediente. Pendiente: personajes y animaciones definitivas con licencia verificada, voces propias, lecciones de cocina y bar, y conexión documentada con Academy y Talent (no existe todavía).

## Cocinero de partida (16-10-2026)
Jugables: «Calentamiento de tres comandas» (servicio-tres), «Servicio de ocho comandas» (servicio-ocho) y «Devolución por cocción» (devolucion-coccion). Con ellos, más 3 platos distintos y las habilidades requeridas, se asciende de ayudante a cocinero de partida (probado en tests). La devolución es un guion de la misión: el cliente devuelve la hamburguesa; hay que avisar (tecla C, máx. 20 s para nota completa) y rehacerla a tiempo. La nota de coordinación del pase se deriva de las entregas a tiempo con varias comandas abiertas; la de alérgenos, de servir las comandas con alergia (el motor bloquea platos que contienen el alérgeno). Pendiente: cocinero especializado en adelante (misión «especialidad-evaluacion»).

## Cocinero especializado (16-10-2026)
8 partidas (carnes, pescados, arroces, pastas, guisos, postres, panadería, cocina canaria) × 3 servicios generados desde los datos del recetario: técnica, servicio y evaluación (misiones especialidad-tecnica/-servicio/-evaluacion). El ascenso exige las tres misiones, especialidad:3 y emplatado:3. La nota de especialidad es la media de los platos; la de emplatado, los aciertos/errores de las fases de emplatar. Limitaciones conocidas: no se exige repetir la MISMA partida en las tres misiones, y se retiró la habilidad «salsas» del requisito hasta tener platos de salsa medibles. Recetas sin validar por un chef.

## Segundo de cocina: reparto de tareas (16-10-2026)

Ruta `/mundo/mando` (pizarra 2D, sin escena 3D). Motor en `src/lib/kitchen/reparto.ts`: equipo de cuatro NPC (perfiles de datos, no personas reales), diez tareas con prioridad, plazo y dependencias, e incidentes (ausencia, avería). Misiones jugables: `reparto-turno`, `reorganizar-ausencia`, `formar-companero`. El requisito de sous-chef pasa a pedir esas tres misiones y las habilidades liderazgo:3, planificacion_produccion:3, formacion:2, resolucion_problemas:3. La nota sale de lo ocurrido (plazos, adecuación y equilibrio de carga, mentor en tareas formativas, reacción y aviso al chef). Una tarea de prioridad 3 sin hacer anula la evidencia. Pendiente: jefe de cocina (`carta-rentable`) y chef ejecutivo; escena 3D y revisión por un jefe de cocina real; los tiempos y competencias son datos de ejemplo sin validar.

## Jefe de cocina: carta rentable (16-10-2026)

Ruta `/mundo/carta`, motor en `src/lib/kitchen/carta.ts`. Misión jugable `carta-rentable` (diseno_carta, escandallos, mermas): seis platos (2 entrantes, 3 principales con uno vegetariano, 1 postre), coste por ración con merma, aprovechamiento de recortes (−40 % de merma a cambio de mano de obra) y precio con IVA. La nota de escandallos mide el error de tu cálculo; vender por debajo del coste anula la evidencia. Pendiente: chef ejecutivo (`estandar-multisede`); precios y mermas son datos de ejemplo sin validar, y solo hay una carta.

## Chef ejecutivo: estándar multisede (16-10-2026)

Ruta `/mundo/multisede`, motor en `src/lib/kitchen/multisede.ts`. Misión jugable `estandar-multisede` (analisis_datos, liderazgo, presupuesto): cuatro locales con cinco indicadores, diagnóstico del problema principal y reparto de 9000 € en cinco acciones (cada una corrige un indicador un 80 % de su desviación). Pasarse de presupuesto anula la evidencia. Con esto toda la rama de cocina es jugable de punta a punta. Pendiente: las cifras son ficticias y sin revisar por un profesional; solo hay un escenario; las demás ramas (sala, barra, hotel…) siguen como datos.

## Sala: camarero y camarero sénior (16-10-2026)

Ruta `/mundo/sala`, motor en `src/lib/kitchen/sala.ts`. Misiones jugables `sala-servicio-normal` (4 mesas, una con alergia) y `sala-alta-demanda` (6 mesas y una reclamación). Un único camarero, acciones con duración (saludar, preguntar alergias, comanda, servir, cobrar, reclamación); las mesas se pierden si esperan demasiado. Tomar la comanda de una mesa con alergia sin preguntar anula la evidencia. Cambio documentado: se quita `formacion:2` del requisito de camarero sénior porque aún no existe una misión de sala que la mida (se recuperará con una misión de formar a un camarero nuevo). Pendiente: jefe de sala (`sala-grupo`) y director de restaurante (`restaurante-mes`); tiempos de ejemplo sin validar por un maître.

## Jefe de sala: reserva de grupo (16-10-2026)

Ruta `/mundo/grupo`, motor en `src/lib/kitchen/grupo.ts`. Misión jugable `sala-grupo` (reservas, coordinacion_pase, liderazgo): un grupo de 12 sobre un aforo de 36, siete solicitudes de reserva, alérgenos que hay que comunicar a cocina, tres cursos con minuto de salida contra una carga de cocina por franjas, y reparto de cuatro camareros en tres zonas. La sobreventa o no avisar de un alérgeno grave anula la evidencia. Pendiente: director de restaurante (`restaurante-mes`); datos de ejemplo sin validar por un maître.

## Resto de ramas: casos de gestión (16-10-2026)

Ruta `/mundo/casos`, motores genéricos en `src/lib/kitchen/casos.ts` y escenarios como datos en `src/lib/kitchen/casos-datos.ts`. Tres tipos de ejercicio: turno con prioridades y dependencias, presupuesto con diagnóstico (se compara con el óptimo calculado por fuerza bruta) y decisiones con consecuencias (con opciones críticas que anulan la evidencia). Cubren las 21 misiones que quedaban pendientes: barra (3), recepción (3), pisos (3), economato (3), mantenimiento (2), eventos (2), dirección (4) y restaurante-mes. Ya no queda ninguna misión «aún no disponible».

Cambio documentado y honesto: cada misión tiene un solo caso, y el motor de carrera exige misiones distintas para subir de nivel de habilidad, así que se rebajaron los requisitos de habilidad de 21 puestos al nivel que hoy se puede evidenciar (por lo general «Inicial») y se quitaron las habilidades que ninguna misión mide. Se irán subiendo al añadir más casos por puesto. Pendiente: varios casos por puesto, escenas 3D, y revisión de todo el contenido por profesionales de cada oficio.

## Realismo gráfico (auditoría, octubre 2026)
Motor actual: three.js 0.169 en el navegador (Next.js). No se migra a Unreal/Unity sin prueba de viabilidad: perderíamos la web, las cuentas y la carrera.
Hecho en la cocina: reflejos de entorno PMREM, sombras suaves, modelos CC0 de Kenney. Pendiente (necesita medir y probar): texturas PBR CC0 de Poly Haven, personajes con animación de manos, vapor/cocción visual, fotogrametría propia de Corralejo. Un cliente Unreal independiente sería un proyecto aparte.
