// Descarga de OpenStreetMap (Overpass, ODbL) los pueblos de Fuerteventura para Island Crew World.
// Uso:
//   node scripts/import-fuerteventura-pueblos.mjs              -> todos los pueblos de la lista
//   node scripts/import-fuerteventura-pueblos.mjs lajares el-cotillo   -> solo esos (ids de la lista)
//   node scripts/import-fuerteventura-pueblos.mjs --lista       -> muestra ids y radios sin descargar
// Salida: public/data/zones/<id>.raw.json (mismo formato que corralejo-osm.raw.json) + public/data/zones/index.json
// El centro de cada pueblo NO se inventa: se pide a OSM por nombre (nodo place=*) dentro de la caja de la isla.
// Se puede relanzar: salta los pueblos ya descargados (borra el .json para repetirlo) y reintenta si Overpass está ocupado.
import { writeFileSync, readFileSync, mkdirSync, existsSync } from "node:fs";

const ISLA = "27.99,-14.60,28.80,-13.75"; // sur,oeste,norte,este
// id, nombre en OSM, radio en metros (la zona descargada es un cuadrado de ±radio alrededor del centro)
export const PUEBLOS = [
  ["puerto-del-rosario", "Puerto del Rosario", 1500], ["morro-jable", "Morro Jable", 1100], ["caleta-de-fuste", "Caleta de Fuste", 900],
  ["gran-tarajal", "Gran Tarajal", 900], ["costa-calma", "Costa Calma", 800], ["el-cotillo", "El Cotillo", 700],
  ["lajares", "Lajares", 600], ["la-oliva", "La Oliva", 600], ["antigua", "Antigua", 600], ["betancuria", "Betancuria", 500],
  ["pajara", "Pájara", 500], ["tuineje", "Tuineje", 500], ["tarajalejo", "Tarajalejo", 500], ["la-lajita", "La Lajita", 500],
  ["villaverde", "Villaverde", 450], ["parque-holandes", "Parque Holandés", 450], ["las-playitas", "Las Playitas", 400],
  ["majanicho", "Majanicho", 350], ["cofete", "Cofete", 400], ["ajuy", "Ajuy", 300], ["tefia", "Tefía", 300], ["vega-de-rio-palmas", "Vega de Río Palmas", 300],
];
if (process.argv.includes("--lista")) { for (const [id, n, r] of PUEBLOS) console.log(id.padEnd(22), n.padEnd(22), r + " m"); process.exit(0); }
const pedidos = process.argv.slice(2).filter((a) => !a.startsWith("--"));
const lista = pedidos.length ? PUEBLOS.filter(([id]) => pedidos.includes(id)) : PUEBLOS;
if (pedidos.length && lista.length !== pedidos.length) { console.error("Ids desconocidos. Usa --lista."); process.exit(1); }

const API = "https://overpass-api.de/api/interpreter";
const KEEP = ["name", "highway", "building", "building:levels", "height", "natural", "amenity", "tourism", "shop"];
const r6 = (n) => Math.round(n * 1e6) / 1e6;
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
async function overpass(q) {
  for (let i = 0; i < 5; i++) {
    const res = await fetch(API, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "IslandCrew-import/1.0 (hola@islandcrew.es)" }, body: "data=" + encodeURIComponent(q) });
    if (res.ok) return res.json();
    if ([429, 502, 503, 504].includes(res.status)) { console.log(`  Overpass ocupado (${res.status}), reintento en ${10 * (i + 1)} s…`); await sleep(10000 * (i + 1)); continue; }
    throw new Error("Overpass " + res.status);
  }
  throw new Error("Overpass sigue ocupado: prueba más tarde");
}
const RANGO = { city: 0, town: 1, village: 2, suburb: 3, hamlet: 4, locality: 5 };
async function centro(nombre) {
  const j = await overpass(`[out:json][timeout:60];node["place"]["name"="${nombre}"](${ISLA});out;`);
  const c = (j.elements || []).filter((e) => e.tags?.place in RANGO).sort((a, b) => RANGO[a.tags.place] - RANGO[b.tags.place])[0];
  return c ? { lat: c.lat, lng: c.lon } : null;
}

const dir = "public/data/zones"; mkdirSync(dir, { recursive: true });
const idxPath = dir + "/index.json"; let idx = { zones: [] };
try { if (existsSync(idxPath)) idx = JSON.parse(readFileSync(idxPath, "utf8")); } catch { /* índice nuevo */ }
const fallos = [];
for (const [id, nombre, R] of lista) {
  const f = `${dir}/${id}.raw.json`;
  if (existsSync(f) && !pedidos.length) { console.log(`= ${nombre}: ya descargado`); continue; }
  try {
    process.stdout.write(`> ${nombre}… `);
    const c = await centro(nombre); if (!c) { console.log("no encontrado en OSM (¿otro nombre?)"); fallos.push(nombre); continue; }
    await sleep(1500);
    const dLat = R / 110574, dLng = R / (111320 * Math.cos((c.lat * Math.PI) / 180)); const bb = `${c.lat - dLat},${c.lng - dLng},${c.lat + dLat},${c.lng + dLng}`;
    const q = `[out:json][timeout:120];(way["highway"](${bb});way["building"](${bb});way["natural"~"coastline|beach"](${bb});node["amenity"~"restaurant|cafe|bar|fast_food|pub|ice_cream|marketplace"](${bb});node["tourism"~"hotel|hostel|apartment|guest_house|motel"](${bb});node["shop"](${bb}););out geom;`;
    const j = await overpass(q);
    const els = j.elements.map((e) => ({ type: e.type, id: e.id, ...(e.type === "node" ? { lat: r6(e.lat), lon: r6(e.lon) } : { geometry: (e.geometry || []).map((g) => ({ lat: r6(g.lat), lon: r6(g.lon) })) }), tags: Object.fromEntries(Object.entries(e.tags || {}).filter(([k]) => KEEP.includes(k))) }));
    const n = (fn) => els.filter(fn).length;
    writeFileSync(f, JSON.stringify({ attribution: "© Colaboradores de OpenStreetMap (ODbL)", fetched: new Date().toISOString(), center: c, radius: R, elements: els }));
    const entrada = { id, name: nombre, lat: r6(c.lat), lng: r6(c.lng), radius: R, streets: n((e) => e.tags.highway), buildings: n((e) => e.tags.building) };
    idx.zones = [...idx.zones.filter((z) => z.id !== id), entrada];
    console.log(`${entrada.streets} calles, ${entrada.buildings} edificios (${(JSON.stringify(els).length / 1e6).toFixed(1)} MB)`);
    await sleep(2500);
  } catch (e) { console.log("ERROR:", e.message); fallos.push(nombre); }
}
idx.zones.sort((a, b) => PUEBLOS.findIndex((p) => p[0] === a.id) - PUEBLOS.findIndex((p) => p[0] === b.id));
writeFileSync(idxPath, JSON.stringify({ attribution: "© Colaboradores de OpenStreetMap (ODbL)", updated: new Date().toISOString(), zones: idx.zones }));
console.log(`\nListo: ${idx.zones.length} pueblos en ${dir}/` + (fallos.length ? ` · sin descargar: ${fallos.join(", ")} (relanza el script)` : ""));
console.log("Prueba: /mundo/real?pueblo=" + (idx.zones[0]?.id || "lajares") + "  ·  en el juego, tecla 0 = siguiente pueblo");
