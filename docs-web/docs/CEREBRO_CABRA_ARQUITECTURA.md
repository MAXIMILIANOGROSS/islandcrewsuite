# Cerebro de La Cabra: decisión de arquitectura

## Decisión
Pila mínima, sin dependencias nuevas: **Supabase Postgres + RLS** (tablas `goat_memories`, `goat_memory_settings`), un único endpoint (`/api/goat-chat`) que usan todas las cabras, y funciones puras en `src/lib/goat/memoria.ts`. Voz: Web Speech API + speechSynthesis del navegador (coste cero).

## Repositorios candidatos evaluados (no instalados; licencias a verificar antes de adoptar)
- mem0, Letta, LangMem, Graphiti, LangChain/LangGraph: ideas útiles (memoria episódica/semántica, resolución de contradicciones) pero añaden servicios y un segundo sistema de memoria. **Rechazados por ahora**; se replicó la idea mínima (dedupe + sustitución por clave).
- pgvector: **diferido**. Con <40 memorias por persona, recuperación por recencia basta; se añade cuando haya volumen.
- NeMo Guardrails / Guardrails AI / Langfuse: diferidos (requieren infraestructura). Capa de seguridad actual: `detectCrisis` + `guardReply` previos al modelo, no desactivables.
- EmpatheticDialogues / conv-emotion: datasets/modelos de investigación; no se incorporan (inferir emociones por modelo contradice "no inferir").

## Principios implementados
Consentimiento (memoria básica por defecto; memoria emocional OFF hasta que la actives, caduca en 14 días), solo lo que la persona dice (`source=declarado`), filtro de categorías sensibles, anti-inyección (no se guarda ni obedece), ver/corregir/olvidar/exportar, aislamiento por usuario (RLS), nunca compartido con empresas, la memoria entra al prompt como DATOS.

## Despliegue
Ejecutar `supabase/migrations/20261015000100_goat_memory.sql`. Rollback: `drop table goat_memories, goat_memory_settings;` (el chat sigue funcionando sin ellas).

## Límites honestos
Extracción por reglas (cubre frases comunes, no todo). Voz del navegador: la calidad depende del dispositivo (Chrome envía audio a Google para reconocer). Voces neuronales de proveedor (ElevenLabs/Azure) requieren coste y aviso RGPD: no incluidas. Astrología/ikigai/neurotransmisores: sin cambios, siguen simbólicos y opcionales. CabraVida, AiFaqChat y la home usan la memoria; CompanionChat (/vida) NO la usa a propósito: un test de privacidad prohíbe que Life importe cuentas; Life es privado y sin cuenta.

## Fase 2 (Island Crew 2050/2100): datos reales y Trust Protocol
- `src/lib/goat/herramientas.ts` + `consultas.ts`: clasificación de la petición y consultas REALES. Empleo = función pública `jobs_list` (abierta, negocio verificado, revisada ≤60 días, <3 denuncias); el recuento suma todas las páginas. Marketplace = `market_items` con la sesión de la persona (RLS: solo miembros), disponible = `published` y no caducado. Respuesta determinista: ninguna cifra sale del modelo; si la consulta falla, se dice y no se da número. Texto de anuncios/ofertas se limpia (no puede inyectar enlaces ni instrucciones).
- `tareas.ts` + migración `20261015000300_goat_tasks.sql`: estados PROPOSED → AWAITING_APPROVAL → APPROVED → EXECUTING → COMPLETED/FAILED/CANCELLED, con trigger SQL que impide saltarse la aprobación y completar sin confirmación. AÚN NO conectado a acciones reales (no hay envío de candidaturas por la cabra).
- `/confianza`: centro público de transparencia (solo describe lo que existe).
- Pendiente: contexto entre turnos ("enséñame los más baratos"), ubicación autorizada, tarjetas visuales con imagen, preparar/enviar candidatura con aprobación (`jobs_apply` existe), observabilidad (Langfuse/OTel) sin contenido de conversaciones, pruebas de aislamiento contra Supabase real, voz con proveedor de pago, Island Twin, Passport/credenciales, Academia, sello Empleo Transparente.
