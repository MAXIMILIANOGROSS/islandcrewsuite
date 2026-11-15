# Island Crew World — dirección de arte (referencia visual)

Las imágenes de referencia (seis capturas del paseo de Corralejo en primera persona, con interfaz) fijan el objetivo visual. Este documento las traduce en requisitos. **Los nombres de negocios de esas imágenes (La Ola, Tiki, El Ancla, O'Bar, La Sirena) y las personas que aparecen son ficticios o generados: no se usan como negocios reales ni sin comprobar que no coinciden con locales existentes.**

## Qué define el aspecto
- Luz atlántica de tarde, cielo azul, sombras suaves.
- Paseo marítimo de adoquín, fachadas blancas de poca altura con detalles azules, toldos, terrazas, pizarras de menú, macetas, farolas, palmeras moderadas.
- Mar y montaña volcánica al fondo. Gente paseando (adultos diversos, ropa cotidiana).
- Negocios con rótulo propio y un encargado en la puerta; interior visible.

## Interfaz (ya implementada en el prototipo)
- Arriba izquierda: lugar ("Corralejo · Fuerteventura, Islas Canarias").
- Arriba derecha: "★ N OPORTUNIDADES" (cuenta real de vacantes abiertas).
- Mira central, "[ E ] HABLAR/ENTRAR" y nombre + distancia del negocio cercano.
- Pendiente: brújula (solo cuando la orientación real de la escena esté modelada), barras de estado, manos del jugador, mensaje de guía del Goat ("Explora Corralejo…").
- Reglas: sin XP por pasear; el progreso lo concede el backend por acciones reales.

## Cómo llegar a ese aspecto (opciones reales)
1. **Panorámicas 360° propias.** Fotografiar el paseo con una cámara 360° (con permiso donde proceda), mostrarlas en un visor con puntos de interacción sobre cada negocio. Es el camino más rápido a "se ve real". No permite caminar libre: se salta de nodo en nodo. Revisar con abogado: caras y matrículas desenfocadas, derechos sobre fachadas y rótulos, y el uso de marcas de negocios no participantes.
2. **Escena 3D modelada en Unreal** con artistas 3D y assets con licencia. Máxima calidad y libertad, meses de trabajo y presupuesto de arte.
3. **Imágenes generadas por IA como fondos.** Rápido de ver, pero sin caminar libre, con riesgo de parecerse a locales reales y con licencias de la herramienta que revisar. No recomendado para negocios reales.

## Personajes
- Encargados de negocio con permiso del negocio y de la persona. Sin voces ni rostros reales sin autorización.
- Diálogo con guion y datos reales del negocio hasta tener revisión legal para IA.

## Accesibilidad
Siempre existe la alternativa no 3D (lista y mapa en `/mundo`), subtítulos, reducir movimiento y mando.

## Decisión recomendada
Empezar con un solo tramo del paseo en panorámicas propias y un solo negocio real con consentimiento. Medir si la gente lo usa antes de invertir en 3D completo.
