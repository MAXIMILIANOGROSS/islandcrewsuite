#!/usr/bin/env node
// Generador determinista de NPC: modelo + skin + ropa + pelo + accesorios + animaciones.
// Uso: node scripts/assets/build-npcs.mjs [--count=300] [--seed=ICW-000001] [--summary]
import fs from "node:fs";
import path from "node:path";
import { PACKS, CANDIDATES } from "./registry.mjs";
import { ROOT, WANTED, hashStr, mulberry32, buildAnimMap } from "./lib.mjs";

export const ARCHETYPES = {
  camarero: { es: "Camarero/a", anims: ["carry", "talk", "wave", "work"], night: ["drink", "talk"], tone: "servicial, observador" },
  cocinero: { es: "Cocinero/a", anims: ["cook", "work", "clean", "talk"], night: ["eat", "sleep"], tone: "perfeccionista, irritable" },
  pescador: { es: "Pescador/a", anims: ["fish", "carry", "work", "look_around"], night: ["drink", "sleep"], tone: "callado, supersticioso" },
  turista: { es: "Turista", anims: ["phone", "point", "look_around", "wave", "laugh"], night: ["dance", "drink", "laugh"], tone: "curioso, despistado" },
  empresario: { es: "Empresario/a", anims: ["phone", "talk", "argue", "stand"], night: ["drink", "talk"], tone: "ambicioso, impaciente" },
  portuario: { es: "Trabajador/a del puerto", anims: ["carry", "push", "work", "climb"], night: ["drink", "argue"], tone: "directo, cansado" },
  surfista: { es: "Surfista", anims: ["run", "swim", "wave", "laugh"], night: ["dance", "drink"], tone: "relajado, competitivo" },
  buceador: { es: "Buceador/a", anims: ["dive", "swim", "work", "wave"], night: ["eat", "sleep"], tone: "metódico, aventurero" },
  musico: { es: "Músico/a", anims: ["dance", "talk", "laugh", "stand"], night: ["dance", "drink", "talk"], tone: "soñador, sociable" },
  vendedor: { es: "Vendedor/a", anims: ["wave", "talk", "carry", "point"], night: ["clean", "sleep"], tone: "persuasivo, ingenioso" },
  local: { es: "Habitante local", anims: ["walk", "talk", "sit", "look_around"], night: ["sit", "sleep", "talk"], tone: "orgulloso, hospitalario" },
  excentrico: { es: "Excéntrico/a", anims: ["dance", "point", "panic", "laugh"], night: ["dance", "look_around"], tone: "impredecible, creativo" },
  misterioso: { es: "Misterioso/a", anims: ["look_around", "stand", "phone", "walk"], night: ["walk", "look_around", "argue"], tone: "reservado, calculador" },
  comico: { es: "Cómico/a", anims: ["laugh", "dance", "fall", "talk"], night: ["laugh", "drink", "dance"], tone: "bromista, empático" },
  nocturno: { es: "Nocturno/a", anims: ["drink", "dance", "argue", "phone"], night: ["dance", "drink", "fight", "argue"], tone: "magnético, inquieto" },
};
const HAIR = ["corto", "rapado", "rizado", "largo", "coleta", "moño", "calvo", "canoso", "mohicano", "ondulado"];
const HAIRCOL = ["#1b1b1b", "#3b2417", "#6b4423", "#a67c52", "#d8b45e", "#8c2f1c", "#9aa0a6", "#e8e8e8"];
const CLOTH = { camarero: ["camisa blanca+delantal"], cocinero: ["chaquetilla blanca"], pescador: ["jersey azul+botas"], turista: ["camiseta+bermudas", "camisa floreada", "vestido de verano"], empresario: ["traje", "blazer"], portuario: ["mono naranja+chaleco"], surfista: ["bañador+camiseta lycra"], buceador: ["neopreno"], musico: ["camisa abierta", "chaqueta vintage"], vendedor: ["camisa lino+gorra"], local: ["camisa lino", "polo", "vestido sencillo"], excentrico: ["abrigo imposible", "chándal dorado"], misterioso: ["gabardina oscura"], comico: ["camisa a cuadros"], nocturno: ["cuero+gafas", "vestido de noche"] };
const ACC = ["gafas de sol", "gorra", "sombrero de paja", "mochila", "cámara", "auriculares", "reloj", "collar", "pañuelo", "bolso", "ninguno", "ninguno", "ninguno"];
const SKIN = ["#f1d5bf", "#e3b896", "#c98f63", "#a86b43", "#7a4a2d", "#4f301e"];
const BODY = ["delgado", "medio", "atlético", "robusto", "alto"];
const AGE = [["young_adult", 3], ["adult", 6], ["elder", 1.5]];
const pick = (r, a) => a[Math.floor(r() * a.length)];
const wpick = (r, a) => { let t = a.reduce((s, x) => s + x[1], 0) * r(); for (const [v, w] of a) if ((t -= w) < 0) return v; return a[0][0]; };

