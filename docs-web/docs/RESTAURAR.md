# Cómo recuperar Island Crew desde cero

Qué guarda GitHub y qué no:

| Pieza | Dónde está |
|---|---|
| Código de la web | Este repositorio privado |
| Estructura de la base de datos (SQL) | `supabase/` y `supabase/sql-island-crew/` (ejecutar en orden, ver abajo) |
| Documentos de empresa y calidad (PDF) | `public/documentos/` |
| Claves y variables | `.env.local.enc` (cifrado con tu contraseña) + Vercel y GitHub Secrets |
| Datos de usuarios, ofertas, leads, certificados | Supabase. Copia en `copias-cifradas/` (cifrada con tu contraseña): se genera con `backup-db.sh` y luego `guardar-backup.sh`; se descifra con `restaurar-backup.sh` |
| Fotos subidas (Supabase Storage) | Supabase. Hay que copiarlas aparte |

## Pasos
1. `git clone` del repositorio y `npm install`.
2. `bash scripts/restaurar-env.sh` (pide tu contraseña) para recrear `.env.local`.
3. En un proyecto nuevo de Supabase, ejecutar los SQL de `supabase/sql-island-crew/` en este orden: PARTE_1, 2, 3, 4, 5, 6 y por último COMPROBAR_FALTANTES (debe devolver 0 filas). Después `supabase/MAXI_OS.sql` y `supabase/HIVE.sql y supabase/GROWTH.sql` (memoria colectiva de las cabras).
4. Restaurar los datos con la copia de `backup-db.sh` (si existe).
5. Variables en Vercel y secretos en GitHub (`CRON_SECRET`, etc.), copiándolos de `.env.local`.
6. `npm run dev` para comprobar.

## Rutina recomendada
- Cada vez que cambies claves: `bash scripts/guardar-env.sh`, commit y push.
- Una vez a la semana: `scripts/backup-db.sh`, luego `scripts/guardar-backup.sh`, commit y push. El volcado sin cifrar (`backups/`) nunca se sube.
