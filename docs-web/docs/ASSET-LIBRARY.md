# Island Crew World · Biblioteca de assets libres

## Regla de entrada
Solo entra lo que sea **CC0 / dominio público / propio**. "Gratis para descargar" no basta.
Cada asset externo se registra en `public/data/asset-registry.json` ANTES de usarlo, con: `AssetID`, `Name`, `Category`, `Source`, `License`, `CommercialUse: true`, `SourceURL`, `LicenseURL`, `AcquiredAt` (AAAA-MM-DD) y `File`.
`npm test` falla si un registro incumple la política (`src/lib/assetPolicy.ts`). Guarda también una copia de la licencia junto al archivo.

## Fuentes aprobadas (comprobar la licencia del pack concreto en cada descarga)
| Necesidad | Fuente |
|---|---|
| Muebles, comida, ciudad, vehículos, naturaleza, náutica | Kenney (kenney.nl/assets) |
| Rocas volcánicas, materiales PBR, HDRIs, modelos | Poly Haven |
| Texturas y materiales (suelos, paredes, asfalto, arena) | ambientCG |
| Personajes, animales, vehículos, barcos animados | Quaternius |
| Props, personajes, edificios | KayKit (verificar el pack) |
| Objetos y personajes GLB | Gobkit |
| Árboles y vegetación | CC0Tree |
| Descubrimiento | CC0 Asset Index, Awesome CC0 |

## Estructura de carpetas (public/models/…)
01_buildings · 02_interiors · 03_furniture · 04_restaurants · 05_shops · 06_hotels · 07_beach · 08_port · 09_boats · 10_vehicles · 11_motorcycles · 12_bicycles · 13_fishing · 14_diving · 15_sports · 16_nature · 17_volcanic_rock · 18_palms · 19_roads · 20_signs · 21_tools · 22_food · 23_clothing · 24_npcs · 25_animations · 26_animals · 27_decoration · 28_lighting · 29_textures · 30_audio · 31_ui · 32_collectibles

## Prioridad para Corralejo
1. Rocas volcánicas y materiales de suelo (Poly Haven + ambientCG): sustituyen las rocas procedurales.
2. Barcos y puerto (Quaternius + Kenney).
3. Mobiliario de restaurantes (Kenney Furniture/Food).
4. Personajes/NPC con animaciones (Quaternius).
