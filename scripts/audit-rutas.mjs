// Inventario visual de rutas: captura móvil + fondo dominante + errores de contraste (axe). Uso: node scripts/audit-rutas.mjs [puerto]
import { chromium } from "playwright";
import AxeBuilder from "@axe-core/playwright";
import fs from "node:fs";
import path from "node:path";
const port = process.argv[2] || "3111";
const raiz = "src/app";
const rutas = [];
(function rec(d, pre) {
  for (const e of fs.readdirSync(d, { withFileTypes: true })) {
    if (e.isDirectory()) { if (/^(api|admin|universo-preview)$/.test(e.name) || e.name.startsWith("[") || e.name.startsWith("(")) continue; rec(path.join(d, e.name), pre + "/" + e.name); }
    else if (e.name === "page.tsx") rutas.push(pre || "/");
  }
})(raiz, "");
if (process.env.END) rutas.splice(+process.env.END);
if (process.env.START) rutas.splice(0, +process.env.START);
const salida = process.env.HOME + "/Downloads/audit-rutas";
fs.mkdirSync(salida, { recursive: true });
const b = await chromium.launch();
const c = await b.newContext({ viewport: { width: 390, height: 844 } });
const out = [];
for (const r of rutas) {
  const pg = await c.newPage();
  const corte = setTimeout(() => { pg.close().catch(() => {}); }, 40000);
  try {
    await Promise.race([(async () => {
    await pg.goto(`http://localhost:${port}${r}`, { waitUntil: "domcontentloaded", timeout: 45000 });
    await pg.evaluate(() => { try { localStorage.setItem("ic-age-18", "1"); } catch {} });
    await pg.waitForTimeout(900);
    const bg = await pg.evaluate(() => getComputedStyle(document.body).backgroundColor);
    const ax = process.env.AXE ? await new AxeBuilder({ page: pg }).withRules(["color-contrast"]).analyze() : { violations: [] };
    const fam = bg.match(/\d+/g)?.slice(0, 3).map(Number) ?? [255, 255, 255];
    const lum = (0.2126 * fam[0] + 0.7152 * fam[1] + 0.0722 * fam[2]) / 255;
    out.push({ ruta: r, fondo: lum < 0.35 ? "oscuro" : "claro", contraste: ax.violations.reduce((n, v) => n + v.nodes.length, 0) });
    })(), new Promise((_, rej) => setTimeout(() => rej(new Error('tiempo agotado')), 45000))]);
  } catch (e) { out.push({ ruta: r, error: String(e.message).slice(0, 80) }); }
  clearTimeout(corte);
  await pg.close().catch(() => {});
  fs.writeFileSync(salida + `/inv-${process.env.START || 0}.json`, JSON.stringify(out, null, 1));
  process.stdout.write(`${out.length}/${rutas.length} ${r}\n`);
}
fs.writeFileSync(salida + `/inv-${process.env.START || 0}.json`, JSON.stringify(out, null, 1));
const claras = out.filter((o) => o.fondo === "claro").length, osc = out.filter((o) => o.fondo === "oscuro").length;
console.log(`rutas=${out.length} claras=${claras} oscuras=${osc} errores=${out.filter((o) => o.error).length}`);
await b.close();
