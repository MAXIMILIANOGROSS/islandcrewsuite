#!/usr/bin/env bash
# Volcado completo de la base de datos de Supabase a backups/ (esa carpeta NO se sube a GitHub: contiene datos personales).
# Necesita pg_dump y la variable DATABASE_URL (Supabase → Project Settings → Database → Connection string). Uso: DATABASE_URL='postgresql://...' bash scripts/backup-db.sh
set -e
cd "$(dirname "$0")/.."
: "${DATABASE_URL:?Falta DATABASE_URL}"
mkdir -p backups
f="backups/supabase-$(date +%Y-%m-%d_%H%M).sql"
pg_dump "$DATABASE_URL" --no-owner --no-privileges -f "$f"
echo "Copia creada: $f (guárdala en un disco externo o en la nube privada, no en GitHub)."
