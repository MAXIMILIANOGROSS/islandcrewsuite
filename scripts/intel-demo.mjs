// Ejecución REAL de la Intelligence Network desde la línea de comandos (sin datos de demostración): diagnostica los conectores y lanza la primera investigación.
// Uso: node --experimental-strip-types scripts/intel-demo.mjs [salida.md]
// Variables opcionales: GITHUB_TOKEN, JINA_API_KEY. No imprime secretos.
import { writeFileSync, mkdirSync } from "node:fs";
import { dirname } from "node:path";
import { diagnosticar } from "../src/lib/intel/diagnostico.ts";
import { ejecutarInvestigacion } from "../src/lib/intel/ejecutor.ts";

const env = { GITHUB_TOKEN: process.env.GITHUB_TOKEN, JINA_API_KEY: process.env.JINA_API_KEY };
const diag = await diagnosticar({ env });
console.log("== DIAGNÓSTICO ==");
for (const d of diag) console.log(`${d.plataforma.padEnd(9)} ${d.estado.padEnd(15)} ${d.ms ?? "-"} ms  ${d.mensaje ?? ""}`);
const r = await ejecutarInvestigacion({
  pregunta: "Investiga Agent-Reach y determina cómo podemos utilizarlo para mejorar las capacidades de investigación de Island Crew. Comprueba sus funciones, requisitos, limitaciones y licencia.",
  objetivo: "Decidir cómo integrar Agent-Reach en la oficina virtual", proyecto: "island-crew", agente: "ciro",
  urls: ["https://github.com/Panniantong/Agent-Reach", "https://github.com/Panniantong/Agent-Reach/blob/main/docs/README_en.md", "https://github.com/Panniantong/Agent-Reach/blob/main/docs/install.md", "https://github.com/Panniantong/Agent-Reach/commits/main.atom"],
  profundidad: "normal",
}, { env, diagnostico: async () => diag });
console.log("\n== RESULTADO ==", r.estado, `${r.elementos.length} elementos`, `${r.ms} ms`, r.motivo ?? "");
for (const g of r.registros) console.log(g.ok ? "OK  " : "FALLO", JSON.stringify(g.consulta), g.ok ? g.elementos + " elementos" : g.error);
const out = process.argv[2];
if (out) { mkdirSync(dirname(out), { recursive: true }); writeFileSync(out, r.informe); console.log("Informe guardado en", out); }
process.exit(r.estado === "completada" || r.estado === "parcial" ? 0 : 1);
