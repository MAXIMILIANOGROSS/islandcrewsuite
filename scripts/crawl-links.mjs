// Recorre TODAS las paginas internas enlazadas (sitemap + enlaces de cada pagina) y comprueba que ninguna da error.
// Uso: node scripts/crawl-links.mjs [URL_BASE] [concurrencia]   (por defecto https://islandcrew.es y 4: educado con produccion)
const BASE = (process.argv[2] || "https://islandcrew.es").replace(/\/$/, "");
const CONC = Math.max(1, Math.min(10, Number(process.argv[3] || 4)));
const seen = new Map(); const queue = []; const bad = [];
const norm = (u) => { try { const x = new URL(u, BASE); if (x.origin !== BASE) return null; x.hash = ""; x.search = ""; return x.pathname.replace(/\/$/, "") || "/"; } catch { return null; } };
const add = (p) => { if (p && !seen.has(p) && !/\.(png|jpe?g|webp|svg|gif|ico|pdf|mp4|webm|xml|txt|json|js|css|woff2?)$/i.test(p) && !p.startsWith("/api/") && !p.startsWith("/_next")) { seen.set(p, null); queue.push(p); } };
const sm = await fetch(BASE + "/sitemap.xml").then((r) => r.text()).catch(() => ""); for (const m of sm.matchAll(/<loc>([^<]+)<\/loc>/g)) add(norm(m[1]));
["/", "/marketplace", "/housing", "/actividad", "/nivel", "/notificaciones", "/cuenta/identidad", "/empresa/nueva", "/business-engine", "/invertir"].forEach(add);
async function worker() {
  while (queue.length) {
    const p = queue.shift();
    try {
      const r = await fetch(BASE + p, { redirect: "follow", headers: { "user-agent": "IslandCrewLinkCheck/1.0" } }); seen.set(p, r.status);
      if (r.status >= 400) bad.push([p, r.status]);
      else if ((r.headers.get("content-type") || "").includes("text/html")) { const h = await r.text(); for (const m of h.matchAll(/href="([^"#]+)"/g)) add(norm(m[1])); }
    } catch (e) { seen.set(p, 0); bad.push([p, "sin respuesta"]); }
  }
}
await Promise.all(Array.from({ length: CONC }, worker));
console.log(`Paginas revisadas: ${seen.size}`); console.log(bad.length ? "FALLOS:\n" + bad.map(([p, s]) => `  ${s}  ${p}`).join("\n") : "Todas responden correctamente.");
process.exit(bad.length ? 1 : 0);
