# Island Avatar System

Estado: **diferido a P2, condicionado a validación del MVP 2D.**

## Decisión
Un avatar solo se construye si mejora una métrica real (más contactos, más aplicaciones, más Crews). Si el usuario ya se identifica con foto/inicial y nombre, el avatar es decoración.

## Diseño propuesto cuando se haga
- **2D modular** (capas: cuerpo, piel, pelo, ropa, accesorios, calzado, mochila, uniforme/profesión) para no producir cientos de assets a mano; animación con Rive solo para el Goat y reacciones puntuales.
- **Inclusivo:** variedad real de cuerpos, tonos de piel, pelo, edades, discapacidades visibles opcionales; sin caricaturas.
- **Identidad local sin estereotipos:** capa cultural opcional por destino (p. ej. majorero/majorera, chicharrero/chicharrera), diseñada **con personas de cada isla**, con ropa y objetos contemporáneos; sin acentos ridiculizados ni clichés.
- **3D:** no hasta que exista una razón de producto medida; si 2D resuelve, se usa 2D.

## Privacidad
El avatar es una **representación**, no un dato de ubicación. Visibilidad: público / usuarios registrados / solo empleadores / privado. Presencia online opcional y desactivada por defecto. Nunca teléfono, email, dirección, DNI ni ubicación exacta. Menores: Island Crew es solo para mayores de 18; no se diseña para menores.

## Derechos
Los elementos gráficos deben ser propios o con licencia; sin imitar personajes, marcas ni estilos protegidos de terceros. Voz y *likeness* de personas reales: solo con consentimiento escrito.

## Cabra
El Goat sigue siendo guía, no avatar del usuario. Primero unificar las tres implementaciones actuales en un componente con estados.
