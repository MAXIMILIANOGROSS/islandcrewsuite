// Puerta de riesgo para pull requests. Uso: node --experimental-strip-types scripts/riesgo-cambio.mjs <base> [etiquetas separadas por coma]
import { execSync } from "node:child_process";
const { nivelCambio, politicaDespliegue } = await import("../src/lib/ingenieria/riesgo.ts");
const base = process.argv[2] || "origin/main"; const etiquetas = (process.argv[3] || "").split(",").map((s) => s.trim()).filter(Boolean);
const archivos = execSync(`git diff --name-only ${base}...HEAD`, { encoding: "utf8" }).split("\n").filter(Boolean);
const { nivel, porArchivo } = nivelCambio(archivos); const d = politicaDespliegue(nivel, true, etiquetas);
console.log(`Riesgo del cambio: ${nivel.toUpperCase()} (${archivos.length} archivos)`); for (const [f, n] of Object.entries(porArchivo)) if (n !== "bajo") console.log(`  ${n}: ${f}`);
console.log(d.puede ? `OK · ${d.motivo}` : `BLOQUEADO · ${d.motivo}`); process.exit(d.puede ? 0 : 1);
