# Island Crew World — arquitectura, auditoría y MVP

Estado: **diseño. No se ha implementado nada de World.** Fecha: 2026-10-06. Lo que se afirma del repositorio está comprobado; lo demás está marcado como *desconocido* o *a verificar*.

## 1. Opinión del arquitecto (lo primero)
1. La idea tiene valor: convertir la búsqueda de trabajo y vivienda en **exploración de un lugar real** es diferencial y encaja con el North Star (empleo y vivienda conseguidos).
2. El mayor riesgo **no es técnico, es de contenido y derechos**: hoy Island Crew no tiene un directorio de negocios reales que hayan aceptado participar, ni licencias de panorámicas/Street View, ni propietarios que gestionen un avatar. Sin eso, World es un mapa vacío.
3. **No construiría 3D, avatares ni entrevistas con IA libre todavía.** Primero hay que validar con un mapa 2D si la gente explora, contacta negocios y aplica (sección 7). Si el mapa 2D no mueve esas métricas, el 3D tampoco lo hará.
4. **Entrevista virtual con IA = la pieza de mayor riesgo legal** (selección de personal con IA, art. 22 RGPD, Reglamento europeo de IA: la selección de personal figura como uso de alto riesgo y el reconocimiento de emociones en el trabajo está prohibido; **fechas y alcance exactos: revisión legal**). Se sustituye en el MVP por un **cuestionario estructurado de pre-selección con decisión humana**.
5. *Walk to Work* es una buena idea **como vista** (ruta de negocios que contratan), siempre con alternativa en lista/búsqueda. Nunca la única vía.

## 2. Qué existe hoy (auditoría relevante a World)
| Pieza | Estado real |
|---|---|
| Ofertas de empleo | tabla `offers` (+ `matches`, `swipes`, `interviews`); modelo de vacante **no revisado en detalle** |
| Negocios | `restaurant_profiles` (modelo antiguo) y `business_accounts/members` (nuevo, con verificación y roles) → **dos modelos de empresa a unificar** |
| Vivienda | `properties` con `lat/lng` numéricos (**precisión no limitada**, a revisar antes de mostrar en mapa), fotos, favoritos, intereses, visitas |
| Market | `market_items` (+ vista pública sin propietario), zona por municipio |
| Chat | mensajes de vivienda y de grupo; chat de matches en `messages`; **tres sistemas** de conversación |
| Mapa | **no hay librería de mapas** (ni MapLibre, Mapbox, Leaflet ni Google). `IslandMap.tsx` es una sección de marketing |
| 3D | `three` + R3F ya en el proyecto, solo para la cabra |
| Geolocalización | `profiles.lat/lng` existen y están protegidos (no se exponen) |
| Gamificación | motor XP/niveles/objetivos, `launch_gate`, flags, `next_best_action` (ya en producción) |
| Privacidad/derechos | `privacy_requests`, `terms_acceptances`, cookies; **sin** `consent_records` ni Privacy Center |

## 3. Qué se reutiliza y qué cambia
- **Reutilizar:** `user_id` único, `business_accounts` (como `BusinessAccount`), `offers` (como `Job`), `properties`, `market_items`, motor de XP/objetivos, `launch_gate`, flags, notificaciones, `employment_records`.
- **Cambiar antes de World:** unificar `restaurant_profiles` ↔ `business_accounts`; reducir precisión de `properties.lat/lng` a una zona/coordenada aproximada pública; decidir un sistema de conversación único (ver §9).
- **No tocar:** Housing, Crew, Market, identidad.

## 4. Arquitectura: tres niveles, progresivos
1. **Exploración (nivel 1).** Mapa 2D de Corralejo con zonas y puntos de interés. Panoramas 360 **solo** con licencia propia/autorizada (nivel 1b, después). Street View: no se reutiliza imagen; si algún día se usa, solo mediante el producto oficial y sus condiciones (**a verificar con abogado**).
2. **Capa Island Crew (nivel 2).** Hotspots que apuntan a entidades existentes: negocio, vacante, vivienda, artículo de Market, evento, servicio, Crew, partner.
3. **Espacios interactivos (nivel 3).** "Entrar en un negocio" = página de negocio con información estructurada, vacantes y cuestionario. Interiores 3D, NPC y eventos: no antes de validar ROI.