const readMap = (root) => { try { return JSON.parse(fs.readFileSync(path.join(root, "Documentation/ANIMATION_MAP.json"), "utf8")); } catch { return { map: {}, missing: WANTED }; } };
export function loadPools(root = ROOT) {
  let cat = {}; try { cat = JSON.parse(fs.readFileSync(path.join(root, "Documentation/NPC_ASSET_DATABASE.json"), "utf8")).catalog || {}; } catch {}
  const people = (cat.models || []).filter((m) => m.usable && m.category !== "monsters" && m.category !== "accessory" && m.kind !== "animation-library");
  // three.js carga glTF/GLB directamente: FBX/OBJ/DAE solo entran si no hay suficientes GLB (y quedan «pending-retarget»).
  const glb = people.filter((m) => /^(glb|gltf)$/.test(m.format));
  if (glb.length >= 6) return { people: glb, map: readMap(root) };
  return { people, map: readMap(root) };
}

/** Los clips solo valen para el rig del modelo: Kenney usa los suyos; los modelos con rig UAL (mannequins) usan UAL; FBX sin inspeccionar → "retarget". */
function clipsFor(base, pools, cache) {
  if (cache.has(base.id)) return cache.get(base.id);
  let r;
  if (base.animations?.length >= 3) r = { rig: base.pack, ...buildAnimMap([{ pack: base.pack, priority: 100, clips: base.animations }]) };
  else if (/mannequin|ual|universal/i.test(base.id)) r = { rig: "UAL", map: pools.map.map || {}, missing: pools.map.missing || [] };
  else r = { rig: "pending-retarget", map: {}, missing: WANTED };
  cache.set(base.id, r); return r;
}
export function buildNpcs({ count = 300, seed = "ICW-000001", pools = loadPools() } = {}) {
  const rigCache = new Map();
  const r = mulberry32(hashStr(seed));
  const keys = Object.keys(ARCHETYPES);
  const seen = new Set(), out = [];
  const bases = pools.people.length ? pools.people : [{ id: "PLACEHOLDER/base_m", gender: "male", file: null }, { id: "PLACEHOLDER/base_f", gender: "female", file: null }];
  let guard = 0;
  while (out.length < count && guard++ < count * 50) {
    const arch = pick(r, keys), a = ARCHETYPES[arch];
    const base = pick(r, bases);
    const gender = base.gender !== "unknown" ? base.gender : r() < 0.5 ? "male" : "female";
    const age = base.age && base.age !== "adult" ? base.age : wpick(r, AGE);
    const npc = {
      model: base.id, skin_tone: pick(r, SKIN), hair: pick(r, HAIR), hair_color: pick(r, HAIRCOL), clothing: pick(r, CLOTH[arch]),
      outfit_tint: "#" + Math.floor(r() * 0xffffff).toString(16).padStart(6, "0"), accessories: [pick(r, ACC)].filter((x) => x !== "ninguno"),
      body_type: pick(r, BODY), height_scale: +(0.92 + r() * 0.16).toFixed(2),
    };
    const key = [arch, npc.model, npc.skin_tone, npc.hair, npc.hair_color, npc.clothing, npc.outfit_tint, npc.accessories.join()].join("|");
    if (seen.has(key)) continue; seen.add(key);
    const id = "NPC_" + String(out.length + 1).padStart(4, "0");
    out.push({
      character_id: id, archetype: arch, label: a.es, gender, age_category: age, ...npc, animations: ["idle", "walk", "talk", ...a.anims], night_animations: a.night,
      ...(() => { const rg = clipsFor(base, pools, rigCache); const want = [...new Set(["idle", "walk", "talk", ...a.anims, ...a.night])]; return { rig: rg.rig, animation_clips: Object.fromEntries(want.filter((k) => rg.map[k]).map((k) => [k, rg.map[k]])), animations_unavailable: want.filter((k) => !rg.map[k]) }; })(),
      personality_tone: a.tone, factory_seed: seed + ":" + id, source: base.pack || "pending", license: base.license || "pending",
      needs_procedural: { hair: true, accessories: npc.accessories.length > 0, clothing_tint: true },
    });
  }
  return out;
}

