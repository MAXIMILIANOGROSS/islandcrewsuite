# Auditoría de fuentes externas — Chef AI / Smart Swipe

Fecha: 2026-10-11. Método: lectura de la página pública de cada repo. **Las fechas del último commit no aparecían en las páginas leídas**, así que el "mantenimiento" solo se estima por nº de commits/estrellas (NO VERIFICADO). Las licencias son las que muestra la página; donde solo hay insignia/README sin archivo LICENSE se indica. No es asesoría legal.

## 1. Tabla comparativa

| # | Proyecto | Stack | Licencia (código) | Datos/modelos | Señales | Veredicto |
|---|---|---|---|---|---|---|
| 1 | SmartPantry | Next 14 + FastAPI, YOLOv8, OpenAI | MIT | pesos YOLO propios; datos no verificados | 57 commits, 0 ★ | Referencia de diseño (revisar detecciones antes de guardar: ya lo hacemos) |
| 2 | PantryMatch | Flask + React 19, ResNet18 | MIT (fork) | peso no verificado | 12 commits | Descartar código |
| 3 | Smart Fridge Mgmt | Flask, YOLO, ESP32 | MIT solo en README, sin LICENSE | no verificado | 7 commits | Descartar |
| 4 | Fridge Vision RAG | Flask+Next, FAISS, Llama 3.2 | **Ninguna** | licencias Llama/Mistral | 2 commits | **Descartar** |
| 5 | ZeroWaste-Kitchen | Flask | MIT solo por insignia | — | 37 commits | Idea de semáforo de caducidad, reimplementada propia |
| 6 | Mealie | Python/Vue app completa | **AGPL-3.0** | — | 13,4k ★ | **No embeber**; referencia funcional |
| 7 | Tandoor | Django/Vue app completa | AGPL-3.0 + "common clause", dudas legales abiertas | — | 8,6k ★ | **Descartar** |
| 8 | react-form-wizard | React/TS | MIT | — | 78 commits | Redundante con SmartSwipeFlow |
| 9 | react-swipeable-cards | React/TS | **Tipo no mostrado** | — | 21 commits | Descartar hasta confirmar; ya existe useSwipe |
| 10 | react-wizard-onboarding | React/TS | MIT | — | 36 commits | Redundante |
| 11 | NutriLens | Streamlit, TF, Groq | MIT por insignia | dataset de origen no declarado | 16 commits | Descartar modelo; idea barcode→Open Food Facts anotada |
| 12 | Food Label AI Pipeline | PyTorch, YOLOv8, EasyOCR | MIT | pesos no incluidos | 1 commit, WIP | Descartar (WIP; YOLO de Ultralytics es AGPL) |
| 13/29 | Topic freshness-detection | listado | — | — | — | No es un recurso |
| 14 | AI4Food-NutritionDB | Python | **Sin licencia** | 7 datasets de terceros | — | **Descartar** |
| 15 | Food-101 | dataset | **No verificado** (la página falló) | imágenes de terceros | — | Descartar hasta verificar |
| 16 | Fruit_Freshness_Detection | TF+SVM | MIT | dataset sin origen/licencia | 57 commits | Descartar modelo |
| 17 | PD-Lab | PyTorch ViT | **Ninguna** | README admite etiquetas erróneas y 99% inflado | 14 commits | **Descartar** |
| 18 | Nutrition5k | dataset | código sin licencia | **CC BY 4.0, comercial permitido con atribución**; 181 GB; repo archivado | — | Licencia OK, inviable en Vercel |
| 19 | USDA FoodData Central | API/datos | — | **CC0 / dominio público**; clave data.gov; 1.000 req/h | oficial | **Adoptar** (importación offline) |
| 20 | Segmentation-Aware Nutrition | PyTorch | no leído (falló) | — | — | NO VERIFICADO → descartar |
| 21 | 3D-FoodCalorie | Mask R-CNN, depth | **Ninguna** | — | 291 commits | **Descartar** |
| 22 | Food Recog. & Nutrition Analyzer | YOLOv8m + MiDaS | MIT | UECFOOD256 (términos no verificados) | 16 commits | Descartar |
| 23 | RecipeNLG | dataset | sin licencia en repo | solo investigación no comercial (según README de #25) | — | **Descartar** |
| 24 | Recipe-Generation-Project | PyTorch | sin licencia | — | — | **Descartar** |
| 25 | recipe-generation (LLaMA) | LLaMA-Adapter | GPL-3.0 | LLaMA 7B + RecipeNLG no comercial; 22–30 GB GPU | 24 commits | **Descartar** |
| 26 | Food Recog. Calorie CNN | TF/Streamlit | MIT | Food-11 + CSV de origen no declarado | 8 commits | Descartar |
| 27 | AI4FoodDB | datos clínicos | no visible | **"no usado en aplicaciones comerciales"** + datos de salud | — | **Descartar** |
| 28 | Topic food-recognition | listado | — | — | — | No es un recurso |

## 2. Utilidad / dificultad

- Útil y fácil: USDA FDC → motor nutricional determinista (hecho); ideas de SmartPantry (revisar antes de guardar) y ZeroWaste (semáforo).
- Útil pero difícil: Nutrition5k (licencia OK, 181 GB, fuera de Vercel); barcode→Open Food Facts (licencia ODbL a verificar).
- Redundante: react-form-wizard, react-wizard-onboarding, react-swipeable-cards.
- Bloqueado por licencia/datos: el resto.

## 3. Matriz de compatibilidad (SaaS comercial cerrado)

- Compatible: MIT, CC0, CC BY 4.0 (con atribución).
- Incompatible con embeber: AGPL (Mealie, Tandoor, YOLO de Ultralytics) — obligaría a publicar el código.
- Incompatible: GPL-3.0 (#25), datos no comerciales (RecipeNLG, AI4FoodDB), sin licencia (#4, #14, #17, #21, #23, #24).
- Sin verificar: #9, #15, #20, datos de #22.

## 4. Arquitectura objetivo

Foto → `/api/chef-nevera` (visión LLM, foto no guardada) → tarjetas swipeables confirmadas → `pantry_items` → asistente (SmartSwipeFlow + aceptación) → `/api/chef-generar` → `comprobarReceta` → **`calcularNutricion` (nuevo, determinista)** → `recipe_save` → libro/PDF → cocinar → compra. La Cabra orquesta con `turnoChef` y confirmación.

## 5. Reutilizar / adaptar / descartar

- Reutilizar: USDA FoodData Central (CC0).
- Adaptar (ideas, código propio): revisión previa de detecciones, semáforo de caducidad.
- Descartar: el resto.

## 6. Fases

1. Hecho: Smart Swipe + flujo Nevera→Asistente→Receta→Libro→Cocinar→Compra.
2. Ahora: `src/lib/chef/nutricion.ts` + `tests/chef-nutricion.test.mjs`.
3. Siguiente: importación USDA a tabla `food_nutrition` (con tu clave data.gov, nunca en el repo) y panel de nutrición en la receta.
4. Después: caducidad manual con semáforo (nunca "es seguro"), perfil culinario, mercado de chefs (decisión Stripe).

## 7. Limitaciones, costes y riesgos

- Sin tabla importada el motor devuelve 0% de cobertura y no inventa.
- Cucharadas/tazas/pizcas no se convierten a gramos.
- Frescura por IA: ningún repo es fiable; no se ofrecerá certificación de seguridad alimentaria.
- Visión depende de un modelo con imágenes configurado en Vercel.
- USDA gratis; visión de pago por uso.
- Mantenimiento de todos los repos y licencias de #9, #15, #20 sin verificar.
