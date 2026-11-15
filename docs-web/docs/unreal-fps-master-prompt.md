# Island Crew World — Unreal FPS Foundation (prompt maestro operativo)

> Para ejecutar en tu Mac con Claude Code dentro de la carpeta del proyecto Unreal. Nada de esto está probado: Claude Code debe compilar y probar en PIE cada paso antes de pasar al siguiente. Si algo no compila, se arregla antes de avanzar.

## Reglas
- Unreal Engine 5.x estable (versión exacta: la que instale Epic Games Launcher; **verificar en la documentación oficial que es compatible con tu macOS y tu chip**). C++ para sistemas, Blueprint para composición y ajuste.
- Backend = fuente de verdad (Supabase / API de Island Crew). Unreal no guarda vacantes, usuarios ni XP.
- Sin inventar datos: el NPC solo dice lo que devuelve la API. Si no hay dato: "No tengo esa información. Puedes preguntarle directamente al negocio."
- Los negocios aparecen solo si están verificados y con consentimiento (ya lo filtra la API `world_hotspots` / `world_vacancies`).
- Sin IA generativa hablando como un negocio hasta revisión legal. Diálogos de la primera versión: guion fijo + datos de vacantes.
- Cada dependencia o asset externo: licencia, origen y uso anotados en `Docs/ASSETS.md`. Nada de assets copiados de otros juegos.
- Accesibilidad: alternativa no 3D siempre (lista y mapa en la web). Subtítulos, sensibilidad de ratón, FOV y reducir movimiento configurables.
- No avanzar de fase hasta que la anterior funcione en PIE y esté documentada.

## Fase A — Proyecto y control de versiones
1. Crear proyecto C++ "IslandCrewWorld" (plantilla en primera persona, sin contenido de arranque innecesario).
2. `git init`, `.gitignore` oficial de Unreal, Git LFS para `*.uasset`, `*.umap`, `*.fbx`, `*.wav`, `*.png`, `*.psd`.
3. Estructura: `Source/IslandCrewWorld`, `Content/IC/{Characters,Maps,UI,Audio,Props}`, `Docs/`.
4. Resultado: abre en el editor y compila sin errores.

## Fase B — Controlador en primera persona
Clases C++: `AICPlayerCharacter`, `AICPlayerController`, `AICPlayerState`.
- Enhanced Input: IA_Move, IA_Look, IA_Jump, IA_Sprint, IA_Crouch, IA_Interact, IA_Menu. Teclado/ratón y mando.
- Caminar, correr, agacharse, saltar, gravedad, colisiones, pendientes/escaleras.
- Cámara en primera persona con FOV configurable y movimiento de cabeza muy sutil (desactivable).
- Pasos con sonido según superficie (placeholders con licencia clara).
- Validar: 60 fps estables en tu Mac en la zona de prueba.

## Fase C — Interacción
- Interfaz `IICInteractable` (CanInteract, GetPrompt, Interact).
- `UICInteractionComponent`: traza desde la cámara, muestra "[E] ..." en UMG.
- Implementadores: puerta, NPC de negocio, tablón de vivienda.
- Sin `if (Actor == ...)`: todo por la interfaz.

## Fase D — Calle de prueba (Corralejo prototipo)
- Una calle pequeña: restaurante, café, hotel, apartamento. Blockout primero, arte después.
- Iluminación diurna (luz solar + atmósfera). Mar y viento como ambiente.
- Referencia visual: tus fotos propias o con licencia. Nada de capturas de Street View o de terceros sin derechos.

## Fase E — NPC y negocio
- `AICBusinessNPC` con BusinessId, Role, DialogueId.
- `UICApiSubsystem` (GameInstance subsystem): llama por HTTPS a la API de Island Crew con el token del usuario (guardado fuera del código, nunca en el repo).
- Diálogo: saludo fijo, "¿Qué vacantes tenéis?" → lista real de vacantes; "Solicitar entrevista real" → crea la solicitud en el backend (el negocio decide).
- Si falla la red: mensaje claro y vuelta a la web.

## Fase F — Progreso real
- Al enviar una solicitud real, el backend (no Unreal) concede el progreso. Unreal solo muestra el resultado.
- Sin XP por pasear o abrir puertas.

## Fase G — Sonido y pulido
- Ambiente (mar, viento), puertas, pasos, interior del restaurante. Audio con licencia documentada.

## Validación por fase
Compila · PIE sin errores en log · prueba con teclado y mando · rendimiento · documentar en `Docs/` qué se hizo, por qué, limitaciones y riesgos.

## Lo que no se construye todavía
Mundo completo de Fuerteventura, multijugador, vehículos, combate, economía, miles de NPC, IA autónoma de personajes.

## Informe final de cada fase
STATUS (READY/PARTIAL/BLOCKED) · CHANGED · TESTED · RISKS · NEXT. No declarar "terminado" sin haberlo probado en PIE.
