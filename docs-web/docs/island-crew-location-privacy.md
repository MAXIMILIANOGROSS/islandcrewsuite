# Privacidad de ubicación

Estado: diseño; **revisión legal y de privacidad obligatoria antes de usuarios reales.**

## Principios
1. **Mínimo necesario.** No se guarda la ubicación exacta si no hace falta.
2. **Separar** `navigation_position` (solo en el dispositivo, mientras se explora; no se envía) de `stored_user_location` (lo que se guarda, solo zona o aproximación elegida por el usuario).
3. **Control del usuario:** permiso explícito, revocable; la ubicación exacta nunca es visible para otros usuarios.
4. **Visibilidad granular** (PUBLIC / REGISTERED_USERS / EMPLOYERS_ONLY / PRIVATE) para perfil, avatar, presencia, historial laboral, vivienda, Market y actividad social.

## Estado actual (comprobado)
- `profiles.lat/lng` existen y están protegidos (no se exponen por la API pública; `profiles_public` no los incluye). La «isla verificada» guarda solo el nombre de la isla y la fecha.
- `properties.lat/lng` son numéricos **sin límite de precisión**: antes de mostrar viviendas en un mapa hay que publicar una **posición aproximada** (zona o coordenada redondeada/desplazada) y reservar la exacta para el propietario y la visita acordada. **Pendiente de hacer.**

## Datos de exploración y analítica
Los eventos de mapa (`zone_entered`, `hotspot_viewed`) llevan **zona**, nunca coordenadas. Requieren revisar base legal y consentimiento de analítica.

## Seguridad social
Cualquier presencia de otros usuarios en el mapa queda **desactivada por defecto**, exige consentimiento y arquitectura de seguridad (bloquear, denunciar, moderación, antiacoso) antes de existir.

## Retención
Posición de navegación: no se almacena. Ubicación guardada: mientras la cuenta esté activa y hasta que el usuario la borre; el calendario formal va en `data-retention-policy.md` (pendiente).
