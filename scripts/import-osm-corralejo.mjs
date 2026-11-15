// Descarga de OpenStreetMap (Overpass API) las calles, edificios, costa y negocios de Corralejo.
// Uso:  node scripts/import-osm-corralejo.mjs [radio_metros=600] [lat] [lng]
// Salida: public/data/corralejo-osm.raw.json   (datos © Colaboradores de OpenStreetMap, licencia ODbL: hay que mostrar la atribución)
import { writeFileSync, mkdirSync } from "node:fs";
const R = Number(process.argv[2] || 600), LAT = Number(process.argv[3] || 28.738617), LNG = Number(process.argv[4] || -13.867431);
const dLat = R / 110574, dLng = R / (111320 * Math.cos((LAT * Math.PI) / 180)); const bb = `${LAT - dLat},${LNG - dLng},${LAT + dLat},${LNG + dLng}`;
const q = `[out:json][timeout:90];(way["highway"](${bb});way["building"](${bb});way["natural"~"coastline|beach"](${bb});node["amenity"~"restaurant|cafe|bar|fast_food|pub|ice_cream|marketplace"](${bb});node["tourism"~"hotel|hostel|apartment|guest_house|motel"](${bb});node["shop"](${bb}););out geom;`;
const KEEP = ["name", "highway", "building", "building:levels", "height", "natural", "amenity", "tourism", "shop"];
const r6 = (n) => Math.round(n * 1e6) / 1e6;
const res = await fetch("https://overpass-api.de/api/interpreter", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "IslandCrew-import/1.0 (hola@islandcrew.es)" }, body: "data=" + encodeURIComponent(q) });
if (!res.ok) { console.error("Overpass respondió", res.status, await res.text().then((t) => t.slice(0, 200))); process.exit(1); }
const j = await res.json();
const els = j.elements.map((e) => ({ type: e.type, id: e.id, ...(e.type === "node" ? { lat: r6(e.lat), lon: r6(e.lon) } : { geometry: (e.geometry || []).map((g) => ({ lat: r6(g.lat), lon: r6(g.lon) })) }), tags: Object.fromEntries(Object.entries(e.tags || {}).filter(([k]) => KEEP.includes(k))) }));
mkdirSync("public/data", { recursive: true });
writeFileSync("public/data/corralejo-osm.raw.json", JSON.stringify({ attribution: "© Colaboradores de OpenStreetMap (ODbL)", fetched: new Date().toISOString(), center: { lat: LAT, lng: LNG }, radius: R, elements: els }));
const c = (f) => els.filter(f).length; console.log(`OK: ${c((e) => e.tags.highway)} calles, ${c((e) => e.tags.building)} edificios, ${c((e) => e.tags.natural)} costa, ${c((e) => e.type === "node")} negocios/POIs`);
