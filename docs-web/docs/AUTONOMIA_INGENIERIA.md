# Ingeniería autónoma (código)

Flujo: workflow manual "Ingeniería autónoma" → `scripts/autonomy/run-task.mjs` pide un parche al modelo (LLM_*) → reglas deterministas (`src/lib/autonomia-codigo/parche.ts`) → `tsc` + `npm test` → rama + Pull Request. **Nunca fusiona ni despliega**: una persona revisa el PR y Vercel despliega al fusionar.

## Configuración (una vez)
1. GitHub → Settings → Secrets and variables → Actions: `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` (cualquier proveedor compatible con OpenAI; uno gratuito sirve).
2. Settings → Actions → General → "Allow GitHub Actions to create and approve pull requests".
3. Etiquetas: `riesgo-bajo`, `riesgo-medio`, `riesgo-alto`, `revisado`, `aprobado-por-direccion`.
4. Protección de `main`: checks obligatorios + revisión humana.

## Límites
Máx. 5 archivos y 40 KB; solo `src/`, `tests/`, `docs/`; nada de SQL, workflows, auth, secretos ni `src/lib/ingenieria/`. 2 intentos. Los PR creados con GITHUB_TOKEN no lanzan otros workflows: ejecuta los checks a mano o usa una GitHub App más adelante.

## Latido independiente del cron de GitHub
`GET https://islandcrew.es/api/latido` es público y mínimo (`estado` y `minutos`). Devuelve 503 si el último ciclo real tiene más de 45 min o no hay ninguno; 200 si está al día o la oficina está detenida a propósito. Añádelo en un monitor gratuito (p. ej. UptimeRobot, intervalo de 5 min) con aviso por correo: así te enteras aunque GitHub Actions falle. Para ciclos más frecuentes que los 15 min de GitHub, un cron gratuito externo (p. ej. cron-job.org) puede hacer `POST /api/oficina/ciclo` con la cabecera `Authorization: Bearer <CRON_SECRET>`; el cerrojo de `office_ciclos` evita ciclos duplicados.

## Despacho desde la oficina (sin entrar en GitHub)
En Oficina → Motor de evolución puedes encargar un cambio de código. Al aprobarlo, el servidor lanza el workflow con `GITHUB_DISPATCH_TOKEN`; cuando aparece el Pull Request lo enlaza, y "Aprobar y desplegar" lo fusiona (squash) solo si ningún archivo es de riesgo alto. Vercel despliega al fusionar. Variable nueva en Vercel: `GITHUB_DISPATCH_TOKEN` (token fine-grained del repo con permisos Actions: Read and write, Pull requests: Read and write, Contents: Read and write). Opcional: `GITHUB_REPO` (por defecto MAXIMILIANOGROSS/island-crew-web).

## Despacho automático (el ciclo inicia el trabajo)
Cada ciclo de la oficina sincroniza el mapa de módulos; por cada página nueva, de baja sensibilidad y sin analítica, crea una tarea de código estable (`inst-…`, sin duplicados) y la lanza sola en GitHub. Límites duros: 1 cambio en curso y 3 al día; se frena con la parada de emergencia o el apagado automático. Cada ciclo también sigue los Pull Requests ya lanzados (los enlaza, detecta fusiones y marca como fallidos los que no producen nada en 40 min). **Solo se genera el Pull Request: fusionarlo y desplegarlo lo decides tú en Oficina → Motor de evolución.** Pendiente: callbacks de fin de workflow (hoy se consulta por sondeo), verificación post-despliegue y rollback.

## Verificación de producción tras fusionar
Cuando un cambio de código se fusiona, el ciclo espera 5 min y comprueba la web real (`/`, `/academy`, `/api/latido` con JSON, y que `/api/oficina/motor-evolucion` siga protegida con 401/403). Si todo responde, queda registrado en la mejora. Si falla, **el motor se pausa** (no más cambios) y se pide intervención: no revierte solo, porque no hay reversión automática segura. Limitación: no comprueba que el commit desplegado sea exactamente el fusionado (haría falta la API de Vercel).

