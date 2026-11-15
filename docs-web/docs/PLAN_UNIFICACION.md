# Plan de unificación — Island Crew

Estado a 2026-10-18. Todo lo marcado **hecho** está en `main` y comprobado por tests; lo demás es plan.

## Fases del prompt maestro
| Fase | Estado |
|---|---|
| 1. Inventario | **Hecho** (`MAPA_UNIVERSO.md`). Falta código de la app iOS (no está en este repo). |
| 2. Mapa del universo | **Hecho** (`MAPA_UNIVERSO.md`). |
| 3. Biblia de marca | **Hecho** (`BIBLIA_ISLAND_CREW.md`, 18 apartados). |
| 4. Arquitectura visual | **Parcial.** Tokens en `brand/tokens.ts` y `:root`; test de coherencia añadido. Falta migrar constantes locales de pantallas antiguas (gradual). |
| 5. Integración funcional | **Parcial.** Cuatro experiencias por perfil (portada, accesos, menú). Falta: chat flotante por perfil y auditoría de autorización ruta a ruta. |
| 6. Implementación | En curso, por etapas. |
| 7. Verificación | Tests unitarios, tipos, build y e2e (Playwright, escritorio y móvil). |
| 8. Optimización | Pendiente: trocear `RealTownWorld.tsx` (H9), revisar peso de imágenes. |
| 9. Documentación | **Hecho** en esta entrega; mantener al día. |

## Prioridades siguientes (por valor y riesgo)
1. **Registro de usuarios nuevos fiable (P0).** Comprobar en producción: confirmar correo activado, SMTP propio (Resend), URLs de redirección y plantillas. Depende de configuración en Supabase.
2. **Autorización real por rol (P0).** Revisar las 56 rutas API y las políticas RLS: ninguna función de empresa accesible a una cuenta de trabajador. Añadir tests de permisos.
3. **La Cabra como personaje transversal (P1).** Un único documento de personalidad y límites usado por web, mundo y oficina; chat flotante con sugerencias por perfil.
4. **Contrato común de misión y ficha de NPC (P1).** H2 y H3.
5. **Agentes con permisos explícitos (P1).** Para cada agente: finalidad, herramientas, contexto, confirmación en acciones importantes y escalado humano. Ya existe `docs/AGENTES.md`; falta cotejarlo con el código.
6. **Modelo de negocio (P2).** Validar con 5–10 negocios antes de publicar nada; hoy todo es gratuito.
7. **Rendimiento (P2).** `RealTownWorld.tsx`, carga diferida de 3D, imágenes.
8. **App iOS (P2).** Auditar su identidad visual cuando se aporte su repositorio.

## Qué se ha decidido no hacer
No fusionar web, mundo, oficina y app en un único código. No añadir animaciones pesadas. No publicar precios ni cifras. No presentar integraciones no comprobadas.
