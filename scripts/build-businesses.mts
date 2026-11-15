// Genera public/data/corralejo-businesses.json (230 negocios de JUEGO sobre el Corralejo real). Uso: node --experimental-strip-types scripts/build-businesses.mts
import { readFileSync, writeFileSync } from "node:fs";
import { buildWorld, pickServiceBuilding, pickSpawn } from "../src/lib/geo.ts";
import { generateBusinesses, validateBusinesses } from "../src/lib/businesses.ts";
const j = JSON.parse(readFileSync("public/data/corralejo-osm.raw.json", "utf8")); const w = buildWorld(j.elements); const sp = pickSpawn(w); const off = pickServiceBuilding(w, sp)!;
const real = j.elements.filter((e: any) => e.type === "node" && e.tags?.name).map((e: any) => e.tags.name);
const list = generateBusinesses(w, { excludeBuildingIds: [off.id], realNames: real, origin: sp, anchors: w.pois.map((q) => ({ x: q.x, z: q.z, cat: q.cat })) }); const v = validateBusinesses(list, w);
console.log("edificios", w.buildings.length, "calles", w.streets.length, "| negocios", list.length, "| BUSINESSES_VALIDATED =", v.ok); if (!v.ok) { console.log(v.errors.slice(0, 20)); process.exit(1); }
console.log(v.summary);
writeFileSync("public/data/corralejo-businesses.json", JSON.stringify({ version: 1, generated: new Date().toISOString(), note: "Negocios FICTICIOS de ambientación sobre edificios reales de OpenStreetMap (© Colaboradores de OpenStreetMap, ODbL).", officeBuildingId: off.id, spawn: sp, businesses: list }));
