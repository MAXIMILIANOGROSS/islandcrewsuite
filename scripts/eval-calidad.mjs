// Banco de pruebas de calidad de la IA de las cabras. Ejecuta las rutinas REALES contra tu proveedor de IA y puntúa cada informe con reglas objetivas.
// Uso (con tus claves LLM_* en el entorno):
//   node --experimental-strip-types scripts/eval-calidad.mjs                      → mide y muestra la puntuación
//   node --experimental-strip-types scripts/eval-calidad.mjs --guardar            → guarda la línea base en evals/baseline.json
//   node --experimental-strip-types scripts/eval-calidad.mjs --comparar           → compara con evals/baseline.json (falla si EMPEORA)
//   node --experimental-strip-types scripts/eval-calidad.mjs --simulado           → prueba el propio banco sin llamar a la IA
import { register } from "node:module";
import { readFileSync, writeFileSync, existsSync } from "node:fs";
register("../tests/helpers/alias-loader.mjs", import.meta.url);
const { callLLM, llmProvider } = await import("../src/lib/llm.ts");
const { analizarLeads, promptLeads } = await import("../src/lib/oficina/leadsAnalisis.ts");
const { embudoLeads } = await import("../src/lib/oficina/embudoLeads.ts");
const { evaluarInforme, promptReparacion } = await import("../src/lib/oficina/calidad.ts");
const { agentePorId, promptDe } = await import("../src/lib/oficina/agentes.ts");
const { RUTINAS } = await import("../src/lib/oficina/rutinas.ts");

const args = new Set(process.argv.slice(2)); const SIM = args.has("--simulado"); const BASE = new URL("../evals/baseline.json", import.meta.url);
const NOW = Date.parse("2026-10-26T10:00:00Z"); const L = (type, status, d, payload = {}) => ({ id: `${type}-${d}-${Math.random().toString(16).slice(2, 10)}`, type, status, score: null, created_at: d + "T10:00:00Z", payload: { name: "Anónimo", email: `x${Math.random().toString(16).slice(2, 6)}@ejemplo.com`, ...payload } });
// Conjuntos de datos sintéticos con la forma de los reales (sin datos personales verdaderos).
const CASOS = [
  { id: "leads-forma-real", tipo: "leads", leads: [...Array(3)].map((_, i) => L("business", "nuevo", "2026-10-0" + (2 + (i % 2)))).concat([...Array(7)].map(() => L("relocation", "nuevo", "2026-10-01")), [...Array(9)].map((_, i) => L("worker", "nuevo", i === 8 ? "2026-10-24" : "2026-10-01"))) },
  { id: "leads-vacio", tipo: "leads", leads: [] },
  { id: "leads-trabajados-con-duplicados", tipo: "leads", leads: [L("business", "contactado", "2026-10-20", { email: "dup@ejemplo.com" }), L("business", "nuevo", "2026-10-21", { email: "dup@ejemplo.com" }), L("worker", "propuesta", "2026-10-22"), L("worker", "nuevo", "2026-10-25", { name: "" }), L("business", "cliente", "2026-10-10")] },
];
const ag = agentePorId("cre-analitica");
const BUENO = (an) => `## Resumen\nHay ${an.total} leads registrados y ${an.ultimos7dias} en los últimos 7 días.\n\n## Problemas de datos\nSe revisan los datos incompletos y los duplicados detectados por el sistema.\n\n## Oportunidades de seguimiento\nLas empresas sin contactar son la oportunidad principal del embudo actual.\n\n## Prioridad comercial\nLas empresas son quienes pagan: se contactan primero, de más antigua a más reciente.\n\n## Recomendaciones\nPrimera, contactar empresas. Segunda, registrar el estado de cada lead. Tercera, revisar la captación.`;

