# Auditoría técnica visual · Island Crew Virtual Office (2026-11-02)

Estado de cada punto: IMPLEMENTADO / PROBADO LOCALMENTE (render de prueba, no en tu escena real) / PARCIAL / PENDIENTE.

## Qué existe
- Motor: three.js directo en `src/components/Oficina3D.tsx` (no React Three Fiber; no se migra, se mejora). Etiquetas CSS2D, picking por Raycaster, calidad adaptativa por escalones (`tier`), sombras que se recalculan cada pocos fotogramas.
- Cabras: 85 desde un único registro (`TODOS`). Cabra 3D propia (`cabra3d.ts`, 2 mallas por cabra, geometría compartida). Fotos 2D disponibles con `?cabra2d`.
- Entorno: océano con shader, nubes, ciclo día/noche, mobiliario de estudios con analizadores que solo reaccionan a eventos reales.
- Modelos GLB: pocos (silla, lámpara, jarra…), licencias en `public/models/LICENCIAS.md`.

## Hecho en este tramo
- **Diosa Cabra 3D** (`diosa.ts`): modelo procedural propio, no una imagen. Cuernos con anillos dorados, ojos dorados, barba, orejas, capa azul con ribete dorado, medallón, halo. Respira, parpadea, mueve orejas y barba y su cabeza sigue a la cámara; con eventos reales activos, ojos y halo brillan más. PROBADO LOCALMENTE (render). Calidad: estilizada, NO fotorrealista.
- **Modo ligero**: automático en táctil/pantalla estrecha, botón «⚡ Modo ligero» (se recuerda), `?calidad=baja|alta` lo fuerza. Océano 64×64 en vez de 200×200, la mitad de nubes, resolución 1, sin reflejos. IMPLEMENTADO; no medido en dispositivos reales.
- **Iluminación**: mapeo de tonos neutro, reflejos suaves (RoomEnvironment, sin descargas) y suelo mínimo de luz ambiente por la noche. IMPLEMENTADO; no visto en la escena real.
- **Pelaje**: textura procedural de pelo (mapa + relieve) en las cabras y en la Diosa.

## Pendiente (no hecho)
- Diosa fotorrealista: requiere un modelo GLB modelado/generado (Blender, Meshy/Tripo/Hunyuan3D) y revisión humana. Evaluar planes gratuitos y licencia comercial antes de usarlos; ninguna herramienta de pago es obligatoria.
- Materiales PBR con mapas reales (Poly Haven/ambientCG, CC0), animaciones Mixamo, post-proceso (bloom, AO), WebGPU opcional, LOD, KTX2/Draco con glTF Transform, regresión visual con capturas.
- Departamentos con arquitectura propia (solo música, mastering y YouTube tienen interior).
- Medir rendimiento real (60 FPS no está demostrado).
