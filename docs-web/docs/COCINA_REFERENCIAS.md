# Simulador de cocina · referencias estudiadas

Comprobado el 16-10-2026 clonando cada repositorio y leyendo su estructura y código clave. **No se ha copiado código ni recursos de ninguno.** Island Crew World es web (TypeScript + three.js): los motores Godot y Unity no son reutilizables, y varios repositorios no declaran licencia (sin licencia, copiar no está permitido).

| Proyecto | Licencia | Último cambio | Qué aporta | Qué adoptamos (reescrito) |
|---|---|---|---|---|
| Restaurant for Monsters | MIT | 2026-08 | Recetas en `data/recipes.json` con fases (`prep`), `heat`, `heat_tolerance`, `time`, `time_tolerance`, dificultad. Sistema de cocción con señales por fase y puntuación por fase. Suite de tests de contenido (cada receta e ingrediente existe). Guardado con prueba de corrupción. | Receta = datos, motor genérico (ya hecho). Próximo: temperatura objetivo con tolerancia además de la ventana de tiempo. Tests de integridad (ya hechos). Prueba de guardado corrupto cuando haya persistencia. |
| OpenKitchen | no declarada | 2026-09 | Escandallo recursivo (recetas dentro de recetas), todo en céntimos, protección contra ciclos, `food_cost_pct` frente a objetivo, margen. | Coste por receta y margen en céntimos; sub-recetas (salsas, mojo) como ingredientes; alerta si supera el coste objetivo. Pendiente en fase de economato. |
| Cozy Bistro | **propietaria (todos los derechos reservados)** | 2026-08 | Economato, personal, compras, reputación, guía de balance. | Solo ideas generales de diseño (stock mínimo, compras, reputación). No se reutiliza nada de su código, textos ni arte. |
| Culinary Comrades | no declarada | 2025-03 | Prototipo muy pequeño (controlador FPS de 70 líneas, ítems recogibles). | Ítems "recogibles" con datos propios; sin código. Nuestro movimiento en primera persona ya existe en el mundo. |
| CAFECAFE | no declarada | 2025-04 | Prototipo: movimiento, ingredientes, aparatos de cocina interactivos, tienda. | Idea de aparatos con estados; sin código. |
| RecipeRush | no declarada | 2026-07 | Cocina cenital con ayudante de IA entrenado por refuerzo. | Descartado el aprendizaje por refuerzo. El ayudante será por reglas: lee la fase actual y señala el siguiente paso, sin actuar por el jugador. |
| CULLinary | no declarada | 2021-07 | Inventario y recetas en Unity, proyecto de 300 MB. | Sin aportación técnica útil para la web. |
| Restaurant Game Canvas JS | MIT | 2024-12 | Pedidos y márgenes muy simples. | Nada que no tengamos ya. |
| Restorant | el enlace no existe (404) | — | — | Sin revisar. |

## Decisiones

1. Seguimos con motor propio en TypeScript y datos; los 100 platos serán datos validados por tests, no código.
2. Nada de estos repositorios entra en el producto. Si algún día se reutiliza algo MIT, se anotará aquí con su aviso de licencia.
3. Todas las recetas siguen `validada: false` hasta que un chef las revise.
