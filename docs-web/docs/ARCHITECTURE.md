# ARCHITECTURE (resumen verificado)

- **Cliente**: Next.js 15 (App Router) + React 18. Mundo en Three.js (sin motor externo; no hay proyecto Unreal en este repositorio).
- **Backend**: Supabase (Postgres + Auth + Realtime + Storage). La lógica sensible vive en funciones SQL `security definer` con RLS cerrada y `search_path` fijo; el cliente solo llama a RPC.
- **Rutas API**: 24 en `src/app/api` (IA, CV, notificaciones, NPC, agentes) para lo que necesita secretos de servidor.
- **Mensajería (única)**: tablas `net_*` (SQL 53/54/58/59/65/66). No se despliega ningún chat externo: ver `docs/CHAT_ECOSISTEMA_REPOS.md`.
- **Mundo → jugadores en vivo**: Supabase Realtime Broadcast, canal `world:fuerteventura`, solo coordenadas del juego. La posición GPS no sale del dispositivo; solo se guarda la última posición redondeada (SQL 64).
- **IA**: capa `src/lib/llm.ts` (proveedor configurable por `LLM_BASE_URL`/`LLM_MODEL`); WebLLM local en navegador para algunos usos. Agent OS con catálogo de 400 agentes, cola y aprobación humana (SQL 60–62).
- **Estructura de mundo objetivo**: World → Destination → Area → Location → Business → NPC/Player. Hoy los lugares del juego y `business_accounts` son tablas separadas (deuda registrada en `UNIVERSO_INVENTARIO.md`).