## Solución de problemas (errores reales vistos)
- **"GitHub respondió 403 al lanzar el workflow"**: el token de `GITHUB_DISPATCH_TOKEN` no tiene Actions/Contents/Pull requests en *Read and write* o no incluye el repo. Cambiar permisos en un token existente no cambia su valor: no hace falta tocar Vercel.
- **Run en rojo en "Proponer, validar y probar el cambio" con `Invalid URL`**: `LLM_BASE_URL` (secreto de **GitHub**, pestaña Repository secrets, no el de Vercel) no empieza por `https://`. El ejecutor limpia espacios y comillas y avisa con un mensaje claro. Ejemplo válido: `https://api.groq.com/openai/v1`.
- **No aparece ningún run nuevo tras "Aprobar y lanzar"**: mirar el mensaje bajo el botón en la Oficina; un 401/403/404 viene de GitHub. No uses "Re-run" en GitHub: reutiliza la configuración antigua.
- **Tarea "Aprobada" sin PR**: a los 40 min sin Pull Request el ciclo la marca como fallida.

## Recuperación manual (no hay reversión automática)
Si la verificación de producción falla y el motor se pausa:
1. Mira en Vercel → Deployments cuál es el despliegue anterior sano.
2. Pulsa "Promote to Production" en ese despliegue (restaura sin tocar git), o en GitHub usa "Revert" en el PR fusionado y deja que Vercel despliegue.
3. Comprueba `/`, `/academy` y `/api/latido`.
4. Reanuda el motor desde Oficina → Motor de evolución solo cuando todo responda.

## Qué está verificado y qué no
- Implementado y probado en local (tests con simulaciones): política, límites, despacho, seguimiento de PR, fusión segura, verificación y pausa.
- Probado contra servicios reales: el despacho llega a GitHub y el workflow arranca. Pendiente de confirmar de punta a punta: PR real, fusión, despliegue y verificación en producción.
- Sin verificar: identidad del commit desplegado (sin API de Vercel), avisos fuera del panel, callbacks de fin de workflow, programador de un minuto.

## Diagnóstico automático de ejecuciones (sin copiar logs)
Mientras una tarea de código no tiene Pull Request, cada sincronización consulta la API de GitHub (mismo `GITHUB_DISPATCH_TOKEN`, permiso Actions) y localiza la ejecución lanzada para esa tarea. Si sigue en curso lo indica; si falló, la tarea pasa a **fallida** con el paso que falló y las últimas líneas de su log (sin tokens ni colores), que se ven en Oficina → Motor de evolución. Si termina bien pero no aparece PR en 40 min, también falla. Estado: implementado y probado con simulaciones; pendiente de verificar contra un run real.

## Herramientas de calidad y seguridad (gratuitas, informativas)
- **Semgrep** (`.github/workflows/semgrep.yml`): análisis estático en cada PR y push a `main`. Hoy es informativo (avisa, no bloquea). Pasará a obligatorio cuando el CI esté estable y se hayan revisado los hallazgos iniciales.
- **Renovate** (`renovate.json`): propone actualizaciones de dependencias en PR agrupados, los lunes antes de las 8:00 (hora de Canarias), máx. 3 abiertos; las versiones mayores esperan tu aprobación en el panel de dependencias. **Para activarlo hay que instalar la app de Renovate en el repositorio** (https://github.com/apps/renovate, gratis); hasta entonces el archivo no hace nada. Estado: configurado, sin verificar contra servicio real.

Prueba end-to-end del ciclo autónomo (2026-10-28)
Prueba end-to-end del ciclo autónomo (2026-10-28)
## Control de canales de marketing (Instagram y Shorts)
`GET https://islandcrew.es/api/latido-canales` es público y mínimo (estado por canal y horas sin señal). Devuelve 503 si el worker de vídeo del Mac o la subida a YouTube llevan más de 1,5 h sin latido, o si Instagram lleva más de 36 h sin publicar (o nunca ha publicado). Un canal que desconectes tú no cuenta como caída. Añádelo a UptimeRobot (monitor HTTP, intervalo de 5 min) con aviso por correo y por la app móvil, gratis. Limitaciones reales: no comprueba que cada día se suban exactamente 4 Shorts (el worker corre en un Mac que debe estar encendido y despierto), ni cuándo caduca el token de Meta. Estado: implementado y probado con simulaciones; sin verificar contra datos reales.

Prueba end-to-end del ciclo autónomo (2026-10-28)
Prueba end-to-end del ciclo autónomo (2026-10-28)
Prueba end-to-end del ciclo autónomo (2026-10-28)