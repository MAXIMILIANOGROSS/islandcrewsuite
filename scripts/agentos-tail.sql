
-- Utilidades internas -------------------------------------------------------------------------------------------------------------
create or replace function public.aos__count(p_table text, p_where text default 'true') returns bigint language plpgsql security definer set search_path = public as $$
declare n bigint;
begin
  if to_regclass('public.' || p_table) is null then return null; end if;      -- tabla inexistente = dato NO DISPONIBLE (nunca 0 inventado)
  execute format('select count(*) from public.%I where %s', p_table, p_where) into n;
  return n;
end $$;
revoke all on function public.aos__count(text,text) from public, anon, authenticated;

create or replace function public.aos__task(p_run uuid, p_agent text, p_dedupe text, p_obj text, i int, c int, e int, r int) returns void language sql security definer set search_path = public as $$
  insert into agent_tasks (dedupe_key, agent_id, objective, impact, confidence, effort, risk, mode, status, source_run)
  select p_dedupe, a.agent_id, p_obj, i, c, e, r, 'verde', 'PROPOSED', p_run from agent_registry a where a.key = p_agent and a.status = 'active'
  on conflict (dedupe_key) where dedupe_key is not null and status not in ('DONE','FAILED') do update set objective = excluded.objective, updated_at = now(); $$;
revoke all on function public.aos__task(uuid,text,text,text,int,int,int,int) from public, anon, authenticated;

-- Ciclo (OBSERVAR → DIAGNOSTICAR → PROPONER → INFORMAR). Determinista: no llama a ninguna IA, no contacta personas, no publica, no cambia producción. ------
create or replace function public.aos__cycle(p_trigger text) returns jsonb language plpgsql security definer set search_path = public as $$
declare s agent_settings; rk text; rid uuid; used text[]; rep text; obs jsonb;
  n_rep bigint; n_rep24 bigint; n_jrep bigint; n_apps bigint; n_unv bigint; n_plus bigint; n_posts24 bigint; n_rew24 bigint; cost_today int;
