// Utilidades compartidas: GLB parser, clasificación por nombre, mapa de animaciones, PRNG.
import fs from "node:fs";
import path from "node:path";

export const ROOT = process.env.IC_ASSETS || path.resolve(process.cwd(), "IslandCrewAssets");

/** Lee el chunk JSON de un .glb (o un .gltf) sin dependencias. */
export function readGlbJson(file) {
  const buf = fs.readFileSync(file);
  if (file.toLowerCase().endsWith(".gltf")) return JSON.parse(buf.toString("utf8"));
  if (buf.readUInt32LE(0) !== 0x46546c67) throw new Error("no es GLB: " + file);
  const len = buf.readUInt32LE(12);
  if (buf.readUInt32LE(16) !== 0x4e4f534a) throw new Error("primer chunk no es JSON");
  return JSON.parse(buf.subarray(20, 20 + len).toString("utf8"));
}
export function inspectGltf(json) {
  return {
    animations: (json.animations || []).map((a, i) => a.name || "anim" + i),
    meshes: (json.meshes || []).map((m) => m.name || ""),
    materials: (json.materials || []).map((m) => m.name || ""),
    skins: (json.skins || []).length,
    images: (json.images || []).length,
  };
}

// --- animaciones que pide el producto → regex de sinónimos (se prueba en orden, gana la primera coincidencia)
export const WANTED = ["idle","talk","laugh","wave","point","dance","drink","eat","sit","stand","walk","run","look_around","phone","argue","push","fight","fall","panic","fish","swim","dive","climb","work","cook","clean","carry","sleep"];
export const ANIM_SYN = {
  idle: /^idle(_loop)?$|^idle[_ ]?(0|1|a)?$|^stand(ing)?_idle|^idle/i,
  talk: /talk(ing)?(_loop)?$|^talk|conversation/i,
  laugh: /laugh|chuckle/i,
  wave: /wave|greet|hello/i,
  point: /point/i,
  dance: /danc/i,
  drink: /drink|sip/i,
  eat: /(^|_)(eat|eating|consume|chew)(_|$)/i,
  sit: /sit(ting)?_idle|^sit(ting)?(_loop)?$|^sit/i,
  stand: /^stand|standing/i,
  walk: /^walk(_fwd)?(_loop)?$|^walk/i,
  run: /^(jog|run)(_fwd)?(_loop)?$|^run|^jog/i,
  look_around: /look[_ ]?around|torch|search/i,
  phone: /phone|call|texting/i,
  argue: /argu|angry|shout|yell/i,
  push: /push/i,
  fight: /punch|kick|fight|attack|sword|melee/i,
  fall: /fall|hit_chest|knock|stumble/i,
  panic: /panic|scared|flee|fear/i,
  fish: /fish|cast/i,
  swim: /swim/i,
  dive: /div(e|ing)|underwater/i,
  climb: /climb|ladder/i,
  work: /fixing|work|hammer|dig|farm|plant|chop|mine|repair/i,
  cook: /cook|stir|kitchen/i,
  clean: /clean|sweep|mop|wash/i,
  carry: /carry|pickup|pick_up|lift/i,
  sleep: /sleep|rest_lying|lying/i,
};
const FOLDER_OF = { idle:"Idle", walk:"Walk", run:"Run", talk:"Talk", dance:"Dance", fight:"Fight", push:"Push", fall:"Fall", fish:"Fishing", swim:"Swimming", dive:"Diving", climb:"Climbing", work:"Working", eat:"Eating", drink:"Drinking", phone:"Phone", laugh:"Emotes", wave:"Emotes", point:"Emotes", panic:"Emotes", argue:"Emotes", look_around:"Emotes", sit:"Idle", stand:"Idle", carry:"Working", cook:"Working", clean:"Working", sleep:"Idle" };
export const animFolder = (k) => FOLDER_OF[k] || "Emotes";

