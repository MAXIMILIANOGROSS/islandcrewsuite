import fs from "node:fs";
const src = process.argv[2]; if (!src) { console.error("uso: node convert-overture-places.mjs archivo.geojson"); process.exit(1); }
const j = JSON.parse(fs.readFileSync(src, "utf8"));
const obj = (v) => { if (typeof v === "string") { try { return JSON.parse(v); } catch { return v; } } return v; };
const typeOf = (c) => { c = String(c || ""); if (/hotel|hostel|resort|lodging|guest_house|motel/.test(c)) return "hotel"; if (/cafe|coffee|tea_room/.test(c)) return "cafe"; if (/bakery|pastry/.test(c)) return "bakery"; if (/\bbar\b|_bar|pub|nightlife|night_club|lounge/.test(c)) return "bar"; if (/restaurant|food|pizza|tapas|seafood|burger|sushi|ice_cream|takeaway|fast_food/.test(c)) return "restaurant"; if (/supermarket|grocery|convenience/.test(c)) return "supermarket"; return null; };
const out = []; const seen = new Set();
for (const f of j.features || []) {
  const p = f.properties || {}; const names = obj(p.names), cats = obj(p.categories); const name = names && names.primary; if (!name || !f.geometry || f.geometry.type !== "Point") continue;
  const conf = Number(p.confidence ?? 1); if (conf < 0.6) continue; const st = p.operating_status; if (st && st !== "open") continue;
  const type = typeOf(cats && cats.primary); if (!type) continue; const [lng, lat] = f.geometry.coordinates; const key = name.toLowerCase() + Math.round(lat * 4000) + Math.round(lng * 4000); if (seen.has(key)) continue; seen.add(key);
  out.push({ id: String(p.id || f.id || key), name, lat, lng, type });
}
fs.writeFileSync(new URL("../public/data/corralejo-places.json", import.meta.url), JSON.stringify({ places: out, attribution: "Lugares: Overture Maps Foundation (datos abiertos)" }));
console.log(`OK: ${out.length} lugares -> public/data/corralejo-places.json`);
