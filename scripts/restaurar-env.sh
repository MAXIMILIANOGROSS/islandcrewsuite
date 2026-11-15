#!/usr/bin/env bash
# Descifra .env.local.enc y recrea .env.local. Uso: bash scripts/restaurar-env.sh
set -e
cd "$(dirname "$0")/.."
[ -f .env.local.enc ] || { echo "No existe .env.local.enc"; exit 1; }
[ -f .env.local ] && { echo ".env.local ya existe; no lo sobrescribo."; exit 1; }
openssl enc -d -aes-256-cbc -pbkdf2 -iter 200000 -in .env.local.enc -out .env.local
echo "Listo: .env.local recreado."