/** packs: [{pack, priority, clips:[names]}] → { map: key→{pack,clip}, missing:[...] }. Mayor priority gana. */
// Política: juego no letal, nunca se mapean animaciones de muerte.
export const BANNED = /death|die(?!t)|dead|kill|execut|corpse/i;
export function buildAnimMap(packs) {
  const sorted = [...packs].sort((a, b) => b.priority - a.priority);
  const map = {};
  for (const key of WANTED) {
    for (const ex of PREFER[key] || []) { const p = sorted.find((q) => q.clips.includes(ex)); if (p) { map[key] = { pack: p.pack, clip: ex }; break; } }
    if (map[key]) continue;
    for (const p of sorted) {
      const hit = p.clips.filter((c) => ANIM_SYN[key].test(c) && !BANNED.test(c));
      if (hit.length) { map[key] = { pack: p.pack, clip: pickBest(hit) }; break; }
    }
  }
  return { map, missing: WANTED.filter((k) => !map[k]) };
}
const isLoop = (c) => /(^|_)loop$/i.test(c) && !/no_loop/i.test(c);
const pickBest = (hits) => [...hits].sort((a, b) => (isLoop(b) - isLoop(a)) || a.length - b.length)[0];
// Nombres canónicos preferidos (si algún pack los tiene exactos, ganan a la heurística)
export const PREFER = { idle: ["Idle_Loop", "idle"], walk: ["Walk_Loop", "walk"], run: ["Jog_Fwd_Loop", "Run_Loop", "run", "sprint"], talk: ["Idle_Talking_Loop"], sit: ["Sitting_Idle_Loop", "sit"], dance: ["Dance_Loop"], swim: ["Swim_Fwd_Loop"], push: ["Push_Loop"], carry: ["Walk_Carry_Loop", "PickUp_Table"] };

// --- clasificación heurística por nombre de modelo/archivo
export function classify(name) {
  const n = name.toLowerCase();
  const gender = /woman|women|female|girl|lady|waitress|femal/.test(n) ? "female" : /\bman\b|men\b|male|boy|guy|waiter|_m_|^m_/.test(n) ? "male" : "unknown";
  const age = /elder|old|grand|senior/.test(n) ? "elder" : /kid|child|boy|girl/.test(n) ? "child" : /young|teen/.test(n) ? "young_adult" : "adult";
  const cat = /^(aid|wheelchair|cane|crutch)([-_]|$)/.test(n) ? "accessory" : /zombie|skeleton|demon|monster|goblin|orc|alien|robot|ghost|yeti/.test(n) ? "monsters"
    : /knight|ninja|viking|pirate|wizard|elf|cowboy|samurai|king|queen|clown/.test(n) ? "unique"
    : /worker|builder|chef|cook|doctor|police|soldier|engineer|farmer|business|suit|sailor|fisher/.test(n) ? "workers"
    : /tourist|beach|swim/.test(n) ? "tourists" : "humans";
  return { gender, age, category: cat };
}
export function charFolder(c) {
  if (c.category === "accessory") return "Accessories";
  if (c.category === "humans") return c.age === "elder" ? "Humans/Elder" : c.age === "young_adult" || c.gender === "unknown" ? "Humans/YoungAdult" : c.gender === "female" ? "Humans/Female" : "Humans/Male";
  return { accessory: "Accessories", workers: "Workers", tourists: "Tourists", unique: "Unique", monsters: "Monsters" }[c.category] || "Unique";
}

// PRNG determinista
export function hashStr(s) { let h = 2166136261 >>> 0; for (const ch of s) { h ^= ch.charCodeAt(0); h = Math.imul(h, 16777619) >>> 0; } return h; }
export function mulberry32(a) { return () => { a |= 0; a = (a + 0x6d2b79f5) | 0; let t = Math.imul(a ^ (a >>> 15), 1 | a); t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t; return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; }

export function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const p = path.join(dir, e.name);
    e.isDirectory() ? walk(p, out) : out.push(p);
  }
  return out;
}