begin
  select * into s from agent_settings where id;
  rk := to_char(date_trunc('hour', now() at time zone 'Europe/Madrid'), 'YYYY-MM-DD"T"HH24');
  if p_trigger = 'manual' then rk := rk || '#manual-' || to_char(now() at time zone 'Europe/Madrid', 'MI'); end if;
  if s.paused then
    insert into agent_runs (run_key, kind, status, report, finished_at) values (rk || '#paused', p_trigger, 'SKIPPED', 'Omitido: el sistema está en pausa (parada de emergencia activa).', now()) on conflict (run_key) do nothing;
    perform aos__audit('cycle_skipped', jsonb_build_object('reason', 'paused', 'trigger', p_trigger));
    return jsonb_build_object('status', 'SKIPPED', 'reason', 'pausado');
  end if;
  select coalesce(sum(cost_cents), 0) into cost_today from agent_runs where started_at > date_trunc('day', now() at time zone 'Europe/Madrid') at time zone 'Europe/Madrid';
  if s.daily_budget_cents > 0 and cost_today >= s.daily_budget_cents then
    insert into agent_runs (run_key, kind, status, report, finished_at) values (rk || '#budget', p_trigger, 'SKIPPED', 'Omitido: presupuesto diario agotado.', now()) on conflict (run_key) do nothing;
    return jsonb_build_object('status', 'SKIPPED', 'reason', 'presupuesto');
  end if;
  insert into agent_runs (run_key, kind, status) values (rk, p_trigger, 'RUNNING') on conflict (run_key) do nothing returning id into rid;
  if rid is null then return jsonb_build_object('status', 'ALREADY', 'run_key', rk); end if;      -- ya ejecutado esta hora: no se duplica
  begin
    n_rep := aos__count('net_reports'); n_rep24 := aos__count('net_reports', 'created_at > now() - interval ''1 day''');
    n_jrep := aos__count('job_reports');
    n_apps := aos__count('job_applications', 'status in (''enviada'',''recibida'') and created_at < now() - interval ''7 days''');
    n_unv := aos__count('business_accounts', 'not verified');
    n_plus := aos__count('plus_interest');
    n_posts24 := aos__count('net_posts', 'created_at > now() - interval ''1 day'' and deleted_at is null');
    n_rew24 := aos__count('game_rewards', 'created_at > now() - interval ''1 day''');
    obs := jsonb_build_object('net_reports_total', n_rep, 'net_reports_24h', n_rep24, 'job_reports_total', n_jrep, 'applications_unanswered_7d', n_apps,
      'businesses_unverified', n_unv, 'plus_responses', n_plus, 'net_posts_24h', n_posts24, 'game_rewards_24h', n_rew24);
    if coalesce(n_rep, 0) > 0 then perform aos__task(rid, 'auditor', 'review-net-reports', 'Revisar ' || n_rep || ' denuncias de Network y resolver las pendientes', 4, 4, 2, 2); end if;
    if coalesce(n_jrep, 0) > 0 then perform aos__task(rid, 'auditor', 'review-job-reports', 'Revisar ' || n_jrep || ' denuncias de ofertas de empleo', 4, 4, 2, 2); end if;
    if coalesce(n_apps, 0) > 0 then perform aos__task(rid, 'ceo', 'unanswered-applications', 'Hay ' || n_apps || ' candidaturas sin responder tras más de 7 días: avisar a los negocios (la acción la haces tú)', 4, 5, 1, 1); end if;
    if coalesce(n_unv, 0) > 0 then perform aos__task(rid, 'auditor', 'unverified-businesses', 'Revisar ' || n_unv || ' negocios pendientes de verificación', 3, 4, 2, 2); end if;
    select coalesce(array_agg(key order by key), '{}') into used from (select key from agent_registry where key in ('analitica','auditor','ceo') and status = 'active' limit s.max_agents_per_cycle) u;
    update agent_registry set last_run_at = now() where key = any(used);
    rep := 'Ciclo ' || rk || ' (' || p_trigger || '). Reglas deterministas, sin IA, coste 0. Roles: ' || coalesce(nullif(array_to_string(used, ', '), ''), 'ninguno activo') || E'.\n'
      || 'Denuncias Network: ' || coalesce(n_rep::text, 'no disponible') || ' (24 h: ' || coalesce(n_rep24::text, 'no disponible') || '). '
      || 'Denuncias de ofertas: ' || coalesce(n_jrep::text, 'no disponible') || '. '
      || 'Candidaturas sin responder >7 d: ' || coalesce(n_apps::text, 'no disponible') || '. '
      || 'Negocios sin verificar: ' || coalesce(n_unv::text, 'no disponible') || E'. '
      || 'Respuestas Crew Plus: ' || coalesce(n_plus::text, 'no disponible') || '. '
      || 'Publicaciones 24 h: ' || coalesce(n_posts24::text, 'no disponible') || '. Recompensas de juego 24 h: ' || coalesce(n_rew24::text, 'no disponible') || '.';
    update agent_runs set status = 'DONE', agents_used = used, observations = obs, report = rep, finished_at = now() where id = rid;
    perform aos__audit('cycle_done', jsonb_build_object('run_key', rk, 'trigger', p_trigger));
    return jsonb_build_object('status', 'DONE', 'run_key', rk, 'report', rep);
  exception when others then
    update agent_runs set status = 'FAILED', report = 'Fallo interno del ciclo: ' || left(sqlerrm, 200), finished_at = now() where id = rid;
    return jsonb_build_object('status', 'FAILED');
  end;
end $$;
revoke all on function public.aos__cycle(text) from public, anon, authenticated;

create or replace function public.aos_run_cycle() returns jsonb language plpgsql security definer set search_path = public as $$
begin if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if; return aos__cycle('manual'); end $$;
revoke all on function public.aos_run_cycle() from public, anon; grant execute on function public.aos_run_cycle() to authenticated;
-- Para un futuro programador (pg_cron / n8n con service_role). NO se programa nada en este archivo.
create or replace function public.aos_run_cycle_system() returns jsonb language sql security definer set search_path = public as $$ select public.aos__cycle('schedule'); $$;
revoke all on function public.aos_run_cycle_system() from public, anon, authenticated; grant execute on function public.aos_run_cycle_system() to service_role;

