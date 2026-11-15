# Oficina Island Crew — repos de referencia (NO verificados)

Lista aportada por el CEO. No se ha comprobado licencia, actividad ni coste de ninguno. Antes de integrar: licencia, mantenimiento, dependencias, costes de API.

- Orquestación: langgraph, crewAI, openai-agents-python, pydantic-ai, agno, dify, Flowise, langflow.
- Automatización: n8n (licencia "fair-code", NO es open source libre: revisar uso comercial).
- Marketing: loopmark-agent, autonomous-ai-marketing-orchestrator, marketingskills, posthog, metabase, twenty, chatwoot.
- Vídeo: remotion (licencia propia, de pago para empresas), FFmpeg, moviepy, whisper, whisperX, auto-editor, OpenTimelineO.
- YouTube: youtube-automation-agent, youtube/api-samples, yt-dlp (descargar contenido ajeno puede infringir derechos/ToS).
- Memoria: pgvector (ya compatible con Supabase), chroma, qdrant, mem0.

## Estado honesto
- Producción de vídeo/YouTube: BLOQUEADO. Vercel no ejecuta FFmpeg/Remotion y falta credencial OAuth de YouTube. Requiere un worker aparte.
- Hoy la oficina solo genera texto (guiones, planes) revisado por el CEO.
- No se han clonado ni ejecutado estos repos.


## Oficina virtual 3D (enlaces aportados, SIN verificar)
Referencias para una oficina 3D caminable: DeskRPG, virtual-office, VirtOffice, rockoffice, office-tour, MPFB2, Animate-Rigged-Humanoid, vrm-viewer, three-avatar, talkinghead, human-three-vrm; assets Quaternius, Kenney, Poly Haven, OpenGameArt; base: three.js, react-three-fiber, drei.
Avisos: la licencia del código y la de los assets son distintas; DeskRPG tiene restricciones de uso como servicio gestionado y office-tour licencia privada: NO copiar código sin revisar la licencia. Preferir assets CC0 (Quaternius/Kenney/Poly Haven).
Plan por fases: 1) plano 2D accesible (hecho) con CEO + CIRO en Dirección y coordinación; 2) sala 3D en R3F con GLB humanoide, estados desde las tareas reales; 3) voz/lip-sync; 4) tiempo real. Siempre con el plano 2D como alternativa.

## Licencias verificadas (GitHub API) y uso real
- MIT (se puede reutilizar con aviso): hermes-virtual-office, VirtOffice (OneByJorah), TalkingHead (futuro lip-sync), vrm-viewer.
- Apache-2.0: three.ws.
- NO copiar (sin licencia o NOASSERTION): DeskRPG, rockoffice, office-tour, MPFB2.
- Uso actual: escena 3D original escrita con three.js (src/components/Oficina3D.tsx); de hermes solo se tomaron ideas de distribución. Activos CC0 (Quaternius/Kenney) que ya posees quedan para muebles/personajes GLB futuros.

## Modelos GLB en la escena 3D
- Escritorio, silla, teclado y planta: Kenney Furniture Kit 2.0 (CC0). Copiados en public/oficina/glb/ con su LICENSE. Si no cargan, la escena dibuja cajas.
- Monitor GLB con pantalla que se ilumina por estado real, estanterías y plantas por sala, cabra sentada sobre su silla.
- Pendiente: cabras en 3D (hoy son imágenes 2D de espaldas), agentes caminando, chat y entrega JPG.
