# Island Crew — Biblia oficial del universo

Referencia única para decisiones de diseño, desarrollo, marketing y producto, para personas y agentes de IA. Actualizada el 2026-10-18 tras la auditoría de unificación (ver `MAPA_UNIVERSO.md` y `PLAN_UNIFICACION.md`).

**Regla de lectura:** cada afirmación de producto lleva su estado. **Implementado** = existe en este repositorio y se ha comprobado. **Planificado** = hay diseño o código parcial. **Propuesto** = idea sin trabajo comprometido. El estado oficial de cada función vive en `src/lib/universe/status.ts` y `src/lib/catalog.ts`; esta Biblia no puede contradecirlos.

## 1. Propósito y misión
Conectar personas, negocios, oportunidades y experiencias reales en Canarias, empezando por Corralejo (Fuerteventura), con tecnología útil y una identidad propia.

## 2. Visión a largo plazo
Un ecosistema donde quien llega, trabaja, contrata o simplemente explora encuentra en un mismo lugar lo que necesita, y puede pasar de la web a la Cabra, al mundo explorable y a las herramientas de negocio sin sentir que cambia de marca. Hoy el alcance real es Corralejo; Fuerteventura y otras islas son horizonte (`en desarrollo`).

## 3. Valores
Honestidad de estado; utilidad antes que espectáculo; privacidad y consentimiento; comunidad local sin excluir a quien llega; gratis primero (hoy todo es gratuito y no hay precios publicados); accesibilidad AA; calidad antes que cantidad.

## 4. Personalidad de marca
Cercana, inteligente, directa, optimista y útil. Local sin ser excluyente, tecnológica sin ser fría, ambiciosa sin promesas vacías. Español de España, tuteo, canario sin caricatura. Humor de la Cabra: atrevido pero respetuoso.

## 5. Historia y narrativa
Canarias está llena de personas, negocios, oportunidades y lugares que a menudo permanecen desconectados. Island Crew ayuda a descubrirlos y conectarlos. La Cabra es la guía; los negocios aportan oportunidades y conocimiento del territorio; los trabajadores aportan talento; quien llega descubre recursos; el mundo explorable convierte el descubrimiento en experiencia. No se fuerzan conexiones entre funciones que aún no están integradas.

## 6. Propuesta de valor
Una puerta de entrada con cuatro experiencias adaptadas a la persona: trabajador, negocio, llegando a Canarias y proyecto completo. Una sola web con la misma portada, el mismo diseño y las mismas secciones; lo que cambia por perfil son los botones y accesos, y se ocultan las secciones dirigidas a otros perfiles (decisión D-010).

## 7. Público objetivo
Personas que buscan trabajo en hostelería y servicios; negocios de hostelería y turismo en Corralejo; personas que llegan a Canarias; quien explora el proyecto.

## 8. Necesidades que resuelve
Encontrar y ofrecer empleo con consentimiento; crear un currículum; organizar un restaurante; orientarse al llegar (conexión móvil, transporte, vivienda); conocer el lugar; bienestar y aprendizaje práctico.

## 9. Arquitectura de productos (estado comprobado en el repo)
Plataforma: web Next.js 15 (200 páginas, 56 rutas API, 56 migraciones Supabase). Productos y estado: ver tabla en `MAPA_UNIVERSO.md`. Resumen: Crew Network, Crew CV, empleo (swipe), Island Crew World (`/mundo/real`), bienestar (`/vida/alma`), FOMO, Chef AI, Talent y Restaurant OS están `disponible`; Housing, eSIM, empleos verificados, Crew Plus, entrevistas, Centro legal y varias herramientas de empresa están `en desarrollo`. App iOS: existe en la App Store (enlace en el menú) pero su código no está en este repositorio y no se ha auditado aquí.

## 10. Identidad visual
Fuente de verdad en código: `src/lib/brand/tokens.ts` y variables `:root` de `src/app/globals.css`. Núcleo: marino `#07182E`, amarillo `#FFD600`, papel `#FFFDF7`, franjas de la bandera de Canarias. Acentos permitidos por D-001 (opción C): turquesa/cian y coral, siempre con texto marino (el blanco sobre ellos no pasa AA). Neutros: grises azulados `#526071`. Tipografías: Archivo Black (titulares) y Space Grotesk (texto). Estilo: bordes gruesos con sombra desplazada. Regla: no introducir colores sueltos por módulo; usar tokens. Un test comprueba que los tokens de código y CSS coinciden.

## 11. Lenguaje y tono
Ver §4. Prohibido: voseo y latinoamericanismos (hay test), promesas de resultados, cifras o testimonios inventados, presentar como disponible lo que no lo está.

