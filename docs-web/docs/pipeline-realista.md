# Pipeline de Corralejo realista (OSM → procedural → juego)

Estado a 2026-10-07. Reutiliza lo existente: `docs/unreal-fps-master-prompt.md`, `docs/brief-artista-3d-unreal.md`, `docs/art-direction-world.md`, `src/lib/geo.ts`, `src/lib/businesses.ts`.

## Decisión de motor
El juego vive HOY en la web (three.js). Motivo: es gratis, se despliega con cada push y ya tiene multijugador/cuentas. Unreal Engine 5 (Nanite, Lumen, World Partition, PCG) queda como destino futuro: los datos están separados para poder exportarlos (ver abajo). No se afirma que haya UE5 hoy.

## Dos capas (no mezclar)
- REAL_MAP_DATA: `public/data/corralejo-osm.raw.json` (OpenStreetMap, ODbL, atribución obligatoria) y `fuerteventura-coast.json`. Solo geometría y POIs.
- GAME_WORLD_DATA: `corralejo-businesses.json` (negocios ficticios), NPC, misiones, economía, multijugador. Nada de aquí se presenta como real.

## Prohibido
Street View / imágenes de Google como textura, scraping, assets sin licencia clara. Solo datos abiertos, procedural, CC0 o propios.

## Hecho (vertical slice web)
- `geo.ts`: OSM → calles, edificios, costa, POIs, índice por celdas (World-Partition-lite).
- `canary.ts` (nuevo): zonas (CENTER/RESIDENTIAL/TOURIST/COAST) y estilo de edificio determinista por SEED+id+zona+tipo; paleta corta dominada por cal blanca, contraventanas azul/verde/madera, desgaste 0–0,35.
- Render: fachadas con ventanas instanciadas (8.500 aprox. en 330 m), contraventanas, toldos de negocio, aires acondicionados, ventanas encendidas de noche, farolas, estrellas, sol real, palmeras.
- Negocios ficticios anclados donde OSM marca locales reales (sin usar su nombre).
- Multijugador básico (presencia, gestos, frases rápidas), NPC a pie/skate/patinete, patinetes cogibles.

## No hecho todavía (honesto)
Interiores, vehículos, tráfico, audio, vegetación canaria diferenciada (cactus/tabaiba), aceras/bordillos/pasos de cebra, texturas PBR y normal maps, LOD/HLOD reales, zona PORT/BEACH, exportación a Unreal, scripts Blender, QA automático.

## Proveedores (abstracción para no acoplarse)
Contrato previsto: MapProvider, GISProvider, BuildingProvider, TerrainProvider, VegetationProvider, AssetProvider. Hoy: OpenStreetMap + procedural. Mapbox/HERE/Google se podrán añadir como otra implementación sin tocar el juego.

## Camino a Unreal (cuando toque)
1. `scripts/import-osm-corralejo.mjs` → raw OSM. 2. Exportar GeoJSON + `Style` por edificio (de `canary.ts`). 3. Blender (Python): extrusión + LOD. 4. UE5: World Partition por celdas de 100 m, PCG para vegetación, Nanite para fachadas. El WORLD_SEED garantiza la misma generación en todos los servidores.

## QA /AUDIT_CANARY_VISUAL_STYLE (manual por ahora)
¿Parece Canarias? ¿Demasiados edificios iguales? ¿Escala humana correcta? ¿Zonas vacías? ¿Mundo vivo? Registrar capturas día/noche y puntuar 1–5.

## Asset Registry
Ver `public/data/asset-registry.json`. Hoy todo es procedural propio (sin licencias externas).
