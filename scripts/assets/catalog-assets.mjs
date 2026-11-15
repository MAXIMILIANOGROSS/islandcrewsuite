#!/usr/bin/env node
// Cataloga lo descargado: modelos, skins, animaciones. Copia (nunca mueve) modelos a Characters/*.
// Escribe NPC_ASSET_DATABASE.json (parte catálogo) y ANIMATION_MAP.json.
import fs from "node:fs";
import path from "node:path";
import { PACKS } from "./registry.mjs";
import { ROOT, walk, readGlbJson, inspectGltf, classify, charFolder, buildAnimMap, animFolder } from "./lib.mjs";

const MODEL = /\.(glb|gltf|fbx|obj|dae)$/i;
const PRIORITY = { "oga-ual2-standard": 100, "UAL_Standard": 90, "oga-ual1-standard": 90 };
const models = [], skins = [], animPacks = [];
for (const p of PACKS.filter((x) => x.status === "AUTO" || x.status === "REVIEW")) {
  const dir = path.join(ROOT, "Source", p.id);
  if (!fs.existsSync(dir) && p.id !== "oga-ual1-standard") continue;
  const files = walk(dir);
  const usable = p.status === "AUTO";
  for (const f of files) {
    const rel = path.relative(ROOT, f);
    if (/\.png$/i.test(f) && /skin|texture|colormap|variation/i.test(f)) skins.push({ pack: p.id, file: rel, usable });
    if (!MODEL.test(f)) continue;
    const base = path.basename(f).replace(/\.[^.]+$/, "");
    const e = { id: p.id + "/" + base, pack: p.id, file: rel, format: path.extname(f).slice(1).toLowerCase(), license: p.license, usable, ...classify(base) };
    if (/\.(glb|gltf)$/i.test(f)) { try { const i = inspectGltf(readGlbJson(f)); Object.assign(e, i); if (i.animations.length >= 20 && /UAL\d?_|animation[_ ]?library/i.test(f)) { animPacks.push({ pack: p.id, priority: PRIORITY[p.id] || 50, clips: i.animations, file: rel }); e.kind = "animation-library"; } } catch (err) { e.parseError = err.message; } }
    models.push(e);
  }
}
// UAL1 descargado a mano
const ual1 = path.join(ROOT, "Source/UAL_Standard/UAL1_Standard.glb");
if (fs.existsSync(ual1) && !animPacks.some((a) => a.file.includes("UAL1"))) { const i = inspectGltf(readGlbJson(ual1)); animPacks.push({ pack: "UAL_Standard", priority: 90, clips: i.animations, file: path.relative(ROOT, ual1) }); }

// Copiar (no mover) personajes usables a Characters/<carpeta>
let copied = 0;
for (const m of models) {
  if (!m.usable || m.kind === "animation-library" || !m.meshes?.length && m.format === "glb" && !m.skins) continue;
  const dest = path.join(ROOT, "Characters", charFolder(m));
  fs.mkdirSync(dest, { recursive: true });
  const t = path.join(dest, m.pack + "__" + path.basename(m.file));
  if (!fs.existsSync(t)) { fs.copyFileSync(path.join(ROOT, m.file), t); copied++; }
  m.catalogPath = path.relative(ROOT, t);
}
for (const s of skins.filter((x) => x.usable)) { const t = path.join(ROOT, "Skins", s.pack + "__" + path.basename(s.file)); fs.mkdirSync(path.dirname(t), { recursive: true }); if (!fs.existsSync(t)) fs.copyFileSync(path.join(ROOT, s.file), t); }

const embedded = {};
for (const m of models) if (m.usable && m.animations?.length && m.kind !== "animation-library" && !animPacks.some((a) => a.file === m.file)) { embedded[m.pack] ||= new Set(); m.animations.forEach((a) => embedded[m.pack].add(a)); }
const { map, missing } = buildAnimMap(animPacks);
for (const [k, v] of Object.entries(map)) fs.mkdirSync(path.join(ROOT, "Animations", animFolder(k)), { recursive: true });
const doc = path.join(ROOT, "Documentation");
fs.mkdirSync(doc, { recursive: true });
fs.writeFileSync(path.join(doc, "ANIMATION_MAP.json"), JSON.stringify({ generated: new Date().toISOString().slice(0, 10), policy: "Sin muertes gráficas: juego no letal. Prioridad UAL2 > UAL1 > resto.", libraries: animPacks.map(({ pack, priority, file, clips }) => ({ pack, priority, file, clips: clips.length })), map, missing }, null, 2));
const dbFile = path.join(doc, "NPC_ASSET_DATABASE.json");
const prev = fs.existsSync(dbFile) ? JSON.parse(fs.readFileSync(dbFile, "utf8")) : {};
fs.writeFileSync(dbFile, JSON.stringify({ ...prev, generated: new Date().toISOString().slice(0, 10), catalog: { models, skins: skins.length, animationLibraries: animPacks.map((a) => ({ pack: a.pack, file: a.file, clips: a.clips })), embeddedClips: Object.fromEntries(Object.entries(embedded).map(([k, v]) => [k, [...v]])) } }, null, 2));
console.log(`modelos ${models.length} (copiados ${copied}) · skins ${skins.length} · librerías de animación ${animPacks.length} · clips de librería ${animPacks.reduce((a, b) => a + b.clips.length, 0)} · clips propios de los modelos ${Object.values(embedded).reduce((a, b) => a + b.size, 0)} · animaciones sin cubrir: ${missing.join(", ") || "ninguna"}`);
