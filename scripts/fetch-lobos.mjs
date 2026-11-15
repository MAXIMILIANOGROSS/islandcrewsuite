// Descarga la costa y los senderos de Isla de Lobos desde OpenStreetMap (© colaboradores de OpenStreetMap, ODbL) a public/data/lobos-coast.json.
// Uso:  node scripts/fetch-lobos.mjs
import { writeFileSync } from "node:fs";
const bbox = "28.725,-13.85,28.775,-13.78";
const q = `[out:json][timeout:60];(way["natural"="coastline"](${bbox});way["highway"~"^(path|track|footway|service)$"](28.725,-13.84,28.775,-13.79););out geom;`;
const hosts = ["https://overpass-api.de/api/interpreter", "https://overpass.kumi.systems/api/interpreter", "https://overpass.private.coffee/api/interpreter"];
let data = null;
for (const h of hosts) { try { const r = await fetch(h, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "IslandCrew/1.0 (https://islandcrew.es)" }, body: "data=" + encodeURIComponent(q) }); if (!r.ok) { console.log(h, r.status); continue; } data = await r.json(); break; } catch (e) { console.log(h, String(e)); } }
if (!data) { console.error("No se pudo descargar. Prueba de nuevo en unos minutos."); process.exit(1); }
const g = (w) => w.geometry.map((p) => [Number(p.lat.toFixed(6)), Number(p.lon.toFixed(6))]);
const coast = data.elements.filter((w) => w.tags?.natural === "coastline" && w.geometry).map(g);
const paths = data.elements.filter((w) => w.tags?.highway && w.geometry).map(g);
writeFileSync("public/data/lobos-coast.json", JSON.stringify({ attribution: "© Colaboradores de OpenStreetMap (ODbL)", fetched: new Date().toISOString(), coast, paths }));
console.log("OK · tramos de costa:", coast.length, "· senderos:", paths.length);