## 12. Personajes y recursos narrativos
La Cabra: guía y punto de entrada conversacional (web: `AiFaqChat`, `/asistente`; mundo: NPC y cabras; oficina: agentes). Personalidad común: cercana, divertida, útil. No se presenta omnisciente ni afirma haber ejecutado acciones que no ha ejecutado. Los personajes del mundo son de demostración salvo indicación contraria. Plantilla de ficha en el Anexo A.

## 13. Experiencia de usuario
Cuatro perfiles (`src/lib/perfiles.ts`, `src/lib/experiencias.ts`): botones de portada, accesos rápidos y menú desplegable propios de cada perfil; secciones ajenas ocultas por CSS (el contenido sigue en el HTML para SEO). El perfil se guarda solo en el navegador. Importante: **ocultar no es proteger**: las acciones sensibles deben tener autorización real en servidor/RLS (ver §16 y `docs/SECURITY_AND_PRIVACY.md`).

## 14. Modelo de negocio
**Hoy:** todo es gratuito; no hay precios ni cobros publicados (`/gratis`). **Propuesto, sin implementar:** suscripciones o servicios para empresas, selección de talento, herramientas operativas (Restaurant OS), oficina virtual, formación, experiencias patrocinadas con etiqueta clara. Criterio para activar cualquiera: demanda validada con negocios reales, cliente que paga identificado, coste de mantenimiento asumible, revisión legal y de privacidad. No se publican cifras de mercado ni resultados económicos.

## 15. Estrategia de crecimiento
Lo comprobable primero: visitas → entradas a `/mundo/real` → currículums creados → negocios interesados. Pilotos con 5–10 negocios de Corralejo con permiso escrito. Contenido real de la isla con autorización. Nada de pago hasta validar demanda.

## 16. Principios tecnológicos
Next.js 15 + React 18 + Supabase (RLS) + Three.js/R3F para el mundo; servidor de mundo en Cloudflare Workers (`servidor-mundo`) y servidor PvP Node (`game-server`) como piezas independientes. Se unifica por identidad, contratos e integraciones, no por código único. IA: cadena Groq → Gemini → OpenRouter, con límite de uso persistente en servidor (`rate_hit`). Las rutas sensibles verifican sesión en servidor. Borrado de cuenta real con cascada. Dependencias externas nuevas: solo con revisión de licencia (D-004).

## 17. Reglas de coherencia (comprobadas por tests donde se indica)
1. Una identidad: tokens únicos (test).
2. Misma web para todos los perfiles; solo cambian botones y secciones visibles (test).
3. Todo enlace de menú/accesos de perfil apunta a una página que existe (test).
4. Todo producto `disponible` del catálogo con ruta apunta a una página que existe (test).
5. Estados honestos: ninguna función futura como disponible.
6. Nada nuevo sin enlace en el pie, en `/productos`, en `catalogo.ts` y en el sitemap.
7. Sin precios; sin datos personales del titular hasta que exista la empresa.
8. Privacidad y consentimiento antes que métricas; analítica anónima.
9. Una función no se elimina sin justificación escrita en `DECISIONES.md`.

## 18. Hoja de ruta de evolución
Ver `PLAN_UNIFICACION.md` (prioridades, estado y siguientes pasos) y `DECISIONES.md` (D-001 a D-012).

## Qué NO está unificado todavía (honesto)
La app iOS y la oficina virtual no se han auditado en este repositorio a nivel de código visual; la Cabra tiene capas de personalidad distintas en web, mundo y oficina; hay tres sistemas de misiones y varias capas de NPC (H2, H3 de `AUDITORIA_UNIFICACION.md`); el chat flotante no cambia por perfil. Todo ello figura en el plan.

---

# Anexo A — Plantillas y reglas operativas


## 1. Principios no negociables

1. **Honestidad de estado.** Cada función, lugar o personaje lleva una de estas etiquetas visibles: `disponible`, `demostración`, `en desarrollo`. Nunca se afirma que algo está desplegado, verificado o activo sin comprobarlo.
2. **Nada falso sobre el mundo real.** Las imágenes son ilustraciones de marca, no fotos del pueblo. Los negocios son fichas públicas derivadas de OpenStreetMap, sin verificar por Island Crew, y ningún negocio real figura como participante sin confirmación escrita.
3. **Personas.** Los personajes y diálogos de IA son una demostración; la IA no se presenta como profesional titulado (médico, abogado, asesor financiero).
4. **Gratis primero.** Cadena LLM: Groq → Gemini → OpenRouter (y Anthropic solo si hay clave). Es una cadena de respaldo, no una fusión.
5. **Licencias.** Ningún repositorio externo se adopta sin revisar licencia, compatibilidad con Next.js 15 / React 18 / Three.js y aprobación expresa del fundador.
6. **Accesibilidad.** Contraste AA, navegación por teclado, `prefers-reduced-motion`, alternativa en lista a toda experiencia animada.
7. **Sin gasto ni acciones externas sin aprobación** (envíos, publicaciones, pagos, despliegues).
8. **Tono.** Español de España, tuteo, cercano, canario sin caricatura.

