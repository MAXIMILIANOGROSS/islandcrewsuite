# Brief para artista 3D / estudio de Unreal — Island Crew World

> Documento para pedir presupuestos. No incluye precios ni plazos: deben venir del estudio. Las imágenes de referencia son arte conceptual generado; **"La Ola", el encargado y las personas que aparecen no existen** y no deben copiarse como marcas ni rostros reales.

## 1. Qué es
Juego social de exploración en **primera persona** ambientado en Corralejo (Fuerteventura, Canarias). El jugador camina por una calle real, entra en un restaurante, habla con la encargada, hace una entrevista, trabaja un turno y vuelve a la calle. El backend (Island Crew) ya existe; el estudio no tiene que hacer servidores ni lógica de empleo real.

## 2. Alcance del primer encargo (vertical slice)
Un solo tramo, pero con calidad final:
- **Calle/paseo de ~150–250 m** de Corralejo: adoquín, fachadas blancas bajas con detalles azules, toldos, terrazas, palmeras, farolas, pizarras, bicis, mobiliario urbano, mar y montaña volcánica al fondo.
- **1 restaurante** con exterior, terraza e **interior navegable** (barra, cocina vista, mesas, iluminación cálida).
- **1 NPC principal** (encargada) realista con animaciones: idle, saludo, conversación, gestos, caminar. Más **8–12 NPC secundarios** (peatones, camarero, clientes) con variación de aspecto.
- **Luz**: ciclo día/noche, sol atlántico, viento visible en palmeras y toldos.
- **Audio**: capas de ambiente (mar, viento, gente, tráfico), interior del restaurante, pasos según superficie.
- **Primera persona**: cámara a 1,65–1,80 m, manos y antebrazos sutiles, movimiento humano natural.

Fuera del primer encargo: más calles, hoteles, tiendas, vehículos conducibles, multijugador, combate.

## 3. Referencia visual
Fotorrealismo tipo Unreal Engine 5: PBR, iluminación física, imperfecciones (desgaste, suciedad, asimetrías). **Prohibido:** cartoon, fantasía, ciberpunk, resort tropical genérico (debe sentirse canario/atlántico), interfaz exagerada. Paleta: blanco cálido, piedra caliza, arena, gris volcánico, madera natural, azul océano.

## 4. Interfaz (mínima, la implementamos nosotros o en UMG según acuerdo)
Arriba izquierda lugar; arriba derecha "★ N OPORTUNIDAD"; mira central; "[E] HABLAR"; distancia al negocio; brújula. Sin minimapas llenos ni misiones permanentes.

## 5. Lo que ya existe y debe respetarse
- Prototipo web jugable en `/mundo/jugar` con la lógica real: entrevista por fases con evaluación por factores, memoria del NPC, turno de trabajo, horarios, demanda del negocio, eventos, reloj. Los datos (diálogo, horarios, eventos) están definidos como datos y **se pueden exportar a JSON** para Unreal.
- Backend con negocios, vacantes y zonas en Supabase. Unreal consume una API; no guarda vacantes, usuarios ni XP.
- Reglas: ningún negocio real aparece sin consentimiento firmado; los personajes de demo son ficticios; sin IA generativa hablando como un negocio real hasta revisión legal.

## 6. Entregables
- Proyecto Unreal (versión estable indicada por el estudio) en un repositorio con Git LFS.
- Mapa de la calle y del restaurante con World Partition o estructura equivalente.
- Personajes con rigs y animaciones; materiales y texturas con licencias documentadas.
- `Docs/ASSETS.md`: origen, licencia y uso de **cada** asset (Fab/Megascans/MetaHuman u otros). Nada copiado de otros juegos ni de capturas de terceros.
- Informe de rendimiento y requisitos mínimos/recomendados (PC y, si procede, Mac con Apple Silicon).
- Código en C++/Blueprint limpio y comentado; interfaz de interacción genérica (no `if (actor == ...)`).

## 7. Condiciones que pedimos al estudio
- Pagos por hitos: blockout de calle → materiales y luz → interior → personajes → audio y pulido.
- Aprobación nuestra antes de cada hito; capturas y vídeo de cada entrega **en PIE (jugando)**, no solo renders.
- Cesión de derechos sobre todo lo creado y lista de licencias de terceros.
- Fotos de referencia: propias o con licencia. Nada de Street View. Si se usan fotos de Corralejo, caras y matrículas difuminadas.

## 8. Qué enviarnos en el presupuesto
Plazo estimado por hito, equipo (roles), motores y versión, riesgos que ven, qué necesitan de nosotros, hardware recomendado y portfolio de entornos exteriores y personajes realistas en Unreal.

## 9. Preguntas abiertas (a decidir nosotros)
- ¿Descarga para PC/Mac, o streaming desde la nube al navegador (coste de GPU por usuario)? El portal web seguiría igual en ambos casos.
- Licencias y condiciones de MetaHuman y de los assets de Fab para un producto comercial: confirmar en sus términos oficiales y con el abogado.
