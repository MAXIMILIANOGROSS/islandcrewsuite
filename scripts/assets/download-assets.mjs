#!/usr/bin/env node
// Descarga idempotente de packs AUTO/REVIEW a IslandCrewAssets/Source/<id>/.
// Nunca modifica ni borra originales. Si una URL falla → "MANUAL DOWNLOAD REQUIRED" y sigue.
// Uso: node scripts/assets/download-assets.mjs [--dry] [--only=id1,id2]
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { execFileSync } from "node:child_process";
import { PACKS, FOLDERS, VERIFIED } from "./registry.mjs";
import { ROOT } from "./lib.mjs";

const dry = process.argv.includes("--dry");
const only = (process.argv.find((a) => a.startsWith("--only=")) || "").slice(7).split(",").filter(Boolean);
const today = new Date().toISOString().slice(0, 10);
const report = [];

for (const f of FOLDERS) if (!dry) fs.mkdirSync(path.join(ROOT, f), { recursive: true });

function unzip(zip, dest) {
  fs.mkdirSync(dest, { recursive: true });
  try { execFileSync("unzip", ["-n", "-q", zip, "-d", dest]); return true; } catch {}
  try { execFileSync("python3", ["-I", "-m", "zipfile", "-e", zip, dest]); return true; } catch { return false; }
}

for (const p of PACKS) {
  if (only.length && !only.includes(p.id)) continue;
  const row = { id: p.id, status: p.status, result: "", files: [] };
  report.push(row);
  if (p.status === "MANUAL" || p.status === "DUPLICATE" || !p.files.length) { row.result = p.status === "DUPLICATE" ? "DUPLICADO (se usa la copia de OpenGameArt)" : "MANUAL DOWNLOAD REQUIRED → " + p.page; continue; }
  if (p.skipIfExists && fs.existsSync(path.join(ROOT, "Source", p.skipIfExists))) { row.result = "OK (ya existe " + p.skipIfExists + ")"; continue; }
  const dir = path.join(ROOT, "Source", p.id);
  for (const f of p.files) {
    const target = path.join(dir, f.name);
    if (fs.existsSync(target)) { row.files.push(f.name + ": ya descargado"); continue; }
    if (dry) { row.files.push(f.name + ": (dry) " + f.url); continue; }
    try {
      const res = await fetch(f.url, { redirect: "follow", headers: { "user-agent": "IslandCrewAssets/1.0 (+https://islandcrew.es)" } });
      const type = res.headers.get("content-type") || "";
      if (!res.ok || /text\/html/.test(type)) throw new Error("HTTP " + res.status + " " + type);
      const buf = Buffer.from(await res.arrayBuffer());
      fs.mkdirSync(dir, { recursive: true });
      fs.writeFileSync(target, buf);
      const meta = { name: p.name, author: p.author, license: p.license, page: p.page, url: f.url, downloaded: today, registryVerified: VERIFIED, bytes: buf.length, sha256: crypto.createHash("sha256").update(buf).digest("hex"), status: p.status };
      fs.writeFileSync(target + ".download.json", JSON.stringify(meta, null, 2));
      if (f.name.endsWith(".zip")) unzip(target, path.join(dir, f.name.replace(/\.zip$/, "")));
      row.files.push(f.name + ": OK " + (buf.length / 1048576).toFixed(1) + " MB");
    } catch (e) {
      row.files.push(f.name + ": FALLÓ (" + e.message + ")");
    }
  }
  const failed = row.files.some((x) => x.includes("FALLÓ"));
  row.result = failed ? "MANUAL DOWNLOAD REQUIRED → " + p.page : p.status === "REVIEW" ? "DESCARGADO — REQUIERE REVISIÓN (no usar aún)" : "OK";
  if (p.status === "AUTO" && !failed) {
    // El pack debe traer licencia CC0: se guarda copia y se avisa si no aparece.
    const lic = fs.existsSync(dir) && fs.readdirSync(dir, { recursive: true }).find((x) => /licen[cs]e/i.test(String(x)));
    row.license = lic ? "licencia en pack: " + lic : "sin archivo de licencia en el zip: confía en la ficha (" + p.license + ")";
  }
}
if (!dry) {
  fs.mkdirSync(path.join(ROOT, "Documentation"), { recursive: true });
  fs.writeFileSync(path.join(ROOT, "Documentation", "DOWNLOAD_REPORT.json"), JSON.stringify({ date: today, report }, null, 2));
}
for (const r of report) console.log(r.result.padEnd(48), r.id, r.files.length ? "\n    " + r.files.join("\n    ") : "");
