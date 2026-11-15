# Island Crew — Lista consolidada para el abogado

> Borrador técnico del equipo: **no es asesoramiento jurídico**. Cada punto es una pregunta o decisión para revisión profesional. Recopilado de `docs/` y de las decisiones de producto hasta 7-oct-2026. Estado de cada punto: ⏳ pendiente salvo que se indique.

## 0. Aviso de arranque
El sitio está publicado en islandcrew.es con registro abierto. Si ya hay personas reales registradas, conviene confirmar quién y mantener apagado lo sensible (transacciones de Market, puntos canjeables, matching a empleadores, registros de empleo con datos reales) hasta esta revisión.

## 1. Datos personales y RGPD
1. Bases jurídicas, minimización, finalidad y plazos de conservación por categoría (falta `data-retention-policy.md`).
2. Encargados y transferencias internacionales: Supabase, Vercel, Resend (DPA y región por comprobar).
3. Consentimientos separados y versionados: términos, privacidad, publicar perfil, visibilidad ante empleadores, comunicaciones, matching, personalización, cookies/analítica, puntos. Nada de "acepto todo".
4. Derechos RGPD: proceso operativo de solicitudes (plazos, responsable). Ya existen `privacy_requests`, `deletion_log`, `/eliminar-cuenta`; falta el procedimiento documentado.
5. Incidentes de seguridad/privacidad: protocolo y plazos de notificación (existe tabla `security_incidents`, falta el proceso).
6. Cookies y terceros: tabla evento/dato/finalidad/retención/proveedor/base e inventario de proveedores.
7. Datos laborales: CV, experiencia, salario, disponibilidad, historial, referencias, documentos. Qué ve cada tipo de empleador (público, registrado, autorizado por candidatura, privado).
8. Declaraciones de edad y documentación; uso por menores y mayoría de edad. Menores: qué se permite y con qué controles.
9. Posición y alias en tiempo real del mundo multijugador: efímeros, no se guardan; información al usuario y base legal. Alias nunca nombre real ni id de cuenta.
10. Reportes de contenido y de jugadores: tratamiento de las denuncias (`content_reports`), evidencias adjuntas, conservación, derecho de defensa del denunciado.

## 2. Empleo, matching e IA
11. Plataforma de conexión frente a agencia/intermediario de empleo: qué se puede cobrar y comunicar.
12. Matching/perfilado: art. 22 RGPD y Reglamento de IA (posible alto riesgo en selección de personal; fechas de aplicación por verificar). Sin rasgos protegidos; explicación e impugnación.
13. Entrevistas reales frente a simuladas: cómo se etiquetan; los resultados dentro del juego nunca equivalen a una contratación real.
14. Empleadores verificados: proceso y responsabilidad (hoy no hay panel de empleadores ni verificación).
15. Compartir CV: visibilidad y consentimiento.
16. Mezcla de ofertas reales con misiones de ficción (decisión del fundador: todo real y virtual, cada elemento etiquetado REAL o JUEGO; progreso del juego separado de la reputación real).

## 3. Negocios, personas y contenido reales dentro del mundo
17. **Nombres de locales reales como ambiente** (carteles de OpenStreetMap, incluido "Splash"): ¿es suficiente mostrarlos como ambiente, con la etiqueta "ambiente (no participa en Island Crew)"? Nunca como participantes ni con ofertas sin autorización.
18. Negocios de juego **anclados en el lugar de locales reales** (sin usar su nombre): ¿puede inducir a confusión? Los 230 negocios son ficticios, etiquetados "negocio de juego".
19. Qué pasa si un local real pide retirar su cartel: procedimiento de retirada.
20. Participación real de un negocio: solo si reclama y verifica su perfil, acepta su presencia y puede retirarse (hoja de consentimiento del kit piloto: capacidad de quien firma, marca e imagen, logos/fotos, responsable del tratamiento, plazo de retirada, datos ya compartidos).
21. Fachadas, rótulos, marcas y caras reales (derechos de imagen y marca). Rótulo "CORRALEJO" y el uso de la identidad local.
22. Google Maps/Places/Street View: **no se copian ni almacenan datos ni imágenes**; las capturas de Street View se usan solo como referencia visual interna. Confirmar que ese uso interno es aceptable y que la lista de restaurantes sale solo de OpenStreetMap.
23. OpenStreetMap (ODbL): atribución visible «© Colaboradores de OpenStreetMap», obligaciones de compartir igual de la base derivada.
24. Panorámicas 360° propias: permisos, difuminado de caras y matrículas, consentimiento de negocios visibles.
25. Panorámicas de terceros: licencia y atribución concretas.
26. Contenido de usuarios: licencia en términos y mecanismo de retirada.
27. Assets de terceros (MetaHuman, Fab, modelos GLB/texturas): licencias para producto comercial.
28. Barcos, aerogeneradores, isla de Lobos y otros elementos del paisaje: son representaciones provisionales sin datos reales; confirmar que no requieren permisos.

