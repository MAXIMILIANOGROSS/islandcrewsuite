# Loop de mejora continua — Island Crew World

Cada ciclo: leer este archivo, elegir UNA tarea del backlog, implementarla pequeña, verificar, registrar. Nunca más de una tarea por ciclo.

## Reglas inquebrantables
1. Verificar antes de terminar: `npx tsc --noEmit` y `node --experimental-strip-types --test tests/*.test.mjs` deben pasar. Si fallan y no se arreglan en el ciclo, deshacer los cambios de ese ciclo (restaurar con git) y anotarlo.
2. NO activar chat libre ni voz. NO tocar el Legal & Privacy Launch Gate.
3. Sin datos inventados presentados como reales; negocios/NPC siempre ficticios y etiquetados. No usar nombres de negocios reales. No usar datos de Google. No scrapear.
4. No gamificar al usuario: el progreso del juego (`ic_game_v1`) está separado de XP/reputación/Island Points reales.
5. No borrar archivos, no tocar credenciales, no ejecutar SQL (solo escribir `supabase/TODO_CORRER_N.sql` nuevos y avisar).
6. No hacer `git push` ni deploy: el usuario sube. Cambios solo en el árbol local; si hay `git`, puede hacerse commit local NO, solo dejar los cambios.
7. Cambios pequeños y reversibles. No reescribir archivos grandes enteros; usar ediciones puntuales.
8. Todo lo legal/RGPD va a la lista del abogado en `docs/arquitectura-comandos.md`.
9. Responder al usuario en español; registrar cada ciclo en el Registro de abajo (fecha, tarea, resultado, qué debe probar el usuario).

## Backlog (orden de prioridad)
**REGLA DE REALISMO (aplica a todo: hype Y realista a la vez):** velocidades y distancias a escala real (peatón ~1,4 m/s, patinete ≤25 km/h como la norma española), sol y hora reales de Corralejo (cálculo astronómico), horarios de negocios según la hora real local, alturas de edificios reales de OSM, materiales PBR creíbles, proporciones humanas correctas, peatones que respetan aceras/pasos, sin objetos flotando ni atravesando paredes. Cualquier cosa decorativa debe parecer plausible en Fuerteventura (palmeras canarias, cal blanca, basalto, viento). Si algo es inventado, se etiqueta como juego.
R1. Sol real: posición solar por fecha/hora/lat-lng de Corralejo (función pura + tests), cielo y sombras acordes.
R2. Clima opcional real (viento/nubes de una fuente abierta sin clave, con fallback), sin inventar datos.
R3. Peatones en aceras (offset por lado de la calle), parar en cruces, ritmo de paso realista, animación de piernas/brazos.
R4. Fachadas realistas: ventanas, puertas, tejados planos con parapeto, texturas de cal/piedra, sombras suaves.
R5. Calles: marcas viales, aceras con bordillo, farolas y mobiliario urbano en los lugares donde OSM los tiene.
**PRIORIDAD HYPE (el juego debe sentirse espectacular; hacer una de estas antes que el resto cuando no haya trabajo de seguridad pendiente):**
H1. Sensación de velocidad: FOV dinámico (hecho al correr/patinete), líneas de viento, balanceo de cámara al caminar.
H2. Audio: olas, gaviotas, viento, música isleña suave, pasos y motor de patinete (WebAudio, sin archivos con copyright; silenciable).
H3. Atardecer/noche con farolas encendidas y negocios iluminados; cielo dorado a ciertas horas.
H4. Agua más viva (olas, espuma en la orilla), sombras suaves, polvo/partículas, mar con reflejos.
H5. Momentos wow: salto de patinete en rampas, emotes con partículas, fuegos artificiales en eventos, drones/cometas.
H6. Pantalla de inicio cinematográfica (vuelo de cámara sobre Corralejo) y transiciones fluidas.
H7. Mini-retos de movilidad (carreras de patinete por checkpoints reales de Corralejo) con marcador de juego, sin gamificar el progreso real.
H8. Fotos: modo foto con filtros y marco "Island Crew", para compartir.
1. Bloqueo y reporte de jugadores visibles en `/mundo/real` y `/mundo/jugar` (botón sobre el jugador).
2. Filtro de alias ofensivos (lista + tests) y pantalla admin de reportes.
3. Quitar `?multi=1` como requisito (multijugador por defecto con cartel de reglas), solo si 1 y 2 están hechos.
4. Interiores simples de los 10 negocios de nivel 4 (mostrador, encargado ficticio, tareas simuladas).
5. Economía simple por negocio (propinas/ventas del juego, moneda de juego separada de dinero real).
6. Ciclo día/noche y clima; horarios de negocios según hora.
7. Más variedad de NPC (rutas por la mañana/tarde, turistas con maleta, surfistas con tabla).
8. Fachadas con ventanas, puertas, toldos y tejados en los edificios.
9. Pantalla de Passport en `/cuenta/identidad` usando `src/lib/ecopassport.ts` (estados VERIFIED/SELF_DECLARED/GAME_EARNED/EMPLOYER_CONFIRMED).
10. Estados de empresa DISCOVERED→PARTNER y etiqueta REAL/SIMULADA en ofertas.
11. Viaje a otros pueblos de Fuerteventura (datos de OSM, scripts ya existentes).
12. Rendimiento: medir y reducir draw calls, instancing de edificios/NPC, carga perezosa.
13. Accesibilidad y móvil: controles táctiles en `/mundo/real`, textos legibles, teclado.
14. Más tests de lógica pura y limpieza de duplicados (`/mundo/jugar` vs `/mundo/real` → un solo mundo).
15. Eventos semanales de comunidad (calendario simple, sin chat libre).

## Registro de ciclos
(vacío)
