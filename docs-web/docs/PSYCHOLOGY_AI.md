# Island Crew · Acompañantes de bienestar (Psychology AI 2.0) — estado real

Actualizado: 2026-10-09. Este documento solo recoge lo implementado y verificado; lo demás figura como pendiente.

## Qué existe
- **8 acompañantes** (`src/lib/soul/companions.ts`): escucha, autoconocimiento, estrés, trabajo, límites, decisiones, hábitos, reflexión profunda. Un solo motor; cada uno con método, tono, límites, herramientas, derivación y banco de preguntas propios. 12 principios comunes en todos los prompts.
- **Catálogo y coordinador** (`catalog.ts`): taxonomía de 20 dominios con capacidad objetivo de 2.000 perfiles. **Hoy hay 12 perfiles definidos, todos en estado `propuesto`, sin revisor profesional.** No hay 2.000 agentes ni profesionales titulados. El coordinador elige 1 perfil principal + hasta 2 de apoyo y construye **un único prompt** (1 llamada al modelo por mensaje, sin recursión). Con salud/medicación/diagnóstico el perfil de orientación profesional pasa a principal. Modo «Elegir por mí» o acompañante fijo.
- **Conocimiento** (`knowledge.ts`): 13 documentos **originales de Island Crew en borrador**, sin fuentes externas ni revisión profesional (evidencia: educativo-general). Recuperación léxica simple. No hay citas científicas: pendiente construir la biblioteca con fuentes verificables y licencias.
- **Seguridad**: detección de crisis (112 / 024 / 016) antes de llamar al modelo; filtro de salida (`safety.ts`) que descarta diagnósticos, promesas de cura, «soy tu psicólogo» y órdenes sobre medicación; el texto del usuario se trata como datos.
- **Voces** (`voices.ts`, `audio.ts`): voces reales en español del dispositivo (Web Speech), muestra, estilo (5), velocidad, pausa/parada. No se clasifica el género. Marca las que requieren conexión. **No hay proveedor de voz de pago ni audios pregrabados**: la arquitectura admite añadirlos, no están hechos.
- **Música y sonidos** (`mix.ts`, `audio.ts`): olas, lluvia, viento (sintéticos), colchón, cuencos y notas (sintéticos). Volúmenes independientes de voz/música/naturaleza, bajada automática mientras habla la voz, temporizador y fundidos. No hay grabaciones reales ni sonidos nocturnos/piano real. Nunca arranca solo.
- **Memoria** (`companionMemory.ts`): `ic_companion_v1` en localStorage (NO cifrado), modos sin memoria / básica / con objetivos, visible, editable y borrable. La conversación no se guarda.
- **Ruta** `/api/life-listen`: acepta acompañante + contexto autorizado, límite 30 mensajes/10 min por IP (en memoria del servidor), salida filtrada, sin registrar contenido.

## Verificado
Tests automáticos (`npm test`): catálogo, coordinador, voces, mezcla, memoria, filtro de seguridad, 9 conversaciones representativas a nivel de prompt/respaldo/crisis. Prueba en navegador simulado: selector, memoria, envío, borrado, crisis.

## NO verificado / pendiente
- Calidad de las respuestas reales del modelo (requiere revisión humana con el proveedor configurado).
- Voces y sonido reales en Chrome/Safari/Android/iOS; latencia.
- `npm run build` de producción (lo ejecuta Vercel).
- Revisión de contenidos clínicos y de seguridad por profesionales habilitados antes de presentarlo como servicio de salud mental. Evaluación jurídica (RGPD, datos sensibles) pendiente.
- Voces de proveedor externo, audios pregrabados, biblioteca con fuentes y licencias, inglés/italiano, sonidos nocturnos y piano.

## Costes operativos (estimación cualitativa)
Una llamada al LLM por mensaje (máx. 380 tokens de salida, 8 mensajes de contexto). El coste real depende del proveedor configurado (`LLM_BASE_URL`/`ANTHROPIC_API_KEY`); no se han medido cifras. Voz y sonido: coste cero (en el navegador).
