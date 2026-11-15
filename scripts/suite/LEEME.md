# Island Crew Marketing Suite

Programa para crear la carta de tu restaurante con un vídeo por plato, código QR y flyers, todo en tu propio ordenador.

Esta versión incluye dos fábricas: **Carta Viva** y **Publicaciones y calendario**. La fábrica de música llegará en una próxima actualización. Cada fábrica se activa según tu licencia.

## Antes de empezar

- Un ordenador con **Windows 10 u 11** (64 bits) o un **Mac con macOS 11 o superior**.
- Tu **licencia**: un texto largo que te ha dado Island Crew.
- Conexión a internet para las claves de inteligencia artificial y para publicar la carta.
- Unos 600 MB libres en el disco.

## Instalar en Windows

1. Conecta el pendrive y ábrelo.
2. Entra en la carpeta **Windows**.
3. Haz doble clic en **Instalar-Windows.bat**.
4. Si Windows muestra un aviso azul («Windows protegió su PC»), pulsa **Más información** y después **Ejecutar de todas formas**. Sale porque el programa aún no lleva firma digital de pago.
5. Espera a que termine. Se abrirá el asistente.

Tendrás un icono **Island Crew Suite** en el escritorio y en el menú Inicio.

## Instalar en Mac

1. Conecta el pendrive y ábrelo.
2. Entra en la carpeta **Mac**.
3. Haz doble clic en **Instalar-Mac.command**. Si el Mac no lo abre, abre la app Terminal, escribe `bash ` (con un espacio), arrastra dentro el archivo y pulsa Intro.
4. Espera a que termine. Se abrirá el asistente.

Tendrás **Island Crew Suite** en la carpeta Aplicaciones de tu usuario y un acceso en el escritorio.

## El asistente (8 preguntas, solo la primera vez)

1. Qué fábricas quieres instalar.
2. Dónde guardar tus datos (por defecto, tu carpeta de usuario; puedes elegir un disco externo).
3. Tu licencia: pégala entera.
4. Nombre de tu negocio, ciudad e idioma.
5. Claves gratuitas de inteligencia artificial, con instrucciones en pantalla.
6. Cómo vas a publicar tu carta.
7. Comprobación de tu equipo.
8. Condiciones de uso.

Puedes repetirlo cuando quieras: en Windows, menú Inicio, Island Crew Suite, **Repetir asistente**.

## Usar Carta Viva

Desde el inicio de Island Crew Suite, abre **Carta Viva**. Crea tu restaurante, añade platos con su foto y genera el vídeo de cada uno. La carta se crea en tu ordenador. Cuando esté lista, el programa genera la carpeta `web` y el código QR. Esa carpeta es tu carta: súbela a donde elijas (por ejemplo, Cloudflare Pages, que tiene plan gratuito) y pega la dirección final en el campo del QR para imprimirlo.

Tus datos están en la carpeta que elegiste en el asistente y **no se envían a Island Crew**.

## Usar Publicaciones y calendario

Abre Island Crew Suite y pulsa **Abrir** en Publicaciones. Elige tu restaurante, la fecha de inicio y cuántas publicaciones por semana quieres, y pulsa **Crear calendario**. El programa usa los platos y fotos de Carta Viva y escribe un texto para cada día con tu clave gratuita de IA; no inventa precios ni ofertas. Revisa y cambia lo que quieras. Cada día, pulsa **Preparar paquete del día**: se abre una carpeta con las imágenes para el feed y las historias, el vídeo si el plato lo tiene y el texto, todo listo para subirlo a Instagram o Facebook. De momento no se publica solo: la subida la haces tú.

## Problemas frecuentes

- **No abre el programa:** ciérralo, vuelve a abrirlo desde el icono. Si sigue igual, escribe a hola@islandcrew.es y adjunta el archivo `carta-viva.log` de la carpeta `IslandCrewSuite` (en Windows, dentro de `AppData\Roaming`; en Mac, dentro de `Library/Application Support`).
- **El asistente dice que la licencia no es válida:** copia el texto completo, sin espacios al principio ni al final.
- **No hay traducciones ni textos automáticos:** falta la clave de Gemini del paso 5. Ponla repitiendo el asistente.
- **Se abre en el navegador y no en ventana propia:** el programa usa Edge o Chrome para mostrar la ventana. En un Mac sin Chrome, Edge ni Brave se abre en tu navegador normal; funciona igual.

## Desinstalar

- **Windows:** menú Inicio, Island Crew Suite, **Desinstalar**.
- **Mac:** carpeta **Mac** del pendrive, **Desinstalar-Mac.command**.

Desinstalar **no borra tus cartas ni tus datos**.

## Licencia y autoría

El software, sus plantillas y las piezas que genera son obra de Maximiliano Olmos Sánchez para Island Crew Marketing. Tu licencia te permite usarlo en tu negocio; no puedes copiarlo ni revenderlo. Los componentes de terceros (Python, Pillow, segno y ffmpeg) tienen sus licencias, detalladas en la carpeta **Licencias**.

Contacto y soporte: **hola@islandcrew.es**
