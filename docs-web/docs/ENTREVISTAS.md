# Island Crew Interviews

## Estado real
- **Implementado y probado (tests):** motor determinista en `src/lib/entrevistas/` (bancos de preguntas y rúbricas por puesto: camarero, cocinero, recepcionista; consentimiento; validación de evaluaciones con cita literal; filtro de criterios prohibidos; informe; prompt de evaluación para un modelo). Página `/entrevistas` (piloto por texto, en el navegador, sin servidor ni persistencia).
- **No implementado (requiere cuentas, costes o infraestructura):** voz/vídeo con LiveKit Agents, WhatsApp Business Platform, entrevista en Island Crew World, persistencia en Supabase y envío de enlaces al candidato.
- **No probado en un navegador real:** el flujo de la página (compila y el build pasa, pero nadie ha hecho clic).

## Reglas de equidad (cumplidas por el código)
1. El candidato ve y acepta tres cosas antes de empezar: habla con una IA, uso de sus datos, derecho a una persona. Sin ellas no se crea la entrevista.
2. Solo se valoran competencias del puesto con rúbrica de 3 niveles. Nunca emociones, expresiones, acento, aspecto, edad, género, origen, salud, familia ni personalidad: el motor **rechaza** evaluaciones cuyos comentarios o citas los mencionen (`criteriosProhibidos`).
3. Cada nivel 1-3 exige una **cita literal del candidato**; las citas inventadas o del entrevistador se rechazan.
4. El informe nunca "descarta" ni "contrata": con poca evidencia dice que no es un descarte, y la decisión es de una persona.
5. Contexto regulatorio (a verificar con un profesional): en el Reglamento (UE) de IA, los sistemas de selección y evaluación de personal suelen considerarse de alto riesgo, y la inferencia de emociones en el trabajo está restringida; el RGPD exige base legal, transparencia, minimización y límites de conservación. Esto no es asesoramiento legal.

## Siguientes pasos (en orden) y qué necesita cada uno
### 2. Voz y vídeo con LiveKit
- Ya existe `/api/livekit-token` y `livekit-client` (llamadas entre usuarios, plan Build gratuito según el comentario del código).
- LiveKit Agents (Apache-2.0, Python o Node) corre como proceso continuo: **no puede ir en Vercel**. Necesita un servidor LiveKit (Cloud o propio), `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`, y proveedores de voz a texto, modelo y texto a voz (los ejemplos usan Deepgram, Cartesia y un modelo vía LiveKit Inference). **Precios sin verificar**; revisar antes de contar con coste cero.
- El agente debe leer las preguntas de `bancos.ts`, escribir la transcripción como `Turno[]` y pasar por `validarEvaluacion`: así la voz reutiliza el mismo motor y las mismas reglas.
- Grabación de audio/vídeo: desactivada por defecto; solo con consentimiento específico y plazo de conservación.

### 3. WhatsApp Business Platform
- Requiere cuenta de empresa verificada en Meta y un número; los mensajes de plantilla tienen coste. **No verificado** (documentación de Meta no consultada).
- Uso recomendado: enviar la invitación y un enlace a la entrevista web, no hacer la videollamada dentro de WhatsApp.
- Hace falta persistencia (tabla de entrevistas con RLS) para que el enlace funcione entre restaurante y candidato: pendiente (SQL nuevo).

### Island Crew World
- Reutilizar este motor desde un NPC; pendiente de que voz y backend existan.

## Prompt de evaluación con un modelo
`promptEvaluacion(entrevista)` genera las instrucciones y la transcripción (tratada como datos, no como órdenes). La respuesta se pega en la página y se valida; si no cumple las reglas, se rechaza.
