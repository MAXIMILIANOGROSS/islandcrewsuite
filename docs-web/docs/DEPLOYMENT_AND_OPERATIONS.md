# DEPLOYMENT AND OPERATIONS

- **Despliegue**: Vercel (plan Hobby) con autodeploy al hacer `git push` a `main`. Dominio islandcrew.es. Sin `vercel.json` ni GitHub Actions.
- **Migraciones**: manuales. Cada `TODO_CORRER_NN_*.sql` se pega en una pestaña vacía del SQL Editor de Supabase, en orden. Pendientes de confirmar en producción: 63, 64, 65, 66.
- **Scheduler**: NINGUNO desplegado. El informe diario y el ciclo de agentes no se ejecutan solos. El ciclo automático está bloqueado hasta que el fundador escriba la frase de activación acordada. Un proceso recurrente real necesita un worker/cron en infraestructura activa (p. ej. Vercel Cron o Supabase pg_cron), con registro de ejecuciones y parada.
- **Plan gratuito de Supabase**: 500 MB de base de datos, 1 GB de archivos, 5 GB de transferencia; los proyectos se pausan tras una semana sin actividad (fuente en `docs/CHAT_ECOSISTEMA_REPOS.md`).
- **Observabilidad y copias**: no configuradas en el repositorio (pendiente: copias de seguridad de Supabase y alertas de error).
- **Comprobaciones**: `node --experimental-strip-types --test tests/*.test.mjs`; `npx tsc --noEmit -p .`; abrir `https://islandcrew.es/mundo/vista` y `/mundo/downtown`.
