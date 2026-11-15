// Prueba de carga con bots (Supabase Realtime). Uso: NEXT_PUBLIC_SUPABASE_URL=... NEXT_PUBLIC_SUPABASE_KEY=... node scripts/loadtest-bots.mjs 20 30 [instancia]
// Mide: bots conectados, errores, mensajes recibidos/s por bot y latencia de entrega (bot 0 -> resto). NO sustituye a la prueba con personas reales.
import { createClient } from "@supabase/supabase-js";
const N = parseInt(process.argv[2] || "10", 10), SECS = parseInt(process.argv[3] || "30", 10), INST = process.argv[4] || "9";
const url = process.env.NEXT_PUBLIC_SUPABASE_URL, key = process.env.NEXT_PUBLIC_SUPABASE_KEY;
if (!url || !key) { console.error("Faltan NEXT_PUBLIC_SUPABASE_URL / NEXT_PUBLIC_SUPABASE_KEY"); process.exit(1); }
const stats = { joined: 0, errors: 0, sent: 0, recv: 0, lat: [] };
const bots = [];
for (let i = 0; i < N; i++) {
  const sb = createClient(url, key, { realtime: { params: { eventsPerSecond: 20 } } });
  const id = "bot" + String(i).padStart(4, "0") + "x";
  const ch = sb.channel(`world-corralejo-${INST}`, { config: { broadcast: { self: false } } });
  ch.on("broadcast", { event: "pos" }, ({ payload }) => { stats.recv++; if (payload?.t) stats.lat.push(Date.now() - payload.t); });
  ch.subscribe((st) => { if (st === "SUBSCRIBED") stats.joined++; if (st === "CHANNEL_ERROR" || st === "TIMED_OUT") stats.errors++; });
  bots.push({ sb, ch, id, x: Math.random() * 100, z: Math.random() * 100, a: Math.random() * 6.28 });
  await new Promise((r) => setTimeout(r, 50));
}
const iv = setInterval(() => { for (const b of bots) { b.a += (Math.random() - 0.5) * 0.4; b.x += Math.cos(b.a) * 1.2; b.z += Math.sin(b.a) * 1.2; b.ch.send({ type: "broadcast", event: "pos", payload: { id: b.id, alias: "Bot", x: b.x, z: b.z, yaw: b.a, t: Date.now() } }); stats.sent++; } }, 200);
await new Promise((r) => setTimeout(r, SECS * 1000)); clearInterval(iv);
stats.lat.sort((a, b) => a - b); const pct = (p) => stats.lat.length ? stats.lat[Math.floor(stats.lat.length * p)] : null;
console.log(JSON.stringify({ bots: N, secs: SECS, joined: stats.joined, errors: stats.errors, sentPerSec: Math.round(stats.sent / SECS), recvPerSec: Math.round(stats.recv / SECS), latencyMs: { p50: pct(0.5), p95: pct(0.95), max: stats.lat.at(-1) ?? null }, verdict: stats.joined === N && stats.errors === 0 ? "PASS (solo conexion/entrega; revisa latencia)" : "FAIL" }, null, 2));
for (const b of bots) b.sb.removeChannel(b.ch); process.exit(0);
