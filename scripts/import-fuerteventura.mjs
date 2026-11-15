// Descarga la costa de Fuerteventura (OpenStreetMap, ODbL) y la simplifica para el minimapa.
// Uso: node scripts/import-fuerteventura.mjs   -> public/data/fuerteventura-coast.json
import { writeFileSync } from "node:fs";
const bb = "27.99,-14.60,28.80,-13.75";
const q = `[out:json][timeout:120];way["natural"="coastline"](${bb});out geom;`;
const res = await fetch("https://overpass-api.de/api/interpreter", { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "IslandCrew-import/1.0 (hola@islandcrew.es)" }, body: "data=" + encodeURIComponent(q) });
if (!res.ok) { console.error("Overpass", res.status); process.exit(1); }
const j = await res.json();
const ways = j.elements.filter((e) => e.geometry && e.geometry.length > 1).map((e) => e.geometry.map((g) => [g.lat, g.lon]));
// Douglas-Peucker en grados (tolerancia ~120 m)
const tol = 0.0011;
function dp(p, t) { if (p.length < 3) return p; const [a, b] = [p[0], p[p.length - 1]]; let m = 0, k = 0; const dx = b[1] - a[1], dy = b[0] - a[0], L = Math.hypot(dx, dy) || 1e-12; for (let i = 1; i < p.length - 1; i++) { const d = Math.abs((p[i][1] - a[1]) * dy - (p[i][0] - a[0]) * dx) / L; if (d > m) { m = d; k = i; } } if (m <= t) return [a, b]; return [...dp(p.slice(0, k + 1), t).slice(0, -1), ...dp(p.slice(k), t)]; }
const out = ways.map((w) => dp(w, tol).map(([la, lo]) => [Math.round(la * 1e4) / 1e4, Math.round(lo * 1e4) / 1e4])).filter((w) => w.length >= 2);
writeFileSync("public/data/fuerteventura-coast.json", JSON.stringify({ attribution: "© Colaboradores de OpenStreetMap (ODbL)", fetched: new Date().toISOString(), ways: out }));
console.log("OK tramos:", out.length, "puntos:", out.reduce((s, w) => s + w.length, 0));
