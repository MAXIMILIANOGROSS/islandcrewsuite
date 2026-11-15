// Descarga TODOS los negocios de Fuerteventura desde OpenStreetMap (Overpass) y los guarda en el mismo formato que corralejo-places.json.
// Uso (necesita internet): node scripts/fetch-fuerteventura-places.mjs
// Datos © colaboradores de OpenStreetMap (ODbL). Resultado: public/data/fuerteventura-places.json
import fs from "node:fs";
const BBOX = "28.04,-14.55,28.78,-13.80"; // sur, oeste, norte, este (isla completa)
const PARTS = [`nwr["amenity"~"restaurant|cafe|bar|pub|fast_food|ice_cream"](${BBOX});`, `nwr["tourism"~"hotel|hostel|guest_house|apartment"](${BBOX});`, `nwr["shop"](${BBOX});`];
const TYPE = (t) => t.amenity === "restaurant" ? "restaurant" : t.amenity === "cafe" ? "cafe" : t.amenity === "bar" || t.amenity === "pub" ? "bar" : t.amenity === "fast_food" ? "fast_food" : t.amenity === "ice_cream" ? "ice_cream" : t.tourism ? "hotel" : t.shop === "supermarket" ? "supermarket" : t.shop ? "shop" : null;
// Los servidores públicos se saturan a menudo (504/500/429): la consulta va en tres partes y cada una rota de espejo con espera.
const HOSTS = ["https://overpass.kumi.systems/api/interpreter", "https://overpass-api.de/api/interpreter", "https://overpass.private.coffee/api/interpreter"];
const sleep = (ms) => new Promise((ok) => setTimeout(ok, ms));
async function overpass(part) {
  const q = `[out:json][timeout:120];(${part});out center tags;`; let err;
  for (let i = 0; i < 12; i++) { const url = HOSTS[i % HOSTS.length];
    try { const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "island-crew-web/1.0 (fetch-fuerteventura-places)", Accept: "application/json" }, body: "data=" + encodeURIComponent(q) }); if (r.ok) return (await r.json()).elements; err = "Overpass " + r.status + " en " + url; } catch (e) { err = e.message + " en " + url; }
    console.warn(err); await sleep(10000); }
  throw new Error(err);
}
const d = { elements: [] }; const seen = new Set();
for (const part of PARTS) for (const e of await overpass(part)) { const k = e.type + e.id; if (!seen.has(k)) { seen.add(k); d.elements.push(e); } }
const places = [];

for (const e of d.elements) { const t = e.tags || {}; const type = TYPE(t); const lat = e.lat ?? e.center?.lat, lng = e.lon ?? e.center?.lon; if (!type || !t.name || lat == null) continue;
  places.push({ id: `osm${e.type[0]}${e.id}`, name: t.name, lat, lng, type, email: t.email || t["contact:email"] || null, phone: t.phone || t["contact:phone"] || null, web: t.website || t["contact:website"] || null, address: [t["addr:street"], t["addr:housenumber"], t["addr:postcode"], t["addr:city"]].filter(Boolean).join(" ") || null, social: t["contact:facebook"] || t["contact:instagram"] || null, oid: e.id, src: "osm", wa: null }); }
fs.writeFileSync("public/data/fuerteventura-places.json", JSON.stringify({ places, attribution: "Lugares: © colaboradores de OpenStreetMap (ODbL)" }));
console.log("Guardados", places.length, "negocios");