export function summary(root = ROOT) {
  const dl = (() => { try { return JSON.parse(fs.readFileSync(path.join(root, "Documentation/DOWNLOAD_REPORT.json"), "utf8")).report; } catch { return null; } })();
  const db = (() => { try { return JSON.parse(fs.readFileSync(path.join(root, "Documentation/NPC_ASSET_DATABASE.json"), "utf8")).catalog; } catch { return null; } })();
  const cc0 = PACKS.filter((p) => p.status === "AUTO" && /^CC0/.test(p.license));
  const lines = [
    ["TOTAL DE PACKS ENCONTRADOS", PACKS.length + " (+ " + CANDIDATES.length + " candidatos sin verificar y la colección de 56 packs Quaternius)"],
    ["MODELOS", db ? db.models.filter((m) => m.usable).length + " usables (" + db.models.length + " detectados)" : "pendiente: ejecuta download + catalog"],
    ["SKINS", db ? db.skins : "pendiente (según fichas: ≥ " + PACKS.reduce((s, p) => s + (p.claims?.skins || 0), 0) + ")"],
    ["ANIMACIONES", db ? (db.animationLibraries.reduce((s, l) => s + l.clips.length, 0) + Object.values(db.embeddedClips || {}).reduce((s, l) => s + l.length, 0)) + " clips (librerías UAL + clips propios de cada pack)" : "pendiente (según fichas: 43 UAL1 + 130+ UAL2 + 27 Blocky + 9)"],
    ["ASSETS CC0", cc0.length + " packs (" + cc0.map((p) => p.id).join(", ") + ")"],
    ["ASSETS QUE REQUIEREN REVISIÓN", PACKS.filter((p) => p.status === "REVIEW").map((p) => p.id).join(", ")],
    ["DESCARGAS MANUALES", PACKS.filter((p) => p.status === "MANUAL").length + ": " + PACKS.filter((p) => p.status === "MANUAL").map((p) => p.name).join("; ") + (dl ? " + las que fallaron: " + (dl.filter((r) => /^MANUAL/.test(r.result) && r.status === "AUTO").map((r) => r.id).join(", ") || "ninguna") : "")],
  ];
  return lines.map(([k, v]) => k + ": " + v).join("\n");
}

if (import.meta.url === "file://" + process.argv[1]) {
  const arg = (n, d) => (process.argv.find((a) => a.startsWith("--" + n + "=")) || "").slice(n.length + 3) || d;
  if (process.argv.includes("--summary")) console.log(summary());
  else {
    const npcs = buildNpcs({ count: +arg("count", 300), seed: arg("seed", "ICW-000001") });
    fs.mkdirSync(path.join(ROOT, "Documentation"), { recursive: true });
    fs.writeFileSync(path.join(ROOT, "Documentation/NPC_COMBINATIONS.json"), JSON.stringify({ seed: arg("seed", "ICW-000001"), count: npcs.length, npcs }, null, 2));
    console.log(npcs.length + " NPC → Documentation/NPC_COMBINATIONS.json");
    console.log(summary());
  }
}