## 4. Gamificación, premios y economía
29. Programa de puntos, caducidad, canjes y partners; beneficios hoy apagados.
30. XP, niveles, reputación y rankings; reputación profesional con efecto real.
31. Caza del tesoro, eventos con premios, sorteos, promociones: bases legales.
32. Objetos aleatorios y rarezas: confirmar que no son "loot box" mientras no haya pago.
33. Intercambio entre jugadores y dinero de juego: que no tenga valor económico ni sea convertible.
34. Reseñas y derecho de réplica.

## 5. Comunicación y moderación
35. Chat de texto y voz: **diferidos** hasta tener moderación y revisión legal. Opciones de bloqueo, silencio e informe.
36. Moderación mínima, tiempos de respuesta, responsabilidad de la plataforma sobre contenido de usuarios.
37. Retirar el flag `?multi=1` y abrir el multijugador a todos: solo tras bloqueo/denuncia cableados, filtro de alias y moderación en admin.

## 6. Combate y PvP (nuevo)
38. **Combate local contra NPC ficticios** (ya implementado): sin sangre, sin daño persistente; ¿alguna restricción de clasificación por edad o contenido?
39. **PvP entre jugadores** (NO implementado). **Decisión del fundador: solo para mayores de 18.** Requisitos de diseño en `docs/pvp-diseno.md`: consentimiento explícito y revocable de ambos, zonas seguras por defecto, servidor autoritativo, anti-abuso, invulnerabilidad tras reaparecer, AFK, bloqueo/informe. Preguntas para el abogado: (a) el registro con email ya exige 18+ en servidor (la fecha no se guarda), pero los registros por proveedor externo (OAuth) **no pasan ese control**: ¿basta una declaración de mayoría de edad guardada con versión y fecha, o hace falta verificación? (b) responsabilidad por acoso o abuso; (c) cómo se acredita y retira el consentimiento; (d) registro de eventos de combate y su conservación; (e) si el servidor no puede validar posiciones (hoy son efímeras), ¿qué nivel de garantía exige un PvP sin dinero ni premios reales?
40. Mecánicas violentas y clasificación de contenido (PEGI/códigos de conducta de tiendas de apps si se publica en app).

## 7. Marketplace, vivienda y seguros
41. Market: compraventa, alquiler, pagos, depósitos, reembolsos, disputas, reseñas, fraude, responsabilidad de plataforma, impuestos, consumidores, bienes prohibidos, moderación.
42. Vivienda: publicación, contacto, intermediación, propietarios/agencias, anuncios externos, comisiones, leads, visitas.
43. Seguros: Island Crew no es aseguradora; solo vía corredor/MGA autorizado; textos, exclusiones, siniestros, precio y comisión.
44. Pagos y depósitos; comisiones.

45. **Reclamar un local real** (nuevo, `/empresa/mi-local`, SQL 36): una persona dice ser dueña, encargada o de RR. HH. de un local real; un admin verifica manualmente (teléfono/correo del negocio) y se crea una cuenta de negocio verificada. Preguntas: a) responsabilidad si la verificación falla y alguien se hace pasar por el local; b) qué datos de la persona se muestran en el juego y en las apps; c) texto de consentimiento del local (marca, nombre, imagen) y de retirada; d) uso del nombre del local como "RR. HH. abierto" una vez verificado.

## 8. Documentos legales a redactar/revisar
Términos, privacidad, cookies, avisos de consentimiento, reglas de Market y de comunidad, términos de empleador, propietario/agencia, partner y recompensas, consentimiento de negocios (borrador en el kit piloto).

## 9. Lanzamiento
Estados: `TECHNICALLY_READY → PRIVACY_REVIEW_PENDING → LEGAL_REVIEW_PENDING → SECURITY_REVIEW_PENDING → APPROVED_FOR_STAGING → APPROVED_FOR_BETA → APPROVED_FOR_PUBLIC_LAUNCH`. No se declara listo hasta marcar: producto, seguridad, privacidad, RGPD, consentimientos, empleo, vivienda, marketplace, gamificación, pagos, seguro, analítica, documentos, retención/eliminación, DSAR e incidentes.

## 10. Contacto
Único correo público: `hola@islandcrew.es`.

> 2026-10-07: el fundador indica que el abogado aprobó verbalmente todos los puntos. Pendiente: confirmación por escrito (email) archivada junto a esta lista.
