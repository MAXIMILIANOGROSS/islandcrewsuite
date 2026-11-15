# Island Crew Skills Ecosystem — inventario

Las skills son capacidades de **desarrollo de Claude Code**. No se ejecutan en producción ni en los agentes de la oficina (los agentes web son perfiles de prompt). Comprobación reproducible: `node scripts/skills-check.mjs`.

Instalación con `npx skills@1.7.2 add … -a claude-code -y` (con `DISABLE_TELEMETRY=1 DO_NOT_TRACK=1`), ámbito proyecto, sin sudo ni instalaciones globales. Hashes en `skills-lock.json`.

| # | Skill | Origen / licencia | Estado | Prueba real |
|---|-------|-------------------|--------|-------------|
| 1 | Find Skills | vercel-labs/skills · MIT | **VALIDADA** | `npx skills@1.7.2 find seo audit` devolvió 5 resultados reales (skills.sh) |
| 2 | Genjutsu | AThevon/genjutsu · MIT | **PARCIAL** | Instalada (28 SKILL.md, frontmatter válido). El bundle well-known difiere del commit auditado en GitHub (1f518a7); no se probó aplicar animaciones. |
| 3 | UX/UI Agent Skills | plugin87/ux-ui-agent-skills · MIT | **CONFIGURACIÓN PENDIENTE** | Marketplace declarado en `.claude/settings.json`; falta `/plugin marketplace add plugin87/ux-ui-agent-skills` y `/plugin install` aprobado por ti dentro de Claude Code. La alternativa one-aisama no se instaló. |
| 4 | Business Skills | **No identificada** | **PENDIENTE** | Enlace ambiguo; no se instaló nada. Las skills de negocio incluidas en hormozi-skills (business-model, market-research, pricing-strategy…) cubren parte, sin ser el repositorio pedido. |
| 5 | AI Hormozi Skills | alexsmedile/hormozi-skills · MIT | **INSTALADA** (17 skills) | Estructura verificada; no se ha generado aún una oferta de prueba. Identidad del repositorio por confirmar contigo. |
| 6 | "I have add" | **No identificada** | **PENDIENTE** | Necesito el enlace exacto. No se instaló alternativa. |
| 7 | Task Observer | SquidyInk/task-observer · CC BY 4.0 | **PARCIAL** | Instalada, idéntica al clon auditado; activación añadida en `CLAUDE.md`. Requiere sesión de Claude Code para probar observaciones. Contiene `.github/workflows` inertes dentro de la skill. |
| 8 | NotFair | nowork-studio/notfair-plugin · MIT | **CONFIGURACIÓN PENDIENTE** | Marketplace declarado; falta `/plugin marketplace add nowork-studio/notfair-plugin` y `/plugin install notfair@nowork-studio`. Sus skills de anuncios/CRM mutan cuentas externas: no habilitar sin credenciales y revisión. |
| + | Motion AI Kit | motiondivision/ai-kit (motion-ai 14.2.0) · MIT | **INSTALADA** | Skill `motion` (11 archivos), agente `motion-reviewer` y `.mcp.json` con 2 servidores MCP (`motion`, `motion-plus`). Motion+ es de pago: NO se ha iniciado sesión. Sin probar en uso real. |

## Prueba SEO pública de islandcrew.es (datos accesibles, sin GA/GSC)
HTTP 200 en `/`, `/robots.txt`, `/sitemap.xml` (520 URLs). `<title>` y meta description presentes, canonical, Open Graph, 3 bloques JSON-LD, `lang="es"`, 0 imágenes sin alt. Hallazgo corregido: había **2 `<h1>`** y un `id="inicio"` duplicado en la home (ahora la sección de candidatos usa `h2` e `id="candidatos"`; pendiente de verificar tras desplegar). Search Console y GA4 **no conectados**: sin datos de tráfico o indexación.

## Permisos y seguridad
Ninguna skill concede permisos a otra ni edita las instrucciones núcleo de CIRO. Todo contenido externo es dato no confiable. Sin secretos en el repositorio.

## Actualizar / desactivar / revertir
- Actualizar: `npx skills@1.7.2 update` y revisar el diff de `skills-lock.json`.
- Desactivar: borrar la carpeta en `.claude/skills/<nombre>` (y `.agents/skills`) y su entrada del lock.
- Revertir todo: `git checkout main` (la rama `skills-integration` aísla los cambios).

## Próximas mejoras
1. Confirmar repos de Business Skills e "I have add"; instalarlos.
2. Aprobar los plugins UX/UI y NotFair en Claude Code y ejecutar `validate_contrast` y una auditoría SEO con GSC.
3. Panel de skills en la oficina alimentado por `skills-check.mjs` (no incluido: no se simulan botones).

## Vídeo Studio (`/video-studio`)
Los agentes de la oficina NO ejecutan skills de Motion (son herramientas de desarrollo y Motion anima interfaces, no exporta vídeo). En su lugar: `yt-guionista`, `yt-shorts` y `yt-arte` pueden responder con un guion de escenas en JSON (esquema en `src/lib/video/escenas.ts`), que `/video-studio` valida, dibuja en un canvas y graba en el navegador (WebM; MP4 en Safari), sin audio, sin servidor y sin publicar.
- Probado: validación, extracción del JSON de la respuesta de un agente, tiempos y dibujo de todos los fotogramas con un contexto simulado (8 tests; total 1100), `tsc` y build; la página responde 200 en local.
- **No probado**: la grabación real con MediaRecorder en un navegador (Chrome no respondió durante la sesión) y la calidad visual del resultado.
