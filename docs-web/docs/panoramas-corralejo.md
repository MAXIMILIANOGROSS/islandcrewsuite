# Recorrido en fotos 360° de Corralejo

El visor está en `/mundo/panorama`. Muestra fotos reales; no inventa nada. Con `PANO_NODES` vacío dice "Todavía no hay fotos publicadas".

## Cómo hacer las fotos
1. Cámara 360° (o modo panorámico del móvil, aunque cose peor). Altura de ojos, 1,6–1,7 m. Luz de tarde, calle poco concurrida.
2. Una foto cada 10–15 m a lo largo del paseo. Anota el orden.
3. Exporta como JPG equirectangular (relación 2:1). Redimensiona a 4096×2048 y comprime a menos de 3 MB.
4. **Difumina caras y matrículas** antes de subir. Si sale el rótulo o la fachada de un negocio, necesitas su consentimiento por escrito (hoja del kit de negocios). Los derechos sobre fachadas y marcas van a la lista para el abogado.
5. No uses fotos de Google Street View ni de terceros sin licencia.

## Cómo registrarlas
1. Copia cada foto a `public/world/pano/<id>.jpg`.
2. Añade el nodo en `src/lib/panoData.ts`:
```ts
{ id: "paseo-1", title: "Paseo marítimo · 1", image: "/world/pano/paseo-1.jpg", northYaw: 0,
  links: [{ to: "paseo-2", yaw: 90, pitch: -5, label: "Seguir por el paseo" }],
  spots: [{ hotspotId: "<id del punto en /admin/world>", yaw: 20, pitch: 3, label: "Restaurante" }] }
```
- `yaw`: grados desde el centro horizontal de la imagen, positivos hacia la derecha. `pitch`: 0 = horizonte, positivo hacia arriba.
- `northYaw`: el yaw donde está el norte en la foto (para la brújula). Si no lo sabes, deja 0 y la brújula no será fiable: quítala o mídelo con una brújula.
- `hotspotId`: id del punto real en `/admin/world`. Solo se muestra si el punto está activo y con fuente aprobada.
3. Las vacantes que salen son las reales de ese negocio. Sin vacantes, el panel lo dice.

## Lo que NO hace
No hay personajes ni entrevista en este visor: es solo el mundo real y sus puntos.