## 2. Universo y marca

- Lugar: Corralejo, Fuerteventura (Canarias). Otros destinos (Lobos, etc.) son horizonte, `en desarrollo`.
- Cuatro arquetipos (ver `src/lib/crew/characters.ts`): mismas estadísticas totales, ninguno mejor que otro.
- Estética: crema, azul marino, amarillo, franjas de la bandera de Canarias (blanco, azul, amarillo), mar turquesa y olas; bordes gruesos con sombra desplazada (neo-brutalista).
- Fuente única de colores: `src/lib/brand/tokens.ts`.
- **Conflicto de paleta pendiente de decisión:** la Biblia propone #103B4A, #31B7B0, #E8D8B7, #F7F4EC, #FF725E, #202B30. La web actual y la petición reciente usan navy/amarillo/bandera. Se mantiene lo implementado; la paleta de la Biblia queda en `tokens.ts` como `bibliaProposal` por si se adopta.

## 3. Las 8 escenas del recorrido (`/recorrido`)

Archivo: `public/recorrido/manifest.json`. Orden: invitación → explora → negocio → camino → océano → Lobos → mundo social → únete (destino final `/mundo/real`). Estados: 1–4 y 8 disponible/demostración; 5–7 `en desarrollo`.

## 4. Plantillas

### 4.1 Ficha de PNJ
```
id:
nombre:
rol:                      # camarero, RR. HH., pescador…
lugar:                    # id de lugar
estado:                   # demostración | disponible
personalidad (3 rasgos):
qué sabe / qué NO sabe:
límites: no da consejo médico, legal ni financiero; no inventa datos de negocios reales
saludo:
3 respuestas de ejemplo:
fuente de datos:
```

### 4.2 Misión / quest
```
id:
título:
arquetipo recomendado (opcional):
objetivo (1 frase):
pasos (máx. 5):
recompensa (cosmética o de aprendizaje, nunca dinero real):
enseñanza:
estado: demostración | disponible | en desarrollo
accesibilidad: alternativa sin ratón / sin tiempo límite
```

### 4.3 Estado de lugares
| Estado | Significado | Se muestra como |
|---|---|---|
| `osm-sin-verificar` | Ficha pública de OpenStreetMap | "Ficha pública, no verificada" |
| `verificado` | Confirmado por Island Crew | Sello de verificado |
| `socio` | Acuerdo escrito con el negocio | Sello socio |
| `retirado` | A petición del titular | No se muestra |

### 4.4 Informe diario (solo recomendaciones)
```
Fecha:
1. CEO Digital: 3 prioridades del día (con motivo)
2. Analítica: visitas, entradas a /mundo/real, CV creados, leads (solo datos reales; si no hay, "sin datos")
3. Auditor: riesgos de honestidad, licencias, accesibilidad, enlaces rotos
4. Decisiones que necesitan al fundador
Sin acciones externas.
```
Se activa solo cuando el fundador lo pide expresamente.

## 5. Agentes y roles

Registro existente: CEO Digital, Analítica, Auditor, etc. Se añaden dos roles de control:
- **Accesibilidad:** revisa contraste, teclado, movimiento reducido, textos alternativos.
- **Cumplimiento de licencias:** revisa licencias de código, imágenes, fuentes y datos (OSM exige atribución ODbL) antes de adoptar nada.

## 6. Repos externos: política

Referencias para estudiar, no para instalar: Colyseus, React Three Fiber, Umami y similares. Antes de adoptar cualquiera: licencia, tamaño, mantenimiento, encaje con el stack, prueba en rama y aprobación. La base actual (Next.js + Three.js + Supabase) se mantiene.

## 7. Plan de 90 días (resumen)

- **Días 1–30:** publicar lo ya hecho (push), SQL 34–50, recorrido y botones en producción, medir entradas al mundo.
- **Días 31–60:** hablar con 5–10 negocios reales de Corralejo para pilotos con permiso escrito; fotos reales con autorización; revisión nativa de textos en italiano e inglés.
- **Días 61–90:** primer evento/quest social real, monetización opcional (precios, Stripe, aspectos legales) solo tras validar demanda.

Métricas: visitas → entradas a /mundo/real → CV creados → negocios interesados.

## 8. Preguntas abiertas

Fotos reales de Corralejo; revisión nativa de italiano; frases motivacionales; precios y Stripe; textos legales; adopción de la paleta de la Biblia.