-- Panel de administración (solo administrador) ----------------------------------------------------------------------------------------
create or replace function public.aos_overview() returns jsonb language plpgsql stable security definer set search_path = public as $$
declare cron_n bigint := 0;
begin
  if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if;
  begin execute 'select count(*) from cron.job where jobname = ''aos-hourly''' into cron_n; exception when others then cron_n := 0; end;
  return jsonb_build_object(
    'registered', (select count(*) from agent_registry),
    'by_status', coalesce((select jsonb_object_agg(status, n) from (select status, count(*) n from agent_registry group by 1) t), '{}'::jsonb),
    'tasks', coalesce((select jsonb_object_agg(status, n) from (select status, count(*) n from agent_tasks group by 1) t), '{}'::jsonb),
    'runs_total', (select count(*) from agent_runs where status in ('DONE','FAILED')),
    'last_run', (select to_jsonb(r) - 'observations' from (select run_key, kind, status, agents_used, cost_cents, report, started_at from agent_runs where status <> 'SKIPPED' order by started_at desc limit 1) r),
    'cost_today_cents', (select coalesce(sum(cost_cents), 0) from agent_runs where started_at > date_trunc('day', now() at time zone 'Europe/Madrid') at time zone 'Europe/Madrid'),
    'settings', (select to_jsonb(s) - 'id' from agent_settings s where id),
    'scheduled', cron_n > 0);
end $$;
revoke all on function public.aos_overview() from public, anon; grant execute on function public.aos_overview() to authenticated;

create or replace function public.aos_agents(p_q text default null) returns table (agent_id text, key text, name text, area text, mission text, kpi text, mode text, phase int, status text, prompt_version int, last_run_at timestamptz, open_tasks int)
language plpgsql stable security definer set search_path = public as $$
declare q text := lower(trim(coalesce(p_q, '')));
begin
  if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if;
  return query select a.agent_id, a.key, a.name, a.area, a.mission, a.kpi, a.mode, a.phase, a.status, a.prompt_version, a.last_run_at,
      (select count(*)::int from agent_tasks t where t.agent_id = a.agent_id and t.status not in ('DONE','FAILED'))
    from agent_registry a where q = '' or lower(a.agent_id || ' ' || a.name || ' ' || a.area || ' ' || a.status || ' ' || a.mission) like '%' || replace(replace(q, '%', ''), '_', '') || '%'
    order by a.agent_id limit 400;
end $$;
revoke all on function public.aos_agents(text) from public, anon; grant execute on function public.aos_agents(text) to authenticated;

create or replace function public.aos_set_agent(p_id text, p_status text) returns void language plpgsql security definer set search_path = public as $$
begin
  if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if;
  if p_status not in ('registered','active','paused','disabled') then raise exception 'BAD_STATUS'; end if;
  update agent_registry set status = p_status, updated_at = now() where agent_id = p_id;
  if not found then raise exception 'NOT_FOUND'; end if;
  perform aos__audit('agent_status', jsonb_build_object('agent', p_id, 'status', p_status));
end $$;
revoke all on function public.aos_set_agent(text,text) from public, anon; grant execute on function public.aos_set_agent(text,text) to authenticated;

create or replace function public.aos_set_settings(p_paused boolean, p_daily int, p_cycle int, p_max int) returns void language plpgsql security definer set search_path = public as $$
begin
  if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if;
  update agent_settings set paused = p_paused, daily_budget_cents = greatest(coalesce(p_daily, 0), 0), cycle_budget_cents = greatest(coalesce(p_cycle, 0), 0),
    max_agents_per_cycle = least(greatest(coalesce(p_max, 5), 1), 20), updated_at = now() where id;
  perform aos__audit('settings', jsonb_build_object('paused', p_paused, 'daily', p_daily, 'cycle', p_cycle, 'max', p_max));
end $$;
revoke all on function public.aos_set_settings(boolean,int,int,int) from public, anon; grant execute on function public.aos_set_settings(boolean,int,int,int) to authenticated;

create or replace function public.aos_tasks(p_status text default null) returns table (id uuid, agent_id text, agent_name text, objective text, mode text, status text, priority numeric, evidence text, approved_by text, blocked_reason text, attempts int, created_at timestamptz, updated_at timestamptz)
language plpgsql stable security definer set search_path = public as $$
begin
  if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if;
  return query select t.id, t.agent_id, a.name, t.objective, t.mode, t.status, round((t.impact * t.confidence)::numeric / (t.effort * (1 + t.risk)), 2), t.evidence, t.approved_by, t.blocked_reason, t.attempts, t.created_at, t.updated_at
    from agent_tasks t join agent_registry a on a.agent_id = t.agent_id where p_status is null or t.status = p_status order by (t.status in ('DONE','FAILED')), 7 desc, t.created_at desc limit 200;
