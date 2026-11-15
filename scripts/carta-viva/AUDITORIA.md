# Carta Viva — auditoría (Fase 0)

## Qué existe hoy (se conserva)
- **Programa de Mac** con ventana propia (`app-nativa/main.swift`, WKWebView) que arranca un servidor local en Python (`carta-viva-app.py`) y una interfaz de un solo archivo (`carta-viva-app.html`).
- **Datos**: una carpeta por restaurante en `T5 EVO/IslandCrewAI/cartas/<id>/` con `carta.json` (restaurante + lista de platos), `fotos/`, `videos/`, `marca/` (logo y fondo), `web/` (carta publicable), `promo/` y QR.
- **Platos**: nombre, categoría, precio, descripción, alérgenos, foto principal, varias fotos (giro 360°), movimiento de vídeo y ajustes del giro.
- **Vídeos**: ffmpeg gratis, 3 estilos (giro 360° con varias fotos, giro plano, cámara de cine), título y precio dentro del vídeo.
- **Carta pública** estática (`web/index.html`): carta de papel con vídeo fijo al lado, rejilla de vídeos y visor, 5 temas, 5 tipos de letra, colores propios.
- **QR** con logo (PNG/SVG), flyer A4 (PNG/PDF), story y banner. **IA** gratis: Gemini con respaldo Groq.
- **Espacio en disco**: caja para borrar copias y vídeos sin tocar fotos ni marca.

## Decisiones (por qué no se hace todo lo del prompt maestro de golpe)
1. **Coste cero y local**: el producto funciona sin servidor propio. Cuentas, suscripciones, cobros, estadísticas de escaneos y traducción en vivo **necesitan un servidor y base de datos en internet**. Eso cambia el modelo (y puede costar dinero), así que **no se activa sin tu autorización**. Queda como Fase 8.
2. **Nada decorativo**: solo se muestran en el menú secciones que funcionan de verdad.
3. **Compatibilidad**: los campos nuevos de cada plato son opcionales; las cartas y QR existentes siguen igual. Copia de seguridad hecha antes de tocar nada.
4. **La carta pública mantiene la carta de papel con vídeo** (es lo que se validó con un restaurante); la rejilla de vídeos sigue como segunda vista.

## Hecho en esta primera versión
- Menú lateral por secciones: Panel, Mi restaurante, Platos y vídeos, Diseño, QR y promoción, Espacio.
- **Panel** con estado, cifras reales, avisos de información incompleta, platos repetidos y accesos rápidos.
- Ficha de plato ampliada: ingredientes, etiquetas (especialidad, más vendido, recomendación del chef, nuevo, favorito, vegetariano, vegano, sin gluten verificado), disponibilidad, duplicar, reordenar.
- Carta pública: etiquetas, ingredientes y platos no disponibles ocultos.
- Exportar e importar platos (JSON) sin duplicados.

## Pendiente por fases
- Fase 3b: recorte de vídeos propios y música (sin derechos).
- Fase 6: idiomas (traducción con IA gratis, revisión manual, selector en la carta).
- Fase 7: estadísticas (requiere servidor) y QR con URL estable propia.
- Fase 8: cuentas, planes y cobros (requiere tu autorización y servicios externos).
