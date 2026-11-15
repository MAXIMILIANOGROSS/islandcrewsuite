# Island Crew — Design system (P0)

Estado: **base mínima**. Los tokens existen; la migración de pantallas es gradual. Lo nuevo usa tokens; lo antiguo sigue con `INK/YEL/PAPER` de `housing/ui`.

## Tokens (`src/app/globals.css`, prefijo `--ic-`)
- **Color:** `ink #07182E`, `yellow #FFD600`, `cream #F4E3B8` (arena), `paper #FFFDF7`, `text-muted #526071`; estados `success / success-bg`, `warning-bg`, `error / error-bg`.
- **Espaciado:** `space-1..6` = 4, 8, 12, 16, 24, 32 px.
- **Radio:** `sm 0`, `md 2px`, `lg 6px` (estilo neo-brutalista: esquinas casi rectas).
- **Sombra:** `sm 2px`, `md 4px`, `lg 8px` (desplazada, sin difuminar).
- **Movimiento:** `fast 120 ms`, `normal 220 ms`, `slow 400 ms`, `ease cubic-bezier(.22,.9,.32,1)`. Todo movimiento nuevo va bajo `prefers-reduced-motion: no-preference`.
- **Táctil:** `--ic-touch: 44px` mínimo para botones.
- **Única fuente en TypeScript:** `src/lib/ui/brand.ts` (INK, YEL, CREAM, PAPER…); `BRAND` de `lib/brand/tokens.ts` toma de ahí el navy y el amarillo. El crema claro de fondo `BRAND.cream` (#FFF8E6) es distinto del arena `--ic-cream` a propósito. Un test comprueba que CSS, TypeScript y Tailwind coinciden.
- Tailwind: los mismos colores (también `ink`, `yellow`, `paper` sin prefijo, ya enlazados a los tokens) disponibles como `bg-ic-ink`, `text-ic-yellow`, etc.

## Primitivas (`src/components/ui/`)
| Componente | Uso | Accesibilidad |
|---|---|---|
| `Dialog` | Confirmaciones y celebraciones | `<dialog>` nativo: foco atrapado, Esc cierra, `aria-labelledby` |
| `ToastProvider` / `useToast` | Avisos breves | `aria-live="polite"`, botón de cierre con etiqueta, se cierran solos (5 s) |
| `Skeleton` / `CardSkeleton` | Carga con la forma real | `role="status"`, animación solo si no hay reducción de movimiento |

Clases globales: `.ic-btn` (botón, foco visible 3 px), `.ic-btn.ghost`, `.ic-skel`, `.ic-pop`, `.ic-toast`.

## Componentes de producto
`NextAction` (siguiente paso), `LevelUp` (subida de nivel, saltable, sin sonido), `Goat` (SVG/imagen existente con 4 estados: neutral, celebrate, search, error).

## Reglas
1. Colores, espacios y sombras nuevos salen de tokens, no de valores literales.
2. Un modal es un `Dialog`; un aviso es un `toast`; una carga es un `Skeleton`.
3. Movimiento: explica, confirma o emociona; si no, no existe. Nunca sonido por defecto.
4. Mobile primero; objetivos táctiles ≥ 44 px; foco visible siempre.
5. Revisar en 375, 768, 1024 y 1440 px, con teclado y con movimiento reducido.

## Pendiente (no hecho)
Migrar `housing/ui` a tokens, reemplazar los `confirm/prompt` nativos por `Dialog`, tipografía documentada, dark mode (no se decide aún), Storybook, iconografía única (hoy emojis).

## Botones: familias y cuándo usar cada una (D-013)
| Clase | Dónde | Notas |
|---|---|---|
| `.btn` (`.light`, `.dark`) | Web pública y portada | Estilo de marca: borde marino, sombra desplazada, amarillo. Es el botón principal visual. |
| `.ic-btn` (`.ghost`) | Paneles, formularios, diálogos (`confirmar`, `Dialog`) | Misma estética que `.btn`; es el que se usa en lo nuevo. |
| `.login-pill` (`.primary`, `.oauth`) | Solo pantalla de acceso/registro | Píldora sobre fondo oscuro; no se usa fuera de `/login`. |

Reglas: un solo botón principal (amarillo) por pantalla; peligro = rojo con confirmación (`confirmar(..., { peligro: true })`); botón de icono siempre con `aria-label`. Estados obligatorios en las tres familias: foco visible, pulsado, desactivado y cargando (`aria-busy="true"`).
