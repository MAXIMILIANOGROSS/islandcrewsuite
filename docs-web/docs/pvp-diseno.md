# PvP Island Crew — diseño (NO implementado)

Decisión del fundador: **solo mayores de 18 años, con consentimiento explícito de ambos.** Borrador técnico; revisión legal pendiente (ver `docs/lista-abogado.md`, punto 39).

## Hechos comprobados en el repo
- El registro con email rechaza menores en el servidor (`enforce_signup_age`, TODO_CORRER_10) y no guarda la fecha de nacimiento.
- Ese trigger solo actúa con `provider = email`: las cuentas creadas por otro proveedor NO tienen comprobación de edad.
- Las posiciones del mundo multijugador son efímeras (Realtime presence), no se guardan: el servidor hoy no puede validar distancia ni línea de visión.

## Reglas
1. Elegibilidad: cuenta con `adult_attested = true` (declaración de mayoría de edad versionada y con fecha). Sin ella no se ve la opción de PvP.
2. Consentimiento de ambos: cada jugador activa "PvP activo" (revocable al instante). Golpear exige que atacante y objetivo lo tengan activo. Zona de combate no sustituye el consentimiento.
3. Zonas seguras por defecto: puerto, tiendas, aparición, Oficina. Fuera de ellas, solo con PvP activo de ambos.
4. Servidor autoritativo: el cliente envía solo la intención de golpe; el servidor aplica daño, cooldown, estado y reaparición.
5. Anti-abuso: invulnerabilidad breve al reaparecer, límite de golpes por segundo, sin daño a AFK/ausentes, bloqueo y denuncia con el sistema existente (`report_content`).
6. Sin pérdida de inventario ni progreso al caer; reaparición en el punto seguro más cercano.
7. Sin dinero ni premios reales por combate.

## Limitación técnica a resolver antes de construirlo
Con solo Realtime presence el servidor no conoce posiciones. Opciones: (A) servidor de juego pequeño que reciba posiciones y valide golpes (más robusto, infraestructura nueva); (B) que cada cliente publique su posición a una tabla/canal con TTL corto y la RPC valide distancia con tolerancia (más simple, menos robusto, implica tratar posiciones como dato, a revisar por el abogado). Recomendación: A si hay presupuesto; mientras tanto, solo combate local contra NPC.

## Orden de construcción propuesto
1. Revisión legal de los puntos del abogado. 2. SQL de consentimiento y declaración de mayoría de edad (`supabase/PROPUESTA_34_PVP_CONSENTIMIENTO.sql`, NO ejecutado). 3. Interruptor de PvP y barra de vida en el cliente. 4. Validación de golpes en servidor. 5. Pruebas con dos clientes reales (daño solo aplicado por servidor; cliente modificado no puede forzar daño ni alcance).