async function generar(caso) {
  const an = { ...analizarLeads(caso.leads, NOW), embudo: embudoLeads(caso.leads, NOW) };
  const bloque = "\n\n## Datos calculados por el sistema\n```json\n" + JSON.stringify(an, null, 1) + "\n```";
  const llm = SIM ? async () => BUENO(an) : callLLM;
  const sys = promptLeads(promptDe(ag), an); const t0 = Date.now();
  const r1 = ((await llm(sys, [{ role: "user", content: RUTINAS[0].instruccion("2026-10-26") }], 1400)) || "").trim();
  const t1 = Date.now() - t0; const q1 = evaluarInforme("leads", r1 + bloque, { datos: an }); let q = q1;
  if (!q1.aprobado) { const r2 = ((await llm(sys, [{ role: "user", content: RUTINAS[0].instruccion("2026-10-26") }, { role: "assistant", content: r1 }, { role: "user", content: promptReparacion(q1.fallos) }], 1400)) || "").trim(); const q2 = evaluarInforme("leads", r2 + bloque, { datos: an }); if (q2.puntos >= q1.puntos) q = q2; }
  return { caso: caso.id, primerIntento: q1.puntos, final: q.puntos, aprobado: q.aprobado, fallosPrimero: q1.fallos, fallosFinal: q.fallos, ms: t1, chars: r1.length };
}

if (!SIM && !llmProvider()) { console.error("No hay proveedor de IA: define LLM_BASE_URL, LLM_API_KEY y LLM_MODEL (o ANTHROPIC_API_KEY)."); process.exit(2); }
const res = []; for (const c of CASOS) { process.stdout.write(`· ${c.id} … `); const r = await generar(c); res.push(r); console.log(`primer intento ${r.primerIntento}/100 → final ${r.final}/100 ${r.aprobado ? "✔" : "✘ " + r.fallosFinal.join("; ")} (${r.ms} ms)`); }
const vacios = res.filter((r) => r.chars === 0);
if (!SIM && vacios.length) { console.error(`\n✘ El proveedor de IA no devolvió texto en ${vacios.length}/${res.length} casos (¿LLM_BASE_URL, LLM_API_KEY o LLM_MODEL con valores de ejemplo como "..."?). Esto NO mide la calidad: no se guarda ni se compara nada.`); process.exit(3); }
const media = (k) => Math.round(res.reduce((s, r) => s + r[k], 0) / res.length);
const resumen = { fecha: new Date().toISOString(), simulado: SIM, modelo: process.env.LLM_MODEL || process.env.COUNCIL_MODEL || "?", mediaPrimerIntento: media("primerIntento"), mediaFinal: media("final"), aprobados: res.filter((r) => r.aprobado).length, total: res.length, casos: res };
console.log(`\nMedia primer intento: ${resumen.mediaPrimerIntento}/100 · media final (con reparación): ${resumen.mediaFinal}/100 · informes que superan el control: ${resumen.aprobados}/${resumen.total}`);
if (args.has("--guardar")) { if (SIM && existsSync(BASE) === false) { /* permitido para probar el banco */ } writeFileSync(BASE, JSON.stringify(resumen, null, 2)); console.log("Línea base guardada en evals/baseline.json"); }
if (args.has("--comparar")) {
  if (!existsSync(BASE)) { console.error("No existe evals/baseline.json: ejecuta antes con --guardar."); process.exit(2); }
  const b = JSON.parse(readFileSync(BASE, "utf8")); if (b.simulado || (b.casos || []).some((c) => c.chars === 0) || b.modelo === "...") { console.error("La línea base guardada no es válida (simulada o con respuestas vacías). Bórrala o sobrescríbela con --guardar usando tus claves LLM_* reales."); process.exit(2); } if (false) { console.error("La línea base guardada es SIMULADA (no mide tu IA). Ejecuta una vez --guardar con tus claves LLM_* para crear la real."); process.exit(2); } const d1 = resumen.mediaPrimerIntento - b.mediaPrimerIntento, d2 = resumen.mediaFinal - b.mediaFinal, d3 = resumen.aprobados - b.aprobados;
  console.log(`Frente a la línea base (${b.fecha.slice(0, 10)}, ${b.modelo}): primer intento ${d1 >= 0 ? "+" : ""}${d1} · final ${d2 >= 0 ? "+" : ""}${d2} · aprobados ${d3 >= 0 ? "+" : ""}${d3}`);
  if (d2 < 0 || d3 < 0) { console.error("✘ LA CALIDAD HA EMPEORADO: no promociones este cambio."); process.exit(1); } console.log("✔ No empeora.");
}
