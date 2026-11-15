#!/usr/bin/env bash
# Cifra .env.local con TU contraseña y deja .env.local.enc (esa copia sí se sube a GitHub). Uso: bash scripts/guardar-env.sh
set -e
cd "$(dirname "$0")/.."
[ -f .env.local ] || { echo "No existe .env.local"; exit 1; }
openssl enc -aes-256-cbc -pbkdf2 -iter 200000 -salt -in .env.local -out .env.local.enc
echo "Listo: .env.local.enc creado. Guarda la contraseña en tu gestor de contraseñas (sin ella no se puede recuperar)."
