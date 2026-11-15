# Island Crew World — Master Art Direction Prompt

Regla absoluta del proyecto:
"If it looks like a videogame world, it is not realistic enough. If it looks like a real place that happens to be playable, we got it right."

> Este documento es la referencia visual objetivo (Unreal 5 / imágenes de moodboard). El prototipo web (three.js, `/mundo/jugar`) NO alcanza este nivel y no pretende hacerlo. Ver `art-direction-world.md` para opciones realistas y `unreal-fps-master-prompt.md` para el plan técnico.

## Notas de proyecto (no forman parte del prompt)
- Los negocios y encargados que aparezcan deben ser reales solo con consentimiento firmado; si no, ficticios y marcados como tales. Personajes nunca parecidos a una persona real sin permiso.
- Fachadas, rótulos y caras reales: derechos de imagen y marca, a revisar por abogado.
- Imágenes generadas con IA: solo moodboard interno, no publicarlas como el juego ni con negocios que parezcan reales.
- El progreso lo concede el backend por acciones reales verificadas, no por pasear. XP ≠ reputación ≠ puntos.
- Siempre debe existir la alternativa no 3D (lista y mapa en `/mundo`).

## 01 Realismo
Prioridad absoluta: fotorrealismo, calidad AAA en Unreal Engine 5. PBR, iluminación y reflejos físicos, oclusión ambiental, vidrio, vegetación, piel, pelo, ropa y arquitectura creíbles, escala física correcta. Evitar: low-poly, estilizado, cartoon, juguete, aspecto móvil, entorno genérico de IA, demasiado limpio. Incluir imperfecciones: pavimento gastado, suciedad, paredes desgastadas, pintura descolorida, cables, carteles, manchas, objetos dejados por la gente.

## 02 Diseño del mundo
Lugares reales con identidad geográfica. Corralejo, Fuerteventura: arquitectura canaria blanca de poca altura, materiales volcánicos, piedra clara, paisaje atlántico seco, palmeras, paseos marítimos, cafés, restaurantes, tiendas, surf shops, terrazas, vistas al océano, montañas volcánicas al fondo, sol atlántico fuerte, clima cálido y seco, agua turquesa. No convertirlo en una isla tropical genérica: identidad por arquitectura + vegetación + geografía + luz + atmósfera + detalles urbanos.

## 03 Iluminación
Luz natural cinematográfica: sol cálido, cielo brillante, dispersión atmosférica azul, sombras fuertes de borde suave, rebote sutil, edificios blancos, pavimento cálido, océano azul, distancia ligeramente polvorienta. Evitar filtros naranjas, HDR excesivo, neón, color grading artificial, cielos sobresaturados, god rays irreales.

## 04 Cámara
Siempre primera persona, altura de ojos 1,65–1,80 m, FOV horizontal 70–85°, movimiento de cabeza y de caminar sutil, inercia realista, profundidad de campo muy contenida. Permitido: manos, antebrazos, parte inferior del cuerpo muy sutil, animaciones de interacción. Evitar ojo de pez, look GoPro, cámara flotante o de dron, tercera persona.

## 05 Presencia del jugador
Manos y antebrazos realistas, bien escalados y conectados. Nunca manos flotantes, dedos deformes, manos gigantes o de dibujo.

## 06–07 NPCs
Seres humanos realistas, no NPCs de videojuego: rostro, cuerpo, peinado, ropa, postura y gestos únicos. Viven su vida (idle, caminar, conversar, rutinas de trabajo, reacciones al entorno) con independencia del jugador. Ejemplos: encargado en la puerta con tablet, turistas con fotos y bolsas, trabajadores sirviendo o descargando. Mundo poblado sin agobio.

## 08 Negocios
Cada negocio parece real y operativo: exterior reconocible, entrada, rótulo, interior, empleados, clientes, mobiliario, cartas, productos, luz, atmósfera e identidad. Nada de prefabs idénticos: individualidad arquitectónica + de marca + actividad humana.

## 09 Bucle de juego
Caminar → descubrir → acercarse → interactuar → hablar → descubrir oportunidad → decidir → progresar. Sin convertir el mundo en una interfaz gigante.

## 10 Interacción
Prompt mínimo: "[ E ] HABLAR" o "[ E ] INTERACTUAR". Pequeño, cerca del centro, con transparencia sutil, integrado, desaparece al alejarse.

## 11 Oportunidades
"★ 1 OPORTUNIDAD", "VACANTE DISPONIBLE", "NUEVA OPORTUNIDAD", "3 OPORTUNIDADES CERCA". Sensación de HUD AAA premium, nunca dominan el entorno. (En la web: el contador sale de vacantes reales abiertas.)

## 12 HUD
Mínimo. Arriba izquierda: Corralejo / Fuerteventura · Islas Canarias. Arriba derecha: ★ N OPORTUNIDAD. Centro: mira pequeña. Interacción: [ E ] HABLAR. Abajo: indicadores mínimos. Abajo derecha: brújula sutil. Evitar minimapas gigantes, registros de misiones, inventarios, UI de MMORPG, iconos excesivos, etiquetas flotantes.

