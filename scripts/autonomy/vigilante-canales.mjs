// Vigilante independiente de los canales de marketing. Corre en GitHub Actions (no depende de tu Mac ni de Vercel).
// Lee /api/latido-canales; si hay un canal atrasado/desconectado abre UN incidente (issue) asignado a ti (GitHub te avisa por correo)
// y lo cierra solo cuando el sondeo vuelve a salir sano. Nunca duplica incidentes. Solo avisa por excepción.
export const ETIQUETA = "incidente-canales", TITULO = "Incidente: canales de marketing degradados";

/** Decide qué hacer. Puro y testeable. sondeo: { ok:boolean, estado?:string, canales?:[{canal,estado,horas}] } | null (sin respuesta). */
export function decidir(sondeo, incidenteAbierto) {
  const caido = !sondeo || sondeo.ok === false || sondeo.estado === "degradado";
  if (caido && !incidenteAbierto) return { accion: "abrir", cuerpo: cuerpo(sondeo) };
  if (caido && incidenteAbierto) return { accion: "comentar_si_cambia", cuerpo: cuerpo(sondeo) };
  if (!caido && incidenteAbierto) return { accion: "cerrar", cuerpo: "Verificado: `/api/latido-canales` vuelve a salir sano. Incidente cerrado automáticamente." };
  return { accion: "nada" };
}
export function cuerpo(s) {
  if (!s) return "No hay respuesta de `https://islandcrew.es/api/latido-canales` (el sitio no responde o devuelve un error). Qué comprobar: despliegue en Vercel y estado de la web.";
  const l = (s.canales || []).filter((c) => c.estado !== "ok").map((c) => `- **${c.canal}**: ${c.estado}${c.horas != null ? ` (${c.horas} h sin señal)` : ""}`).join("\n");
  const ayuda = { worker_video: "El worker de vídeo no da señal: ¿Mac apagado o dormido? Al encenderlo se reanuda solo.", youtube: "YouTube sin subidas recientes: ¿token caducado? Repite `node tools/studio-worker/youtube-cli.mjs autorizar`.", instagram: "Instagram sin publicación reciente: revisa en la Oficina la autorización de fotos y el token de Meta." };
  const pistas = (s.canales || []).filter((c) => c.estado !== "ok").map((c) => `- ${ayuda[c.canal] || c.canal}`).join("\n");
  return `Canales con problema:\n${l || "- (sin detalle)"}\n\nQué hacer:\n${pistas}\n\nEste aviso se cierra solo cuando el sondeo vuelva a estar sano.`;
}

async function main() {
  const { GITHUB_TOKEN: tk, GITHUB_REPOSITORY: repo, SITE = "https://islandcrew.es", ASIGNAR = "" } = process.env; if (!tk || !repo) throw new Error("Falta GITHUB_TOKEN o GITHUB_REPOSITORY");
  const gh = (p, init = {}) => fetch(`https://api.github.com/repos/${repo}${p}`, { ...init, headers: { authorization: `Bearer ${tk}`, accept: "application/vnd.github+json", "content-type": "application/json" } });
  let sondeo = null; try { const r = await fetch(`${SITE}/api/latido-canales`, { cache: "no-store", signal: AbortSignal.timeout(20000) }); const j = await r.json().catch(() => null); sondeo = j ? { ...j, ok: r.status === 200 && j.estado !== "degradado" } : null; } catch { sondeo = null; }
  const lista = await (await gh(`/issues?state=open&labels=${ETIQUETA}&per_page=5`)).json(); const abierto = Array.isArray(lista) ? lista[0] : null;
  const d = decidir(sondeo, abierto); console.log("Sondeo:", JSON.stringify(sondeo), "→", d.accion);
  if (d.accion === "abrir") { await gh("/labels", { method: "POST", body: JSON.stringify({ name: ETIQUETA, color: "d93f0b" }) }); const r = await gh("/issues", { method: "POST", body: JSON.stringify({ title: TITULO, body: d.cuerpo, labels: [ETIQUETA], assignees: ASIGNAR ? [ASIGNAR] : [] }) }); if (!r.ok) throw new Error("No se pudo abrir el incidente: " + r.status); }
  else if (d.accion === "comentar_si_cambia" && abierto && !String(abierto.body || "").includes(d.cuerpo.slice(0, 80))) await gh(`/issues/${abierto.number}`, { method: "PATCH", body: JSON.stringify({ body: d.cuerpo }) });
  else if (d.accion === "cerrar" && abierto) { await gh(`/issues/${abierto.number}/comments`, { method: "POST", body: JSON.stringify({ body: d.cuerpo }) }); await gh(`/issues/${abierto.number}`, { method: "PATCH", body: JSON.stringify({ state: "closed", state_reason: "completed" }) }); }
}
if (import.meta.url === `file://${process.argv[1]}`) main().catch((e) => { console.error("✘", e.message); process.exit(1); });
