#!/usr/bin/env node
// Verifica de forma reproducible el estado REAL de las skills de Island Crew.
// Solo comprueba lo que se puede comprobar: archivos, frontmatter, hash del lockfile.
// Una skill nunca es VALIDADA aquí: la validación funcional se documenta en docs/SKILLS_INVENTARIO.md.
import { readFileSync, existsSync, readdirSync, statSync } from "node:fs";
import { createHash } from "node:crypto";
import { join } from "node:path";

const RAIZ = process.cwd();
const lock = JSON.parse(readFileSync(join(RAIZ, "skills-lock.json"), "utf8")).skills ?? {};

const OBJETIVO = {
  "find-skills": "skill 1",
  genjutsu: "skill 2",
  "task-observer": "skill 7",
  "hormozi-offer": "skill 5",
};

function ficheros(dir, base = dir, acc = []) {
  for (const n of readdirSync(dir).sort()) {
    const p = join(dir, n);
    if (statSync(p).isDirectory()) ficheros(p, base, acc);
    else acc.push(p);
  }
  return acc;
}
function hashDir(dir) {
  const h = createHash("sha256");
  for (const f of ficheros(dir)) {
    h.update(f.slice(dir.length + 1));
    h.update(readFileSync(f));
  }
  return h.digest("hex");
}

const filas = [];
for (const [nombre, info] of Object.entries(lock)) {
  const dir = join(RAIZ, ".claude", "skills", nombre);
  const md = join(dir, "SKILL.md");
  const existe = existsSync(md);
  let frontmatter = false;
  if (existe) {
    const t = readFileSync(md, "utf8");
    frontmatter = /^---\n[\s\S]*?\bname:\s*\S+[\s\S]*?\n---/.test(t) && /description:/.test(t);
  }
  filas.push({
    skill: nombre,
    origen: info.source,
    lockHash: (info.computedHash ?? "").slice(0, 8),
    instalada: existe,
    frontmatterValido: frontmatter,
    archivos: existe ? ficheros(dir).length : 0,
    estado: existe && frontmatter ? "INSTALADA" : "FALLIDA",
    objetivo: OBJETIVO[nombre] ?? null,
  });
}
const resumen = {
  total: filas.length,
  instaladas: filas.filter((f) => f.estado === "INSTALADA").length,
  fallidas: filas.filter((f) => f.estado === "FALLIDA").map((f) => f.skill),
};
console.log(JSON.stringify({ resumen, filas }, null, 2));
process.exit(resumen.fallidas.length ? 1 : 0);
