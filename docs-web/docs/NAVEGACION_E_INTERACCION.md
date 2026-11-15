# Navegación, botones e interacciones — Island Crew

Estado: **fase 1 (auditoría y reglas). Nada de esto cambia todavía el aspecto de la web.** Las cifras salen del código a 2026-10-18 (442 ficheros `.tsx`).

## 1. Inventario real (evidencia)

| Medida | Valor | Lectura |
|---|---|---|
| Etiquetas `<button>` | 1250 | Muchas son del juego y de paneles internos. |
| Enlaces (`<a>` / `Link`) | 785 | |
| Clases de botón distintas | `ic-btn` (104 usos), `btn` (68), `login-pill` (29), `cta` (3), `pill` (1) | **Tres sistemas de botón conviven.** Es la mayor fuente de incoherencia. |
| Botones con estilo en línea | 184 | No heredan hover/foco/estados del sistema. |
| `aria-label` | 457 | Buena base de accesibilidad; falta medir los botones de icono. |
| Diálogos / modales | 55 referencias | Hay `Dialog` nativo (`ui/Dialog`) y modales propios. |
| `confirm()` / `alert()` nativos | 29 | `design-system.md` ya los marca para sustituir por `Dialog`. |
| Ficheros con más botones | `GameLayer` (30), `mundo/jugar` (19), `mundo` (17), `DealPanel` (17) | Juego y paneles: reglas propias (ver §5). |

Menús por perfil (fuente: `src/lib/experiencias.ts`): trabajador 3 secciones / 10 enlaces; negocio 3 / 12; llegando 3 / 11; proyecto 3 / 9. Más 6 accesos rápidos en portada por perfil. Ninguno supera 12 enlaces en el desplegable: el problema no es el tamaño de cada menú, sino que **todo vive dentro de un desplegable** y la acción más frecuente cuesta dos clics.

## 2. Decisiones (ver D-013)

1. **Las cuatro experiencias y la web idéntica (D-010) no cambian.** Esto solo ordena *cómo* se llega a las acciones.
2. **Visibles siempre, por perfil:** 3 accesos directos en la barra superior en escritorio (los 3 primeros de `EXPERIENCIAS[perfil].menu`). El resto queda en el desplegable.
3. **Un acceso rápido contextual** ("¿Qué quieres hacer hoy?") en la portada, con las acciones del perfil. Ya existe como `QuickAccess`; se mantiene y no se duplica en la barra.
4. **Jerarquía de botones única:** primario (amarillo, uno por pantalla), secundario (oscuro con borde), terciario (enlace), peligro (con confirmación), icono (siempre con `aria-label`). Estados: normal, hover, foco, pulsado, cargando, desactivado, éxito.
5. **Un solo sistema de botón.** Se adopta `ic-btn` (tokens `--ic-*`). `btn`, `login-pill` y `cta` se migran por fases; no se borra ninguno hasta que no quede uso.
6. **Menos interrupciones:** los `confirm()` nativos pasan a `Dialog`; solo se confirma lo destructivo, económico o irreversible.
7. **Búsqueda:** una sola caja (La Cabra). Búsqueda global y paleta de comandos descartadas por ahora; si se reabre, debe respetar permisos.
8. **La Cabra** es acceso opcional a ayuda; nunca sustituye al botón directo.

## 3. Reglas por patrón

| Necesidad | Patrón |
|---|---|
| 2–4 secciones equivalentes | Pestañas |
| Funciones independientes | Tarjetas de acceso |
| Criterio de búsqueda frecuente | Filtro visible |
| Contenido secundario largo | Acordeón |
| Proceso largo | Pantalla propia, no modal |
| Acción sobre un elemento | Menú contextual |
| Confirmación breve | `Dialog` |

## 4. Plan por fases

- **F1 (hecha):** inventario, reglas, decisión D-013, test que impide empeorar (§6).
- **F2 (hecha, solo escritorio ≥1280 px):** 3 accesos directos por perfil en la barra superior; en pantallas menores siguen dentro del desplegable. Comprobado por e2e: sin desbordar a 1440 px y ocultos en móvil. Pendiente revisión visual a 1024/1280 px por una persona.
- **F3 (hecha):** los 29 `confirm()` nativos usan `confirmar()` (`src/lib/confirmar.ts`, diálogo propio accesible). Un test impide volver a usar los nativos.
- **F4 (parcial):** `.cta` no es un botón sino una sección (aclarado). `.btn` e `.ic-btn` ya comparten estética; `login-pill` se queda como variante exclusiva de `/login` por su fondo oscuro. Hecho: estados comunes (foco, pulsado, cargando, desactivado) y tabla de familias en `design-system.md`. Hecho también: 72 botones de envío/guardado en 48 ficheros anuncian su estado de carga con `aria-busy` (accesibilidad, sin cambio visual). Revisión de botones de icono: ninguno sin etiqueta accesible. Los botones con estilo en línea se concentran en los mundos jugables (`KitchenWorld`, `AcademiaWorld`) y paneles; `/cuenta` ya usa objetos de estilo compartidos (`pillPrimary`, `pillGhost`). No se migran a ciegas porque cambiaría el aspecto: se hace pantalla a pantalla con revisión visual del fundador.
- **F5 (cerrada por decisión del fundador, 2026-10-18):** se mantiene **una sola caja de búsqueda**, la de La Cabra. No se construye búsqueda global ni paleta de comandos. Se reabre solo si hay datos de uso que lo justifiquen.

Criterio de cierre de cada fase: tsc, lint, tests, Playwright con axe, y comprobación manual móvil.

## 5. Fuera de alcance

El juego en primera persona (`GameLayer`, `mundo/*`) y las herramientas internas tienen controles propios; comparten identidad y accesibilidad, no la barra de navegación.

## 6. Qué no se afirma

No hay búsqueda global, centro de notificaciones ni paleta de comandos implementados. No se han medido tiempos de tarea con usuarios reales: la "facilidad" es una hipótesis hasta probarla.
