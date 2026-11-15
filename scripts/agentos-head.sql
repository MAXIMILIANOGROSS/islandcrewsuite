-- ISLAND CREW · 60 · AGENT OS (MVP honesto): registro de roles, tareas, ciclo, presupuesto, auditoría y parada de emergencia.
-- Requiere housing_is_admin() (SQL 14). Todo se gestiona SOLO por el administrador mediante funciones; las tablas tienen RLS cerrada.
-- HOY el ciclo ejecuta REGLAS deterministas sobre datos reales (sin IA, coste 0). El registro admite hasta AGENT-400; ahora contiene los 32 roles reales del repositorio.
-- NO se programa ninguna ejecución automática: arranca en pausa. Ver el bloque comentado de pg_cron al final.

create table if not exists public.agent_registry (
  agent_id text primary key check (agent_id ~ '^AGENT-[0-9]{3}$'),
  key text not null unique,
  name text not null, area text not null, mission text not null, kpi text not null,
  mode text not null check (mode in ('verde','ambar','rojo')),
  phase int not null check (phase between 1 and 4),
  status text not null default 'registered' check (status in ('registered','active','paused','disabled')),
  prompt_version int not null default 1,
  tools text[] not null default '{}',
  max_budget_cents int not null default 0 check (max_budget_cents >= 0),
  last_run_at timestamptz, next_review_at timestamptz,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now());
alter table public.agent_registry enable row level security; revoke all on public.agent_registry from anon, authenticated;

create table if not exists public.agent_settings (
  id boolean primary key default true check (id),
  paused boolean not null default true,                       -- parada de emergencia: arranca pausado
  daily_budget_cents int not null default 0 check (daily_budget_cents >= 0),
  cycle_budget_cents int not null default 0 check (cycle_budget_cents >= 0),
  max_agents_per_cycle int not null default 5 check (max_agents_per_cycle between 1 and 20),
  updated_at timestamptz not null default now());
insert into public.agent_settings (id) values (true) on conflict do nothing;
alter table public.agent_settings enable row level security; revoke all on public.agent_settings from anon, authenticated;

create table if not exists public.agent_tasks (
  id uuid primary key default gen_random_uuid(),
  dedupe_key text,
  agent_id text not null references public.agent_registry(agent_id),
  objective text not null check (char_length(objective) between 5 and 400),
  impact int not null check (impact between 1 and 5), confidence int not null check (confidence between 1 and 5),
  effort int not null check (effort between 1 and 5), risk int not null check (risk between 1 and 5),
  mode text not null check (mode in ('verde','ambar','rojo')),
  status text not null default 'PROPOSED' check (status in ('BACKLOG','PROPOSED','APPROVED','READY','RUNNING','BLOCKED','REVIEW','DONE','FAILED')),
  evidence text, approved_by text, blocked_reason text,
  attempts int not null default 0 check (attempts between 0 and 3),
  source_run uuid,
  created_at timestamptz not null default now(), updated_at timestamptz not null default now(),
  check (status <> 'DONE' or char_length(trim(coalesce(evidence, ''))) > 0),                       -- nada se completa sin evidencia
  check (mode = 'verde' or status not in ('RUNNING','DONE') or approved_by is not null),            -- ámbar/rojo exigen aprobación humana
  check (status <> 'BLOCKED' or char_length(trim(coalesce(blocked_reason, ''))) > 0));
create unique index if not exists agent_tasks_dedupe_ix on public.agent_tasks (dedupe_key) where dedupe_key is not null and status not in ('DONE','FAILED');
alter table public.agent_tasks enable row level security; revoke all on public.agent_tasks from anon, authenticated;

create table if not exists public.agent_runs (
  id uuid primary key default gen_random_uuid(),
  run_key text not null unique,                              -- una ejecución por hora (Europe/Madrid): idempotente
  kind text not null check (kind in ('manual','schedule')),
  status text not null check (status in ('RUNNING','DONE','SKIPPED','FAILED')),
  agents_used text[] not null default '{}',
  cost_cents int not null default 0,
  observations jsonb not null default '{}'::jsonb,
  report text,
  started_at timestamptz not null default now(), finished_at timestamptz);
alter table public.agent_runs enable row level security; revoke all on public.agent_runs from anon, authenticated;

create table if not exists public.agent_audit (
  id bigserial primary key, at timestamptz not null default now(), actor text not null, action text not null, detail jsonb not null default '{}'::jsonb);
alter table public.agent_audit enable row level security; revoke all on public.agent_audit from anon, authenticated;

create or replace function public.aos__audit(p_action text, p_detail jsonb default '{}'::jsonb) returns void language sql security definer set search_path = public as $$
  insert into agent_audit (actor, action, detail) values (coalesce(nullif(auth.jwt() ->> 'email', ''), 'sistema'), p_action, coalesce(p_detail, '{}'::jsonb)); $$;
revoke all on function public.aos__audit(text,jsonb) from public, anon, authenticated;

-- Roles reales (generados desde src/lib/agents/registry.ts) ---------------------------------------------------------------------
