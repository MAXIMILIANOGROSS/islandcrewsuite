// Descarga los números de portal reales (OpenStreetMap, ODbL) de Corralejo → public/data/corralejo-housenumbers.json
import { writeFileSync } from "node:fs";
const BB = "28.700,-13.900,28.760,-13.840";
const HOSTS = ["https://overpass.kumi.systems/api/interpreter", "https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter"];
const sleep = (ms) => new Promise((ok) => setTimeout(ok, ms));
const q = `[out:json][timeout:120];(node["addr:housenumber"](${BB});way["addr:housenumber"](${BB}););out center tags;`;
let els, err;
for (let i = 0; i < 12 && !els; i++) {
  try { const r = await fetch(HOSTS[i % HOSTS.length], { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "island-crew-web/1.0 (fetch-housenumbers)", Accept: "application/json" }, body: "data=" + encodeURIComponent(q) }); if (r.ok) els = (await r.json()).elements; else err = r.status; } catch (e) { err = String(e); }
  if (!els) await sleep(8000);
}
if (!els) throw new Error("Overpass no responde: " + err);
const out = els.map((e) => ({ n: String(e.tags["addr:housenumber"]).slice(0, 8), s: e.tags["addr:street"] || "", lat: e.lat ?? e.center?.lat, lon: e.lon ?? e.center?.lon })).filter((x) => x.lat && x.lon);
writeFileSync("public/data/corralejo-housenumbers.json", JSON.stringify(out));
console.log("portales:", out.length, "con calle:", out.filter((x) => x.s).length);
