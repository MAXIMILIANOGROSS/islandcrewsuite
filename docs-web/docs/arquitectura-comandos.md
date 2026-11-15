# Island Crew World — estado, arquitectura, auditoría y hoja de ruta
(Resultado de /PROJECT_STATUS, /ARCHITECTURE, /AUDIT_GAME y /ROADMAP. Prototipo web, no probado aún en navegador real ni con carga.)

## Arquitectura (lo que existe)
- PLAYER: gameprog (xp, dinero, flags, stats), career (experiencia, habilidades, ruta), CV. Guardado local + nube (`ic_game_save`, servidor autoritativo: xp/dinero no bajan, tope por guardado).
- WORLD: Corralejo procedural en primera persona, hora, descubrimientos globales (SQL 31), minimapa y mapa de Fuerteventura (solo Corralejo jugable).
- NPC: Marta, recepcionista, vecinos con texto canario (canario.ts), rumores e historias (stories.ts).
- BUSINESS/JOB: vacantes reales (`world_vacancies`) como EMPRESA_PARTICIPANTE; ofertas de juego G1–G6; carteles «SE BUSCA PERSONAL» en el mundo cuando hay oferta real.
- QUEST: Q001–Q012, ofertas urgentes, historias.
- INTERVIEW: entrevistas simuladas (interview.ts), presencial/online, resultado con XP de juego, una vez por oferta.
- SOCIAL/MULTIPLAYER: presencia y emotes por Realtime (`?multi=1`), amigos/bloqueo/reporte (SQL 32). Chat libre y voz BLOQUEADOS hasta moderación y revisión legal.
- ECONOMY: dinero de juego, sin pagos reales ni comercio entre jugadores aún.
- SECURITY: RLS + RPC SECURITY DEFINER; privacidad por diseño (sin documentos, sin edad exacta, nada «verificado»).
- ADMIN/AUDIO/AI: sin panel admin; audio WebAudio básico; sin IA generativa en NPC (reglas fijas).

## Auditoría
CRITICAL: ninguno conocido, pero NADA se ha probado con navegador real ni varios jugadores a la vez.
HIGH: SQL 29/31/32 sin confirmar ejecutados; sin test multijugador ni de carga (no se asume ninguna escala); el cliente guarda progreso local que el servidor solo limita, no valida turno a turno (xp/dinero de juego manipulables dentro del tope: aceptable mientras no tengan valor real).
MEDIUM: sin panel de empleadores ni verificación de empresas; compartir CV solo tiene ajuste de visibilidad; sin viaje a otras localidades; sin reputación profesional detallada.
LOW: cocina/recepción no jugables; sin cámara/álbum; sin eventos semanales.

## Legal (lista del abogado)
Declaraciones de edad y documentación, CV (RGPD), entrevistas reales vs simuladas, tratamiento de reportes, chat/voz, empleadores verificados, búsquedas de tesoro.

## Hoja de ruta (criterios)
PROTOTYPE (ahora): salida = flujo exploración→registro→formación→turno→CV→entrevista probado a mano en navegador.
VERTICAL SLICE: 1 zona pulida, 2+ jugadores reales estables, SQL aplicados, tests E2E.
ALPHA: reputación, árbol de carrera completo, panel empleador básico, moderación mínima.
BETA: chat con moderación y revisión legal, carga medida (20→1000 escalonado).
EARLY ACCESS / LIVE: nuevos destinos (Puerto del Rosario…) sin tocar el núcleo.

## Prioridad siguiente (/PRIORITIZE)
1) Probar en navegador y corregir. 2) Confirmar SQL. 3) Test multijugador de 2 pestañas. 4) Reputación profesional. 5) Panel empleador (tras revisión legal).

## /BUILD_REAL_CORRALEJO — pipeline (iniciado)
Geografía real, juego encima. Stack: web (three.js), no Unreal.
1. `scripts/import-osm-corralejo.mjs` descarga de OpenStreetMap (Overpass, ODbL) calles, edificios, costa y negocios → `public/data/corralejo-osm.raw.json`.
2. `src/lib/geo.ts` (probado): proyección a metros (origen = coordenada de la Playa de Corralejo según documentación municipal, SIN verificar por nosotros), `buildWorld`, simplificación, celdas de 100 m (equivalente ligero a World Partition) y colisión con edificios.
3. Pendiente: renderizar calles/edificios reales en `FirstPersonWorld`, minimapa con calles reales, anclar negocios y hotspots a edificios, NPC y horarios sobre la red de calles.
Atribución obligatoria en el juego: «© Colaboradores de OpenStreetMap (ODbL)».
Legal (lista del abogado): mostrar negocios reales (nombre) como ambiente; NUNCA como participantes ni con ofertas sin autorización; Google Maps/Places NO se usa (sus datos no se pueden copiar).

## /BUILD_CORRALEJO_230_BUSINESSES (iniciado)
- `src/lib/businesses.ts`: generador determinista de 230 negocios FICTICIOS (45 restaurantes, 30 bares, 25 cafés, 12 chiringuitos, 15 tapas, 10 fast food, 10 pizzerías, 12 hoteles, 10 alimentación, 12 tiendas, 12 surf, 10 turismo, 5 ocio nocturno, 7 servicios, 15 especiales) sobre edificios reales de OSM; hoteles en los edificios más grandes, chiringuitos junto a la costa. Horarios (incl. cruce de medianoche), dependencia del tiempo, puestos SIMULADOS, descubrimiento VISIBLE/DISCOVERABLE/SECRET/SPECIAL/LEGENDARY.
- `validateBusinesses` (/VALIDATE_BUSINESSES): 230 IDs únicos, edificios únicos y existentes, coordenadas válidas, sin flotar/atascar/en el agua, categorías exactas, ningún negocio presentado como real o participante, empleos solo simulados.
- Datos: `public/data/corralejo-businesses.json` (regenerar: `node --experimental-strip-types scripts/build-businesses.mts`).
- Niveles de detalle: 10 negocios completos (nivel 4) y 40 gameplay (nivel 3) cerca del origen, el resto 1–2. Interactivo hoy: consultar ficha y solicitar puesto simulado (nivel 3-4). Pendiente: interiores, NPC dentro, minijuegos por negocio, economía y eventos por negocio, multijugador dentro del negocio.
- Los nombres de negocios reales (OSM) NO se reutilizan para los ficticios; los reales siguen como carteles «ambiente».