## 13 Navegación
Física: brújula, waypoint, marcador de distancia, marcador de oportunidad (ej. "● Restaurante · 8 m"). Fomentar mirar alrededor en vez de seguir flechas GPS.

## 14 Narrativa ambiental
Restaurante: personal preparando mesas, clientes, cartas, repartos, cocina. Hotel: recepción, equipaje, huéspedes, limpieza. Playa: surfistas, turistas, socorristas, vendedores. Calle: peatones, scooters, bicicletas, coches, tiendas, repartos, vecinos.

## 15 Materiales
Hormigón con rugosidad, manchas y grietas. Piedra con variación natural. Madera con veta y desgaste. Vidrio con reflejos reales. Metal con arañazos. Tela con trama. Piel con subsurface scattering e imperfecciones. Vegetación con variación natural.

## 16 Vegetación
Propia de Canarias: palmeras, buganvillas, agaves, hierbas secas, plantas subtropicales, vegetación costera. Variación, viento, hojas imperfectas, sombras reales. Nunca "paraíso tropical" genérico.

## 17 Clima
Por defecto: día atlántico brillante. Soportar mañana, tarde, atardecer, nublado, viento, lluvia ocasional.

## 18–19 Escala y exploración
Calles, alturas, distancias y escala peatonal realistas, horizonte oceánico creíble, líneas de visión largas. Composición abierta: se ve de dónde vienes, adónde puedes ir, negocios, gente, calles, hitos. Un momento de juego, no un póster de marketing.

## 20 Narrativa visual
Cada captura responde a una pregunta: ¿dónde estoy? (Corralejo) ¿qué puedo hacer? (hablar con el encargado) ¿qué descubrí? (una oportunidad) ¿adónde sigo? (calle adelante) ¿por qué explorar? (negocios y oportunidades por todas partes).

## 21 Paleta
Primarios: blanco cálido, piedra caliza, arena, gris volcánico, madera natural, azul océano, azul cielo, verde palmera. Acento: amarillo/dorado cálido sutil para oportunidades. Evitar neón, saturación excesiva, morado ciberpunk, colores de fantasía o de dibujo.

## 22–23 Cinematografía y regla de captura
Calidad cinematográfica pero jugable: exposición realista, contraste natural, perspectiva atmosférica, reflejos y sombras naturales. Cada imagen debe parecer un fotograma de juego en primera persona. Sin composición promocional, póster, concept art, tercera persona, vista aérea ni exhibición de personaje.

## 24–26 Conexión con la vida real y emoción
Lugar real + gente real + negocio real + oportunidad real = Island Crew World. El jugador debe sentir: curiosidad, libertad, conexión, utilidad, progreso, optimismo. No lucha, no conquista, no salva el mundo: camina, habla, descubre, trabaja, construye relaciones, encuentra oportunidades, construye una vida.

## 27 Prompt maestro de escena (Corralejo)

Photorealistic AAA first-person gameplay screenshot from "Island Crew World", set in the real-world-inspired streets of Corralejo, Fuerteventura, Canary Islands, Spain. Adult eye-level FPS camera, realistic human scale, visible subtle player hands at the bottom of frame, immersive exploration gameplay. White low-rise Canarian architecture, volcanic stone, pale pavement, Atlantic coastal atmosphere, palm trees, subtropical vegetation, cafés, restaurants, local businesses, tourists and workers behaving naturally. Strong but physically accurate Atlantic daylight, realistic blue sky, ocean visible in the distance, natural shadows, PBR materials, high-resolution textures, realistic glass, wood, stone, concrete, skin and clothing, Unreal Engine 5 quality, physically based lighting, realistic global illumination, ambient occlusion, atmospheric perspective, subtle depth of field, cinematic but completely playable gameplay framing.

The player is approaching a real-looking local restaurant. A believable adult restaurant manager stands naturally near the entrance, looking toward the player and ready to interact. The restaurant has a terrace, tables, customers, staff activity, menus, plants, realistic signage and a visible interior. The environment contains small imperfections, weathering, natural clutter and authentic everyday details.

Minimal premium AAA HUD only: small central reticle, "[ E ] HABLAR" interaction prompt, subtle "1 OPORTUNIDAD" indicator, discreet location text "Corralejo · Fuerteventura, Islas Canarias", subtle distance marker and minimal compass. HUD must never dominate the scene.

The composition must feel like a real moment captured while playing an open-world first-person social exploration game. The player must feel free to continue walking down the street, enter other businesses, meet other people and discover new opportunities.

No third person, no character showcase, no poster, no concept art, no fantasy, no cyberpunk, no cartoon, no low-poly, no generic tropical island, no futuristic city, no combat, no weapons, no monsters, no exaggerated UI, no mobile-game aesthetic, no metaverse aesthetic.

Ultra-photorealistic, AAA production quality, believable human characters, realistic architecture, realistic environment, realistic lighting, premium Unreal Engine 5 visual quality, authentic Fuerteventura atmosphere, immersive first-person gameplay.

## Secuencia de imágenes coherente
calle → restaurante 1 → conversación → caminar → restaurante 2 → nueva oportunidad → hotel → tienda → playa → siguiente zona de Corralejo.
