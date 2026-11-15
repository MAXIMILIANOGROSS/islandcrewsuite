# Island Crew — Next.js

Versión profesional de la landing de Island Crew, migrada de un HTML estático a Next.js 14 (App Router) + TypeScript + Tailwind CSS.

## Empezar

```bash
npm install
cp .env.local.example .env.local   # ya viene con tus claves reales de Supabase
npm run dev
```

Abrí http://localhost:3000 (español) y http://localhost:3000/en (inglés).

## Qué incluye

- **Diseño**: paleta de marca (ink/yellow/paper/cyan) y estilo neo-brutalista vía Tailwind, definido en `tailwind.config.ts` y `src/app/globals.css`.
- **Contenido bilingüe**: todo el texto vive en `src/lib/content.ts` (claves `es`/`en`), sin librería de i18n — simple y fácil de editar.
- **Datos en vivo**: `src/lib/supabase.ts` lee la tabla pública `landing_stats` de Supabase (perfiles activos, empresas activas, tiempo medio de match) y cae de vuelta a los números de ejemplo si algo falla.
- **Secciones**: Nav, Hero, Cómo funciona, Empresas, Sectores, Mapa de islas, Merch, Comparativa, Oportunidad de inversión (con el video de fondo), Built on, Footer con el wordmark gigante.
- **Rutas**: `/` (español, por defecto) y `/en` (inglés) — listo para agregar `/islas/[isla]` y `/sectores/[sector]` (próximo paso, páginas SEO).

## Notas

- Las fuentes (Archivo Black, Space Grotesk) se cargan vía `next/font/google` — necesitan acceso a internet en build/dev (funciona normal en tu máquina o en Vercel).
- El video de la sección de inversión está en `public/images/hero-video.mp4` (~1.1MB, comprimido).
- Cuando tengas el pago de hosting aprobado, este proyecto está listo para desplegar en Vercel y conectar el dominio `islandcrew.es`.
