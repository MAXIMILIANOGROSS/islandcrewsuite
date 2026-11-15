// Ejecutor de ingeniería autónoma (corre en GitHub Actions, sin credenciales de producción).
// Uso: TAREA, OBJETIVO, ARCHIVOS (separados por coma) en el entorno. LLM_BASE_URL, LLM_API_KEY y LLM_MODEL para el modelo (cualquier proveedor compatible; el gratuito sirve).
// Flags: --solo-parche (no ejecuta tsc/tests) · --simulado <archivo.json> (usa esa respuesta en lugar del modelo; para pruebas).
import { readFileSync, writeFileSync, existsSync, lstatSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { spawnSync } from "node:child_process";
const { validarParche, extraerJson, rutaSegura } = await import("../../src/lib/autonomia-codigo/parche.ts");
const { nivelCambio } = await import("../../src/lib/ingenieria/riesgo.ts");
const args = process.argv.slice(2); const flag = (n) => args.includes(n); const val = (n) => { const i = args.indexOf(n); return i >= 0 ? args[i + 1] : undefined; };
const tarea = String(process.env.TAREA || "").replace(/[^\w.-]/g, "").slice(0, 60), objetivo = String(process.env.OBJETIVO || "").slice(0, 1500);
const archivos = String(process.env.ARCHIVOS || "").split(",").map((s) => s.trim()).filter(Boolean).slice(0, 5);
const salida = (o) => { writeFileSync(process.env.RESUMEN_PATH || "autonomia-resumen.json", JSON.stringify(o, null, 1)); console.log(JSON.stringify(o)); };
const falla = (estado, motivo, extra = {}) => { salida({ estado, motivo, tarea, ...extra }); process.exit(1); };
if (!tarea) falla("bloqueada", "Falta el identificador de la tarea."); if (!objetivo) falla("bloqueada", "Falta el objetivo.");
const contexto = [];
for (const a of archivos) { const s = rutaSegura(a); if (!s.ok) falla("bloqueada", `Archivo de contexto no permitido (${a}): ${s.motivo}`); if (!existsSync(a) || lstatSync(a).isSymbolicLink()) falla("bloqueada", `El archivo ${a} no existe o es un enlace simbólico.`); contexto.push({ ruta: a, contenido: readFileSync(a, "utf8").slice(0, 20000) }); }
const sistema = `Eres un ingeniero de software que modifica la web de Island Crew (Next.js 15, TypeScript). Devuelve SOLO un objeto JSON: {"resumen": string, "cambios": [{"ruta": string, "contenido": string}]}. "contenido" es el archivo COMPLETO ya modificado. Reglas: máximo 5 archivos; solo rutas bajo src/, tests/ o docs/; no toques SQL, workflows, autenticación ni secretos; cambio mínimo y reversible; español de España (tuteo) en los textos; no inventes datos.`;
async function pedir(extra) {
  if (val("--simulado")) return readFileSync(val("--simulado"), "utf8");
  const limpiar = (v) => String(v || "").trim().replace(/^["']+|["']+$/g, "").trim();
  const base = limpiar(process.env.LLM_BASE_URL), key = limpiar(process.env.LLM_API_KEY), modelo = limpiar(process.env.LLM_MODEL);
  if (!base || !key || !modelo) falla("bloqueada", "Falta configurar el modelo: LLM_BASE_URL, LLM_API_KEY y LLM_MODEL (secretos de GitHub).");
  if (!/^https:\/\/[^\s/]+/.test(base)) falla("bloqueada", `LLM_BASE_URL no es una dirección válida: debe empezar por https:// (ahora tiene ${base.length} caracteres y empieza por "${base.slice(0, 4)}"). Corrígelo en los secretos de GitHub.`);
  const r = await fetch(`${base.replace(/\/+$/, "")}/chat/completions`, { method: "POST", signal: AbortSignal.timeout(120000), headers: { "content-type": "application/json", authorization: `Bearer ${key}` },
    body: JSON.stringify({ model: modelo, max_tokens: 6000, temperature: 0.2, messages: [{ role: "system", content: sistema }, { role: "user", content: `Objetivo:\n${objetivo}\n\nArchivos de contexto:\n${contexto.map((c) => `--- ${c.ruta} ---\n${c.contenido}`).join("\n\n")}${extra ? `\n\nTu intento anterior falló:\n${extra}\nCorrígelo.` : ""}` }] }) });
  if (!r.ok) { const cuerpo = String(await r.text().catch(() => "")).replace(/(sk-|gsk_|ghp_|github_pat_)[A-Za-z0-9_-]{8,}/g, "***").replace(/\s+/g, " ").slice(0, 220); falla("fallida", `El modelo respondió ${r.status} (modelo «${modelo}», servidor ${new URL(base).host}).${cuerpo ? ` Detalle: ${cuerpo}` : ""}`); } const j = await r.json(); return String(j?.choices?.[0]?.message?.content || "");
}
const ejecutar = (cmd, argv) => { const r = spawnSync(cmd, argv, { encoding: "utf8", timeout: 600000, maxBuffer: 20 * 1024 * 1024 }); return { ok: r.status === 0, cola: ((r.stdout || "") + (r.stderr || "")).slice(-3000) }; };
let fallo = ""; let aplicados = [];
for (let intento = 1; intento <= 2; intento++) { // límite de iteraciones: 2 intentos
  const bruto = await pedir(fallo); const json = extraerJson(bruto); if (!json) { fallo = "La respuesta no era JSON válido."; continue; }
  const v = validarParche(json.cambios); if (!v.ok) { fallo = v.errores.join("\n"); continue; }
  for (const c of v.cambios) { const dir = dirname(c.ruta); if (dir && !existsSync(dir)) mkdirSync(dir, { recursive: true }); if (existsSync(c.ruta) && lstatSync(c.ruta).isSymbolicLink()) falla("bloqueada", `${c.ruta} es un enlace simbólico.`); writeFileSync(c.ruta, c.contenido); }
  aplicados = v.cambios.map((c) => c.ruta);
  if (flag("--solo-parche")) { const n = nivelCambio(aplicados); salida({ estado: "parche_aplicado", tarea, resumen: String(json.resumen || "").slice(0, 400), archivos: aplicados, riesgo: n.nivel, intento }); process.exit(0); }
  const tsc = ejecutar("npx", ["tsc", "--noEmit"]); if (!tsc.ok) { fallo = "tsc falló:\n" + tsc.cola; continue; }
  const tst = ejecutar("npm", ["test"]); if (!tst.ok) { fallo = "Los tests fallaron:\n" + tst.cola; continue; }
  const n = nivelCambio(aplicados); salida({ estado: "listo_para_pr", tarea, resumen: String(json.resumen || "").slice(0, 400), archivos: aplicados, riesgo: n.nivel, intento, pruebas: "tsc y npm test en verde" }); process.exit(0);
}
falla("fallida", "No se obtuvo un cambio válido tras 2 intentos.", { ultimoError: fallo.slice(0, 1500), archivosTocados: aplicados });
