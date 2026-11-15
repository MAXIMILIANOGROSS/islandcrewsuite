// Auditoría ejecutable de autonomía. Cada punto se clasifica VERIFIED / PARTIAL / BLOCKED con su evidencia.
// Uso: node scripts/autonomy/auditoria-autonomia.mjs [--json]   (con SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY en el entorno comprueba también producción; nunca los imprime)
import fs from "node:fs"; import { execSync } from "node:child_process";
const hay = (p) => fs.existsSync(p); const out = [];
const punto = (id, estado, evidencia) => out.push({ id, estado, evidencia });
// 1. Código presente
punto("cola_durable_codigo", hay("src/lib/ciclos/tareas.ts") && hay("TODO_CORRER_130_CICLO_TAREAS.sql") ? "PARTIAL" : "BLOCKED", "módulo y SQL en el repo (la ejecución real se comprueba abajo)");
punto("worker_y_siguiente_ciclo", hay("src/lib/ciclos/ejecutar.ts") ? "PARTIAL" : "BLOCKED", "pasoDelBucle presente");
punto("decision_con_memoria", hay("src/lib/ciclos/decision.ts") ? "PARTIAL" : "BLOCKED", "decidir() presente");
const cableado = hay("src/lib/oficina/correrCiclo.ts") && /pasoDelBucle/.test(fs.readFileSync("src/lib/oficina/correrCiclo.ts", "utf8"));
punto("bucle_cableado_al_cron", cableado ? "PARTIAL" : "BLOCKED", cableado ? "correrCiclo invoca pasoDelBucle" : "no cableado");
const decCableada = /ciclos\/decision/.test(fs.readFileSync("src/lib/oficina/correrCiclo.ts", "utf8"));
punto("memoria_influye_en_ciclo_real", decCableada ? "PARTIAL" : "BLOCKED", decCableada ? "decidir() se llama desde el ciclo" : "decidir() existe pero NO se llama desde el ciclo real");
// 2. Pruebas
try { const r = execSync("node --experimental-strip-types --test tests/ciclos-tareas.test.mjs tests/ciclos-ejecutar.test.mjs tests/ciclos-decision.test.mjs 2>&1", { encoding: "utf8" }); const f = /# fail (\d+)/.exec(r)?.[1], p = /# pass (\d+)/.exec(r)?.[1]; punto("pruebas_del_bucle", f === "0" ? "VERIFIED" : "FAILED", `pass=${p} fail=${f}`); } catch (e) { punto("pruebas_del_bucle", "FAILED", String(e.message).slice(0, 120)); }
// 3. Producción (opcional)
const url = process.env.SUPABASE_URL || process.env.NEXT_PUBLIC_SUPABASE_URL, key = process.env.SUPABASE_SERVICE_ROLE_KEY;
if (!url || !key) { for (const id of ["tabla_ciclo_tareas_en_produccion", "ciclo_completado_en_produccion", "siguiente_ciclo_programado", "recuperacion_real_registrada"]) punto(id, "BLOCKED", "sin SUPABASE_URL/SUPABASE_SERVICE_ROLE_KEY en el entorno"); }
else {
  const q = async (path) => { const r = await fetch(`${url}/rest/v1/${path}`, { headers: { apikey: key, Authorization: `Bearer ${key}` } }); return r.ok ? r.json() : null; };
  const ts = await q("ciclo_tareas?select=tipo,clave,estado,proxima,intentos&order=creada.desc&limit=50");
  punto("tabla_ciclo_tareas_en_produccion", ts ? "VERIFIED" : "BLOCKED", ts ? `${ts.length} filas` : "tabla ausente o sin acceso: ejecuta el SQL 130");
  punto("ciclo_completado_en_produccion", ts?.some((t) => t.estado === "COMPLETED") ? "VERIFIED" : "PARTIAL", "al menos una tarea COMPLETED");
  punto("siguiente_ciclo_programado", ts?.some((t) => t.estado === "PENDING" && new Date(t.proxima) > new Date()) ? "VERIFIED" : "PARTIAL", "hay una PENDING con fecha futura");
  const tr = await q("ciclo_transiciones?select=motivo&motivo=ilike.*lease%20caducado*&limit=1");
  punto("recuperacion_real_registrada", tr?.length ? "VERIFIED" : "PARTIAL", tr?.length ? "hay una recuperación por lease caducado" : "ninguna recuperación real registrada todavía");
}
if (process.argv.includes("--json")) console.log(JSON.stringify(out, null, 2)); else for (const o of out) console.log(`${o.estado.padEnd(9)} ${o.id} — ${o.evidencia}`);
process.exit(out.some((o) => o.estado === "FAILED") ? 1 : 0);
