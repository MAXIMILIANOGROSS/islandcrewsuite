# Island Crew Network · estado real (actualizado 2026-10-10)

Estados: TERMINADA Y VERIFICADA (probada por el fundador en producción) · IMPLEMENTADA, PENDIENTE DE PRUEBAS (código + tests de código, sin prueba con cuentas reales) · BLOQUEADA · PENDIENTE · DESCARTADA.

## Bloque A · Núcleo
- Perfil (alias, titular, sobre mí, sector, zona, visibilidad): TERMINADA Y VERIFICADA (SQL 53).
- Publicar texto, tipos (proyecto/logro/pregunta/aprendizaje/evento), visibilidad: TERMINADA Y VERIFICADA.
- Reacciones, comentarios, guardar, denunciar, eliminar: TERMINADA Y VERIFICADA.
- Conexiones, bloqueo, búsqueda de personas: TERMINADA Y VERIFICADA (SQL 54).
- Experiencia/formación/habilidades/idiomas/certificaciones/proyectos declarados + «Verificado» solo por el servicio: IMPLEMENTADA, PENDIENTE DE PRUEBAS (SQL 58).
- Perfil público con URL estable /network/u/[handle]: IMPLEMENTADA, PENDIENTE DE PRUEBAS.
- Editar publicación, compartir con referencia al original, ocultar: IMPLEMENTADA, PENDIENTE DE PRUEBAS (SQL 58).
- Feed «Recomendados»: PENDIENTE a propósito (sin volumen real; el feed es cronológico y transparente).
- Editar/eliminar comentarios, respuestas anidadas: PENDIENTE.
- Imágenes, vídeos y documentos: BLOQUEADA hasta definir almacenamiento (Supabase Storage), límites, escaneo y política de moderación.
- Vista previa de enlaces: PENDIENTE (requiere servidor que consulte URLs de forma segura).

## Bloque B · Comunicación
- Mensajes entre contactos, avisos de conexión/comentario/reacción/mensaje: TERMINADA Y VERIFICADA. Sin cifrado de extremo a extremo (no se afirma).
- Preferencias de notificación, silenciar conversaciones, adjuntos: PENDIENTE.
- Grupos y eventos: PENDIENTE.

## Bloque C · Empresas y empleo
- Negocios verificados, vacantes, candidaturas, gestión por el negocio, denuncias: IMPLEMENTADA, PENDIENTE DE PRUEBAS (SQL 56, /empleos, /empresa/[id]/candidaturas).
- Páginas de empresa públicas con publicaciones y seguidores: PENDIENTE.

## Bloque D · Island Crew World
- Misión 1 con puntos del servidor y ranking v2: IMPLEMENTADA, PENDIENTE DE PRUEBAS (SQL 52 y 57).
- Resto de misiones (m02–m33): PENDIENTE (en_desarrollo en el catálogo).

## Bloque E · Comercial
- Crew Plus: solo experimento de validación (SQL 55). Cobros BLOQUEADA hasta tener empresa real y condiciones publicadas.

## Bloque F · Escala/seguridad
- RLS cerrada + funciones con auth.uid(), límites por hora/día: hecho en los SQL 53–58.
- Panel de métricas, monitorización, política de privacidad y condiciones, revisión legal: PENDIENTE.