end $$;
revoke all on function public.aos_tasks(text) from public, anon; grant execute on function public.aos_tasks(text) to authenticated;

create or replace function public.aos_task_create(p_agent text, p_objective text, i int, c int, e int, r int, p_mode text) returns uuid language plpgsql security definer set search_path = public as $$
declare tid uuid; aid text;
begin
  if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if;
  select agent_id into aid from agent_registry where key = p_agent; if aid is null then raise exception 'NOT_FOUND'; end if;
  insert into agent_tasks (dedupe_key, agent_id, objective, impact, confidence, effort, risk, mode) values (md5(lower(trim(p_objective))), aid, trim(p_objective), i, c, e, r, p_mode)
  on conflict (dedupe_key) where dedupe_key is not null and status not in ('DONE','FAILED') do nothing returning id into tid;
  if tid is null then raise exception 'DUPLICATE'; end if;
  perform aos__audit('task_create', jsonb_build_object('task', tid));
  return tid;
end $$;
revoke all on function public.aos_task_create(text,text,int,int,int,int,text) from public, anon; grant execute on function public.aos_task_create(text,text,int,int,int,int,text) to authenticated;

-- La aprobación es SIEMPRE humana: se guarda el correo del administrador que la ejecuta; ningún agente puede aprobar.
create or replace function public.aos_task_approve(p_id uuid) returns void language plpgsql security definer set search_path = public as $$
begin
  if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if;
  update agent_tasks set approved_by = auth.jwt() ->> 'email', status = case when status in ('PROPOSED','BACKLOG') then 'APPROVED' else status end, updated_at = now() where id = p_id;
  if not found then raise exception 'NOT_FOUND'; end if;
  perform aos__audit('task_approve', jsonb_build_object('task', p_id));
end $$;
revoke all on function public.aos_task_approve(uuid) from public, anon; grant execute on function public.aos_task_approve(uuid) to authenticated;

create or replace function public.aos_task_status(p_id uuid, p_status text, p_evidence text default null, p_reason text default null) returns void language plpgsql security definer set search_path = public as $$
begin
  if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if;
  update agent_tasks set status = p_status, evidence = coalesce(nullif(trim(p_evidence), ''), evidence), blocked_reason = case when p_status = 'BLOCKED' then nullif(trim(p_reason), '') else null end,
    attempts = attempts + case when p_status = 'FAILED' then 1 else 0 end, updated_at = now() where id = p_id;
  if not found then raise exception 'NOT_FOUND'; end if;
  perform aos__audit('task_status', jsonb_build_object('task', p_id, 'status', p_status));
end $$;
revoke all on function public.aos_task_status(uuid,text,text,text) from public, anon; grant execute on function public.aos_task_status(uuid,text,text,text) to authenticated;

create or replace function public.aos_runs(p_limit int default 30) returns table (run_key text, kind text, status text, agents_used text[], cost_cents int, report text, started_at timestamptz, finished_at timestamptz)
language plpgsql stable security definer set search_path = public as $$
begin
  if not public.housing_is_admin() then raise exception 'FORBIDDEN'; end if;
  return query select r.run_key, r.kind, r.status, r.agents_used, r.cost_cents, r.report, r.started_at, r.finished_at from agent_runs r order by r.started_at desc limit least(greatest(coalesce(p_limit, 30), 1), 100);
end $$;
revoke all on function public.aos_runs(int) from public, anon; grant execute on function public.aos_runs(int) to authenticated;

-- PROGRAMACIÓN HORARIA: NO ACTIVADA. Solo se activa con la frase exacta del fundador:
--   «Sí, activa el informe diario con CEO Digital, Analítica y Auditor, solo con recomendaciones y sin acciones externas.»
-- (cuando se dé, y con pg_cron habilitado en Supabase:)
--   select cron.schedule('aos-hourly', '0 * * * *', $$select public.aos_run_cycle_system()$$);
-- Para quitarla:  select cron.unschedule('aos-hourly');
