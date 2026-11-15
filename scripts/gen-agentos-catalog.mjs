// Genera el SQL que registra los 368 roles nuevos (AGENT-033..400) en agent_registry, estado 'registered'. Uso: node scripts/gen-agentos-catalog.mjs > TODO_CORRER_61_AGENT_CATALOGO_400.sql
import { catalogRoles } from "../src/lib/agents/catalog.ts";
const q = (s) => `'${String(s).replace(/'/g, "''")}'`;
const rs = catalogRoles();
const rows = rs.map((a) => `  (${q(a.agentId)}, ${q(a.key)}, ${q(a.name)}, ${q(a.area)}, ${q(a.mission)}, ${q(a.kpi)}, ${q(a.mode)}, ${a.phase}, 'registered')`);
console.log(`-- ISLAND CREW · Agent OS 400: registra ${rs.length} roles nuevos (AGENT-033 a AGENT-400). Son definiciones: ninguno se ejecuta solo ni queda activo. Ya existentes: no se tocan.\ninsert into public.agent_registry (agent_id, key, name, area, mission, kpi, mode, phase, status) values\n${rows.join(",\n")}\non conflict do nothing;\nselect count(*) as roles_registrados from public.agent_registry;`);
