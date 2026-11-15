# Journeys, ramas, misiones y «¿Qué pasaría si…?»

Estado: diseño (P2). Se apoya en lo ya construido: `goals_catalog`, `goal_value`, `next_best_action`, `xp_events`.

## Modelo
```
Journey (work | home | crew | market)
  └─ JourneyNode (hecho verificable)           ← vista de hechos; no concede XP por sí mismo
       └─ JourneyBranch (camino posible, reversible)
```
Un usuario puede cambiar de rama; ninguna es permanente. El árbol («Island Life Tree») es una **visualización** de hechos reales (empleo, vivienda, Crew, Market), distinta para cada persona.

## Trayectorias profesionales (posibles, no garantías)
Se guardan como datos editables (`career_paths`), con aviso «posible trayectoria, no una promesa». Ejemplos: sala (camarero → camarero sénior → supervisor → gerente de restaurante), recepción (recepcionista → sénior → supervisor → responsable de front office), cocina (ayudante → cocinero → chef de partida → sous chef → jefe de cocina), surf (asistente → instructor → dirección de escuela). Las rutas son orientativas y deben validarse con profesionales del sector antes de publicarse.

## Misiones
Principales («Encuentra tu lugar») y secundarias (primer empleo, primera vivienda, Crew, primera venta/alquiler, temporada completa, un año). **Una misión es un objetivo ligado a un hecho real**; las recompensas salen del motor de XP existente. Prioridad del motor de acción: necesidad → relevancia → impacto → momento → esfuerzo; una sola acción visible.

## «¿Qué pasaría si…?»
Todo resultado se etiqueta con su tipo y nunca se presenta como hecho:
| Etiqueta | Significa |
|---|---|
| `REAL_DATA` | dato existente y verificado (p. ej. salario *declarado* de la oferta) |
| `ESTIMATE` | cálculo con supuestos visibles (p. ej. presupuesto conjunto de una Crew) |
| `SCENARIO` | simulación explícita («si te mudas a Lanzarote…») sin garantía |
Prohibido inventar tiempos de viaje, vacantes, salarios o disponibilidad; si no hay dato: «sin datos».

## Pasaporte y traslado entre islas (P4)
Misma cuenta, XP, reputación y badges; nuevo contexto local (búsqueda, perfil de zona, pasaporte). No es una competición ni un ranking.
