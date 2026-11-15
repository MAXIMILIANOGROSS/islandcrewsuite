# Island Crew Intelligence Network

Capa de investigación de la oficina virtual: CIRO y los agentes autorizados buscan en fuentes externas reales, guardan las investigaciones por proyecto y entregan informes con enlaces originales. Solo lectura. Nada se publica.

## 1. Auditoría (16 oct 2026)
- Web: Next.js 15 en Vercel (autodeploy desde `main`), Supabase (auth + RLS), sin trabajador persistente ni Mac mini conectado.
- Oficina: `AGENTES` (30) + `AGENTES_YT` (13), permisos por herramienta en `src/lib/oficina/permisos.ts`, tareas con estados y aprobación humana, ciclo por cron.
- Ya existía: búsqueda web con Exa/Serper/Tavily (`src/lib/oficina/busqueda.ts`) y el flujo del Investigador. Se reutiliza; no hay MCP ni navegador en servidor.
- Secretos: variables de entorno en Vercel; el navegador nunca las ve.
- Agent-Reach: v1.5.0, MIT, Python ≥ 3.10, commit fijado `94f06c1969dfc1834001269d79d3ad0972d9dee6`. Es un CLI/skill que instala y diagnostica herramientas externas por canal (gh, yt-dlp, mcporter/Exa, feedparser, Jina Reader, cookies de navegador para redes…). Evidencia del `doctor` real en `docs/evidencias/agent-reach-doctor.md`.
- Aviso de cadena de suministro: un commit del propio repo dice que deja de recomendar «el paquete agent-reach no relacionado de PyPI». **No instales `pip install agent-reach` desde PyPI**: instala siempre desde GitHub con el commit fijado.

## 2. Arquitectura
```
Oficina web (/oficina → Intelligence)  →  /api/intel/* (sesión + administrador + parada global + límites)
   →  permisosRed (fuentes por agente)  →  ejecutor (diagnóstico → plan → consultas → normalizar → deduplicar → informe)
   →  conectores TypeScript (Jina Reader, API GitHub, RSS, buscador)  →  intel_jobs / intel_diagnostico (Supabase, RLS por propietario)
```
- Vercel no puede ejecutar el CLI Python ni procesos persistentes. Por eso los conectores **web, GitHub y RSS** reproducen en TypeScript los mismos backends que usa Agent-Reach v1.5.0 (Jina Reader, API de GitHub equivalente a `gh`, feeds). No se ejecuta código de Agent-Reach en producción hoy.
- Los trabajos corren en el servidor con `after()` de Next: la petición del navegador termina enseguida (202) y la interfaz consulta el estado. Las que quedan colgadas más de 3 minutos se marcan «Fallida: interrumpida» (no se reintentan solas).
- YouTube (yt-dlp), redes sociales y la búsqueda semántica de Exa-MCP requieren el **trabajador Python** (fase 2, abajo). Hoy aparecen como «Necesita configuración» y no se simulan.

## 3. Archivos
`src/lib/intel/{tipos,seguridad,conectores,diagnostico,plan,informe,ejecutor,permisosRed,servidor}.ts` · `src/app/api/intel/{investigar,diagnostico,accion}/route.ts` · `src/components/IntelligenceTab.tsx` (pestaña «🔎 Intelligence» en `/oficina`) · `TODO_CORRER_103_INTELLIGENCE.sql` · `scripts/intel-demo.mjs` · `tests/intel.test.mjs`.

## 4. Seguridad
- Solo administrador (como la oficina). RLS: cada usuario solo ve sus investigaciones y su diagnóstico.
- URLs: solo http(s) públicas (sin credenciales, puertos raros, localhost, redes privadas ni metadatos cloud). Repos: solo `github.com` con nombres validados. No hay ejecución de comandos arbitrarios.
- Todo contenido recuperado es dato no confiable: se delimita en el prompt, se detectan instrucciones incrustadas (se avisan en «Limitaciones» y no se obedecen), y la síntesis de IA se descarta si cita fuentes inexistentes.
- Secretos (`GITHUB_TOKEN`, `JINA_API_KEY`, claves del buscador) solo en el servidor; `sinSecretos` limpia errores. No viajan al navegador, al prompt ni al informe.
- Límites: 15 investigaciones nuevas/hora, `INTEL_MAX_DIA` (20 por defecto) en 24 h, 2 simultáneas, 40 s de presupuesto por investigación, parada global de la oficina respetada.

## 5. Costes y variables (opcionales)
| Variable | Para qué | Coste |
|---|---|---|
| `GITHUB_TOKEN` | Subir de 60 a 5.000 consultas/hora a la API de GitHub (token de solo lectura, sin permisos) | gratis |
| `JINA_API_KEY` | Más cuota en Jina Reader | gratis con límites / de pago según plan (comprobar en jina.ai) |
| `EXA_API_KEY` / `SERPER_API_KEY` / `TAVILY_API_KEY` | Búsqueda web general | cuota gratuita limitada, luego de pago |
| `INTEL_MAX_DIA` | Tope diario | — |

## 6. Estado de las pruebas de aceptación
Ver `docs/evidencias/intel-primera-investigacion.md` (informe real) y la sección «Pruebas» de la entrega. Lo que depende de SQL 103 o de que el usuario lo pruebe en la web desplegada **no está marcado como pasado** hasta que se verifique.

## 7. Fase 2: trabajador Python con Agent-Reach (pendiente)
Requisitos: máquina con Python ≥ 3.10 (el Mac actual tiene 3.9), pipx y Node. Procedimiento controlado:
```
pipx install "git+https://github.com/Panniantong/Agent-Reach.git@94f06c1969dfc1834001269d79d3ad0972d9dee6"
agent-reach install --env=auto        # solo comprueba, no instala nada
agent-reach doctor                    # estado por canal
```
`--system` instala herramientas externas: solo con tu aprobación explícita y canal por canal. Los canales con cookies (Twitter/X, Reddit, Xiaohongshu…) dependen de sesiones de navegador locales: no se copian al servidor. Actualizar = reinstalar con otro commit tras revisar el diff; revertir = reinstalar el commit anterior (`pipx uninstall agent-reach`).
Diseño previsto: el trabajador sondea `intel_jobs` en estado `en_cola` con una clave de servicio propia, solo ejecuta las operaciones del adaptador (lista blanca de canales y parámetros validados) y escribe resultados normalizados.

## 8. Limitaciones conocidas
- YouTube, redes sociales y Exa-MCP: no disponibles hasta la fase 2.
- Jina Reader y GitHub pueden limitar por IP; el diagnóstico lo muestra como «Limitada».
- El informe verificable no usa IA; la síntesis solo aparece si hay IA configurada y cita bien.
- Roles de Academy y Operations de hostelería no existen como agentes: no se han creado duplicados; se pueden autorizar en `permisosRed.ts` cuando existan.
- Licencias: se informa la licencia declarada del código; la de recursos (modelos, texturas, audio) hay que comprobarla aparte.
