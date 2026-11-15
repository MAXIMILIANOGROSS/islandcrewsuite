#!/bin/bash
# Comprobacion de identidad unica desde fuera (visitante sin cuenta). Uso: bash scripts/check-identity.sh
cd "$(dirname "$0")/.." || exit 1
SITE="${SITE:-https://islandcrew.es}"
set -a; [ -f .env.local ] && . ./.env.local; set +a
URL="$NEXT_PUBLIC_SUPABASE_URL"; KEY="${NEXT_PUBLIC_SUPABASE_ANON_KEY:-$NEXT_PUBLIC_SUPABASE_KEY}"
[ -z "$URL" ] || [ -z "$KEY" ] && { echo "Falta NEXT_PUBLIC_SUPABASE_URL o la clave publica en .env.local"; exit 1; }
pass=0; fail=0
ok()  { echo "  ✅ $1"; pass=$((pass+1)); }
bad() { echo "  ❌ $1"; fail=$((fail+1)); }
rest() { curl -s -m 20 -o /tmp/id_body -w "%{http_code}" -H "apikey: $KEY" -H "Authorization: Bearer $KEY" "$URL/rest/v1/$1"; }
rpc()  { curl -s -m 20 -o /tmp/id_body -w "%{http_code}" -X POST -H "apikey: $KEY" -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d "$2" "$URL/rest/v1/rpc/$1"; }
echo "== Paginas (cargan sin romper; piden login dentro) =="
for p in /actividad /notificaciones /nivel /cuenta/identidad /empresa/nueva /admin/identidad /marketplace/crew/00000000-0000-0000-0000-000000000000 /u/00000000-0000-0000-0000-000000000000 /empresa/00000000-0000-0000-0000-000000000000 /housing/notifications /marketplace /business-engine; do
  c=$(curl -s -L -m 20 -o /dev/null -w "%{http_code}" "$SITE$p"); [ "$c" = "200" ] && ok "$p -> $c" || bad "$p -> $c (esperado 200)"
done
echo "== Base de datos (rol anonimo) =="
for t in user_roles trust_signals business_accounts business_members business_audit crew_market_items crew_market_votes employment_records xp_events points_ledger badges_awarded; do
  c=$(rest "$t?select=*&limit=1"); body=$(cat /tmp/id_body)
  if [ "$c" = "401" ] || [ "$c" = "403" ] || [ "$body" = "[]" ]; then ok "anon no ve datos de $t"; else bad "anon podria leer $t (http $c)"; fi
done
c=$(rest "badge_catalog?select=code"); [ "$c" = "200" ] && ok "catalogo de badges publico" || bad "catalogo de badges: http $c"
for f in my_activity levels_sync trust_summary identity_card business_create admin_find_user; do
  c=$(rpc "$f" '{}'); [ "$c" != "200" ] && ok "anon no puede llamar $f (http $c)" || bad "anon pudo llamar $f"
done
c=$(rpc "employment_create" '{"p_worker_email":"x@x.es","p_start":"2026-01-01"}'); [ "$c" != "200" ] && ok "anon no puede registrar empleos (http $c)" || bad "anon pudo registrar un empleo"
echo; echo "Resultado: $pass ok, $fail fallos"; [ "$fail" = "0" ]
