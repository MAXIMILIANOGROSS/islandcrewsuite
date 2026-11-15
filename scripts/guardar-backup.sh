#!/usr/bin/env bash
# Comprime y CIFRA el último volcado de backups/ y lo deja en copias-cifradas/ (esa carpeta SÍ se sube a GitHub; el volcado sin cifrar NO).
# Uso: bash scripts/guardar-backup.sh   (te pide una contraseña; guárdala en tu gestor de contraseñas)
set -e
cd "$(dirname "$0")/.."
f=$(ls -t backups/supabase-*.sql 2>/dev/null | head -1)
[ -n "$f" ] || { echo "No hay volcados en backups/. Ejecuta antes scripts/backup-db.sh"; exit 1; }
mkdir -p copias-cifradas
out="copias-cifradas/$(basename "$f" .sql).sql.gz.enc"
gzip -c "$f" | openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt -out "$out"
echo "Listo: $out ($(du -h "$out" | cut -f1)). Ya puedes subirlo con git add/commit/push."