## 5. WorldEngine (abstracción independiente)
Responsabilidades: cargar destino, listar zonas, devolver hotspots, navegar, descubrir, estado espacial. **No conoce Jobs ni Housing**: son capas de contenido que registran hotspots.
```
Destination 1─n Zone 1─n WorldLocation 1─n Hotspot ──(type, ref_id)──▶ Business | Job | Housing | MarketListing | Event | Service | Crew | Partner
WorldLocation 0..1─n Panorama (opcional) ; Hotspot n─1 WorldContentSource (derechos)
```
Hotspot: `type`, `ref_id` (entidad real, **sin duplicar datos**), `state` (ACTIVE/INACTIVE/HIDDEN), `zone_id`, `position` (aproximada), `source_status` (verified / user_submitted / partner / external / estimated / unavailable).

## 6. Modelo de entidades (nuevo vs. existente)
Nuevas: `destinations`, `zones`, `world_locations`, `hotspots`, `world_content_sources`, `business_knowledge` (base estructurada del negocio), `business_prescreen_questions/answers`, `journeys`, `journey_branches`, `missions`. Existentes que se enlazan: `profiles`, `business_accounts`, `offers`, `properties`, `market_items`, `housing_groups`, `xp_events`, `badges_awarded`, `goals_catalog`. Avatar y pasaporte: **diferidos**.

## 7. MVP recomendado: «Corralejo 2D» (validar antes de invertir)
**Entregable:** mapa + lista de Corralejo con hotspots de **negocios reales que han aceptado**, sus vacantes, viviendas y artículos de Market; página de negocio; cuestionario estructurado; XP/objetivos ya existentes; Goat como guía. Sin avatares, 3D ni IA conversacional.
**Hipótesis a medir (sección 66 del prompt) con eventos reales:** ¿exploran? ¿abren negocios? ¿inician contacto? ¿aplican? ¿consiguen entrevista? ¿el negocio recibe valor? ¿Housing/Crew mejoran su conversión?
**Criterio para pasar a P2:** umbrales definidos *antes* de lanzar el piloto (propuesta: lo decide el fundador con datos de 4–6 semanas; no se inventan cifras aquí).
**Dependencia crítica:** conseguir de 5 a 10 negocios reales dispuestos y con consentimiento. Sin ellos, usar solo negocios **ficticios claramente etiquetados** para demos.

## 8. Qué NO construir todavía
Mundo 3D, interiores, creador de avatares, voz, entrevista con IA libre, Life Tree gráfico, Island Passport, eventos estacionales, transferencia entre destinos, social avatars, puntos canjeables, tienda de recompensas, panorámicas sin licencia.

## 9. Conversaciones
Hoy hay tres sistemas. Antes de añadir "usuario ↔ negocio" o "↔ avatar IA" hay que unificar en un modelo `conversations/participants/messages` con contexto (propiedad, oferta, artículo). Es trabajo de P1, previo al avatar.

## 10. Roadmap
- **P0 Fundación (2–3 sem. estimadas):** modelo `destinations/zones/hotspots`, flags World, unificación de negocio, aproximar `properties.lat/lng`, `consent_records`, `/settings/privacy`, E2E + axe.
- **P1 Corralejo 2D:** MapLibre + OSM (atribución ODbL; licencia y términos **a verificar**), hotspots, perfil de negocio reclamable, cuestionario, solicitud, enlace a Housing/Market.
- **P2 Interactivo:** Walk to Work (ruta de negocios), Journey/ramas, misiones dinámicas, avatar 2D simple si el P1 valida.
- **P3 Crew + Market integrados, P4 destino completo, P5 escala:** como el prompt, condicionados a datos.
*Duraciones: estimaciones sin verificar.*

## 11. Feature flags (ya existe `gamification_flags`; se amplía)
`world_enabled`, `street_exploration_enabled`, `business_ai_enabled`, `virtual_interviews_enabled`, `avatar_system_enabled`, `3d_world_enabled`, `walk_to_work_enabled`, `island_passport_enabled`, `dynamic_missions_enabled`, `island_points_enabled`. **Todos apagados por defecto**; cada uno ligado a su área del `launch_gate`.

## 12. Prioridad cuando hay conflicto
Seguridad → privacidad → legalidad → utilidad → UX → accesibilidad → rendimiento → escalabilidad → monetización → gamificación.
