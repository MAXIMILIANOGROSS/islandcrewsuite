# Mapa del universo Island Crew (inventario comprobado, 2026-10-18)

Generado a partir del repositorio `island-crew-web`. Lo que no está aquí no se ha comprobado.

## 1. Piezas y repositorios
| Pieza | Dónde | Tecnología | Estado de auditoría |
|---|---|---|---|
| Web y plataforma | este repo, `src/` | Next.js 15, React 18, Supabase (auth, RLS, RPC), Resend, Vercel | Auditada |
| Island Crew World (`/mundo/real`) | `src/components/RealTownWorld.tsx` y relacionados | Three.js / R3F, datos OSM | Auditada (H9: archivo muy grande) |
| Servidor de mundo | `servidor-mundo/` | Cloudflare Workers + Durable Objects | Documentado en su README; no desplegado/verificado desde aquí |
| Servidor PvP | `game-server/` | Node, WebSocket, Supabase | Documentado en su README; no verificado desde aquí |
| Oficina virtual y agentes | `src/app/oficina*`, `src/lib/oficina`, `src/lib/agents`, `docs/OFICINA_*.md` | Next.js + Supabase + LLM | Revisada a nivel de documentación y rutas |
| La Cabra | `src/lib/goat`, `src/lib/cabra*.ts`, `AiFaqChat`, `/asistente`, API `goat-chat`, `cabra` | LLM en cadena con límite de uso | Revisada |
| App iOS | App Store (enlace en el menú) | — | **Su código no está en este repo; no auditada** |
| Datos | `supabase/migrations` (56) + scripts SQL `TODO_CORRER_*` | PostgreSQL | Índice en `SQL_INDICE.md` |

## 2. Qué ve cada perfil (misma web, distintos botones)
Definido en `src/lib/perfiles.ts` (portada y destino) y `src/lib/experiencias.ts` (botones de portada, accesos rápidos y menú). Las secciones de la portada dirigidas a otro perfil se ocultan con `data-solo`.
| Perfil | Destino principal | Menú desplegable |
|---|---|---|
| Trabajador | `/soy-trabajador` | Buscar trabajo · Vivir en la isla · Comunidad |
| Negocio | `/restaurantes` | Contratar personal · Tu operación · Tu equipo |
| Llegando a Canarias | `/desde-fuera` | Antes de llegar · Al aterrizar · Trabajo y comunidad |
| Proyecto completo | `/proyecto` | El proyecto · Participar · Transparencia |

## 3. Servicios compartidos
Cuenta y sesión (Supabase Auth, confirmación por correo, recuperar contraseña); consentimientos versionados (`consent_events`); límite de uso persistente (`rate_hit`); borrado de cuenta real (`/api/cuenta-eliminar` + cascada + `purge_user_data`); avisos por correo (`lead-notify`, `legal-notify`); analítica anónima (`src/lib/analytics.ts`, `universe/events.ts`); registro de estado de funciones (`universe/status.ts`, `catalog.ts`); tokens de marca (`brand/tokens.ts`).

## 4. Autorización (ocultar no es proteger)
Perfil elegido = solo presentación, en el navegador. Protección real: sesión + RLS en Supabase y verificación en servidor en las rutas API. Pendiente de revisar ruta a ruta (ver plan).

## 5. Catálogo de productos (fuente: `src/lib/catalog.ts`)
| Producto | Público | Estado | Ruta |
|---|---|---|---|
| Crew Network | trabajadores | disponible | /network |
| Crew CV | trabajadores | disponible | /crearcurriculum |
| Crew Jobs | trabajadores | disponible | /swipe |
| Island Crew World | mundo | disponible | /mundo/real |
| Meditaciones y bienestar | trabajadores | disponible | /vida/alma |
| Island Crew FOMO | trabajadores | disponible | /fomo |
| Vida en la isla | trabajadores | disponible | /vida |
| Vivienda | trabajadores | en desarrollo | /housing |
| Chef y recetas | trabajadores | disponible | /chef |
| eSIM | trabajadores | en desarrollo | /esim |
| Empleos verificados | trabajadores | en desarrollo | /empleos |
| Crew Plus | trabajadores | en desarrollo | /crew-plus |
| Crew Coach | trabajadores | en desarrollo | — |
| Crew Academy | trabajadores | en desarrollo | — |
| Crew Benefits | trabajadores | en desarrollo | — |
| Island Crew Talent | empresas | disponible | /talent |
| Restaurant OS | empresas | disponible | /restaurant-os |
| Mando de cocina | mundo | en desarrollo | — |
| Carta rentable | mundo | en desarrollo | — |
| Estándar multisede | mundo | en desarrollo | — |
| Servicio de sala | mundo | en desarrollo | — |
| Reserva de grupo | mundo | en desarrollo | — |
| Casos de gestión | mundo | en desarrollo | — |
| Academia Virtual | mundo | en desarrollo | — |
| Academy Island Crew | mundo | en desarrollo | — |
| Island Crew YouTube Studio | mundo | en desarrollo | — |
| Island Crew Vídeo Studio | mundo | en desarrollo | — |
| Island Crew Interviews | empresas | en desarrollo | — |
| Compromiso de gratuidad | trabajadores | disponible | /gratis |
| Entrada por perfiles | trabajadores | disponible | /empezar |
| Centro legal y consentimientos | trabajadores | en desarrollo | /legal |
| Intelligence Network (oficina interna) | mundo | en desarrollo | — |
| Simulador de cocina | mundo | en desarrollo | — |
| Carreras de hostelería | mundo | en desarrollo | — |
| Crew Business | empresas | en desarrollo | /empresas |
| Crew Hiring | empresas | en desarrollo | — |
| Crew Academy for Teams | empresas | en desarrollo | — |
| Crew Marketplace y Experiencias | empresas | en desarrollo | /marketplace |

El estado "en desarrollo" con ruta existente significa que la página existe pero la función no se da por completa; no se promociona como disponible.
