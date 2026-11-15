# Personajes 3D realistas (Island Crew Show)
El plató carga `/models/personajes/<id>.glb` si existe; si no, usa la cabra procedural. Ids: `capra`, `brisa`, `noticiasf`, `noticiasm`, `tiempo`, `invitado`.
Requisitos del `.glb`: personaje de pie o sentado mirando a +Z, altura libre (se escala a ~1,5 m), y un **morph target** llamado `jawOpen` o `mouthOpen` en la malla de la cara (la boca se abre con el micrófono o la voz).
Flujo recomendado: arte original del personaje → imagen a 3D (comprobar licencia comercial del modelo) → limpiar y rigear en Blender → exportar glTF binario → copiar a `public/models/personajes/`.
Estado: cargador IMPLEMENTED y sin modelos reales todavía (los .glb los tiene que aportar la Dirección). Los modelos hay que tener derechos para usarlos.
