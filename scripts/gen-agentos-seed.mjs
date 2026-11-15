// Genera las filas de agent_registry desde la fuente única src/lib/agents/registry.ts (los 32 roles reales). Uso: node scripts/gen-agentos-seed.mjs
import { AGENTS } from "../src/lib/agents/registry.ts";
const q = (s) => `'${String(s).replace(/'/g, "''")}'`;
const rows = AGENTS.map((a) => `  (${q("AGENT-" + String(a.id).padStart(3, "0"))}, ${q(a.key)}, ${q(a.name)}, ${q(a.area)}, ${q(a.mission)}, ${q(a.kpi)}, ${q(a.defaultMode)}, ${a.phase}, ${a.phase === 1 ? "'active'" : "'registered'"})`);
console.log(`insert into public.agent_registry (agent_id, key, name, area, mission, kpi, mode, phase, status) values\n${rows.join(",\n")}\non conflict (agent_id) do update set name = excluded.name, area = excluded.area, mission = excluded.mission, kpi = excluded.kpi, mode = excluded.mode, phase = excluded.phase, updated_at = now();`);
