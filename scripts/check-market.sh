#!/bin/bash
# Prueba rapida del Market desde fuera (como un visitante sin cuenta). Uso: bash scripts/check-market.sh
cd "$(dirname "$0")/.." || exit 1
SITE="${SITE:-https://islandcrew.es}"
set -a; [ -f .env.local ] && . ./.env.local; set +a
URL="$NEXT_PUBLIC_SUPABASE_URL"; KEY="${NEXT_PUBLIC_SUPABASE_ANON_KEY:-$NEXT_PUBLIC_SUPABASE_KEY}"
[ -z "$URL" ] || [ -z "$KEY" ] && { echo "Falta NEXT_PUBLIC_SUPABASE_URL o NEXT_PUBLIC_SUPABASE_KEY en .env.local"; exit 1; }
pass=0; fail=0
ok()  { echo "  ✅ $1"; pass=$((pass+1)); }
bad() { echo "  ❌ $1"; fail=$((fail+1)); }
rest() { curl -s -m 20 -o /tmp/mk_body -w "%{http_code}" -H "apikey: $KEY" -H "Authorization: Bearer $KEY" "$URL/rest/v1/$1"; }

echo "== Web (visitante sin cuenta) =="
for p in /marketplace /marketplace/wanted /marketplace/sell /marketplace/mine /business-engine /invertir /producto /vision; do
  c=$(curl -s -m 20 -o /dev/null -w "%{http_code}" "$SITE$p"); [ "$c" = "200" ] && ok "$p -> $c" || bad "$p -> $c (esperado 200)"
done
c=$(curl -s -m 20 -o /dev/null -w "%{http_code}" "$SITE/marketplace/rent"); [ "$c" = "200" ] && ok "/marketplace/rent -> $c" || bad "/marketplace/rent -> $c"
c=$(curl -s -m 20 -o /dev/null -w "%{http_code}" "$SITE/marketplace/00000000-0000-0000-0000-000000000000"); [ "$c" = "200" ] && ok "ficha inexistente carga sin romper -> $c" || bad "ficha inexistente -> $c"
curl -s -m 20 "$SITE/" | grep -qi "/marketplace" && ok "el footer enlaza al Market" || bad "no veo /marketplace en el footer de la home"
curl -s -m 20 "$SITE/sitemap.xml" | grep -q "/marketplace" && ok "sitemap incluye /marketplace" || bad "sitemap sin /marketplace"

echo "== Base de datos (rol anonimo) =="
c=$(rest "market_categories?select=slug"); n=$(python3 -c "import json;print(len(json.load(open('/tmp/mk_body'))))" 2>/dev/null)
[ "$c" = "200" ] && [ "$n" = "14" ] && ok "14 categorias visibles" || bad "categorias: http $c, $n (esperado 200 y 14)"
c=$(rest "market_items_public?select=id,title&limit=5"); [ "$c" = "200" ] && ok "vista publica de anuncios responde ($(python3 -c "import json;print(len(json.load(open('/tmp/mk_body'))))" 2>/dev/null) publicados)" || bad "vista publica: http $c"
c=$(rest "market_items_public?select=owner&limit=1"); [ "$c" != "200" ] && ok "la vista publica NO expone owner" || bad "la vista publica expone owner"
c=$(rest "market_wanted_public?select=id,title&limit=5"); [ "$c" = "200" ] && ok "busquedas publicas responden" || bad "busquedas publicas: http $c"
c=$(rest "market_wanted_public?select=user_id&limit=1"); [ "$c" != "200" ] && ok "las busquedas NO exponen user_id" || bad "las busquedas exponen user_id"
for t in market_items market_orders market_rentals market_handovers market_disputes market_favorites market_reports market_wanted market_reviews; do
  c=$(rest "$t?select=*&limit=1"); body=$(cat /tmp/mk_body)
  if [ "$c" = "401" ] || [ "$c" = "403" ] || [ "$body" = "[]" ]; then ok "anon no ve datos de $t"; else bad "anon podria leer $t (http $c)"; fi
done
c=$(curl -s -m 20 -o /tmp/mk_body -w "%{http_code}" -X POST -H "apikey: $KEY" -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d '{}' "$URL/rest/v1/rpc/market_admin_stats")
[ "$c" != "200" ] && ok "anon no puede llamar market_admin_stats (http $c)" || bad "anon pudo llamar market_admin_stats"
c=$(curl -s -m 20 -o /tmp/mk_body -w "%{http_code}" -X POST -H "apikey: $KEY" -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -d '{"p_item":"00000000-0000-0000-0000-000000000000","p_body":"hola"}' "$URL/rest/v1/rpc/market_contact")
[ "$c" != "200" ] && ok "anon no puede contactar (http $c)" || bad "anon pudo llamar market_contact"
c=$(curl -s -m 20 -o /tmp/mk_body -w "%{http_code}" -X POST -H "apikey: $KEY" -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" -H "Prefer: return=minimal" -d '{"title":"hack","category":"otros","can_sell":true,"sale_price":1}' "$URL/rest/v1/market_items")
[ "$c" != "201" ] && ok "anon no puede crear anuncios (http $c)" || bad "anon pudo crear un anuncio"

echo
echo "Resultado: $pass ok, $fail fallos"
[ "$fail" = "0" ]
