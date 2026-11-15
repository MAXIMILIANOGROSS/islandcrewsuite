# Island Crew World · inventario de recursos y prioridades

## Auditoría (verificada en el código)
- Motor: **Three.js** (WebGL en navegador), render propio en `RealTownWorld.tsx`. Terreno y calles salen de datos reales de OpenStreetMap; materiales procedurales (shader `finish`), no PBR con mapas.
- Formatos: glTF/GLB para modelos, FBX para coches, JPG/WebP para texturas.
- **No migrar a Godot**: no aporta nada que Three.js no tenga ya aquí. De Godot solo sirven los *recursos* y las ideas de diseño.
- Límite real hoy: el plan gratuito de Vercel (10 GB de almacenamiento de despliegues). Todo recurso nuevo en `public/` se copia en cada despliegue → los recursos grandes deben ir a almacenamiento externo (Supabase Storage) o comprimirse.

## Licencias
| Recurso | Estado |
|---|---|
| Quaternius (Downtown City MegaKit, Standard) | CC0, ya usado y acreditado en /creditos |
| glTF-Transform | MIT (verificado en su repositorio) |
| Kokoro, XTTS, Piper | ver docs/ai-ecosystem/COMPATIBILITY_MATRIX.md |
| Poly Haven, ambientCG, Kenney, Poly Pizza, OpenGameArt, Freesound, Sonniss, Mixamo | **SIN VERIFICAR aquí.** Comprobar la licencia de cada archivo antes de incluirlo; Freesound y Mixamo varían por autor/condiciones |
| Godot Open World, Terrain3D, Proton Scatter, Material Maker | Solo referencia (son para Godot) |

## Prioridad (impacto visual · jugabilidad · coste · dificultad)
1. Estilo Downtown en todo Corralejo — **hecho** (edificios completos cerca, modulares lejos, aceras y asfalto con textura). Falta verlo en producción.
2. Liberar espacio en Vercel — vídeos recomprimidos (-25 MB/despliegue). Siguiente: mover GLB grandes a almacenamiento externo.
3. Materiales y HDRI de Corralejo (arena volcánica, roca oscura, fachadas blancas): alto impacto, coste bajo, **tras verificar licencia** y con texturas ≤1024 px en WebP.
4. Océano/barcos/pesca/buceo/Lobos: hay mecánicas parciales; no existe un paquete listo, se construye encima de Three.js.
5. Audio ambiental por capas: base ya existente (`public/world/sfx`); ampliar con licencias verificadas.
6. Optimización (LOD, meshopt/KTX2): medido con glTF-Transform sobre los edificios del kit: solo -29 % (8,3 → 5,9 MB) sin meshopt; no compensa el riesgo ahora.

## Regla
Un recurso entra solo si: licencia verificada, registrada en /creditos, tamaño razonable y probado en el juego real.
