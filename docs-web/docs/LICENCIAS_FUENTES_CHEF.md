# Fuentes externas para Chef AI — estado de licencias

Última revisión: 11/10/2026. Revisado leyendo las páginas públicas de GitHub; **no es asesoramiento legal**.

| Recurso | Qué es | Licencia declarada | Estado en Island Crew |
|---|---|---|---|
| Glorf/recipenlg | Scripts y notebooks del paper INLG 2020 (scraping, NER, evaluación). El dataset (~2,2 M recetas) se descarga aparte desde la web del proyecto; el modelo está en Hugging Face (mbien/recipenlg). | **No se declara licencia** para el código ni términos de uso comercial para el dataset en la página del repositorio. El dataset incluye recetas recopiladas de otras fuentes. | **No integrado.** Sin licencia, por defecto todos los derechos están reservados. No se copia código, no se redistribuye el dataset ni se entrena un modelo comercial con él. |
| Hazot/Recipe-Generation-Project | Pipeline de investigación para ajustar modelos con RecipeNLG (el usuario descarga el dataset, ~10 GB). | **No se encuentra archivo LICENSE.** Depende de RecipeNLG. | **No integrado**, por la misma razón. |
| USDA FoodData Central | Composición nutricional de alimentos. | Datos del gobierno de EE. UU. publicados como dominio público (CC0). **Pendiente de confirmar en la página oficial antes de importar.** | Pendiente: motor de cálculo + importación. |

## Qué sí se hace con RecipeNLG / Recipe-Generation-Project
- Se usan como **referencia de ideas** (esquema de receta: título, ingredientes, pasos, entidades; evaluar coherencia). Las ideas generales no están protegidas; el código y los datos concretos sí.
- Chef AI sigue generando con un modelo de lenguaje por API y **valida** el resultado con reglas propias (`src/lib/chef/coherencia.ts`).

## Qué haría falta para usarlos de verdad
1. Confirmar por escrito (autores / sitio del dataset) que se permite el uso comercial, o usar solo para investigación interna sin distribuir resultados ni modelos.
2. Hardware de GPU para ajustar un modelo (no cabe en el alojamiento actual de la web) y un sitio donde servirlo.
3. Revisar el origen de las recetas recopiladas (derechos de terceros).
