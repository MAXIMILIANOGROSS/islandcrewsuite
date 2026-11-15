#!/usr/bin/env bash
# Descifra una copia de copias-cifradas/ y deja el .sql en backups/. Uso: bash scripts/restaurar-backup.sh copias-cifradas/ARCHIVO.sql.gz.enc
set -e
cd "$(dirname "$0")/.."
in="${1:?Indica el archivo .enc}"
mkdir -p backups
out="backups/$(basename "$in" .sql.gz.enc)-restaurado.sql"
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in "$in" | gunzip > "$out"
echo "Listo: $out (restáuralo con psql en un proyecto de Supabase nuevo)."
