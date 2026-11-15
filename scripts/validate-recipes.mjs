import { RECETARIO as RECETAS, PRODUCTOS_TODOS as PRODUCTOS } from "../src/lib/kitchen/recetario.ts";
import { validarCatalogo } from "../src/lib/kitchen/validate.ts";
const i = validarCatalogo(RECETAS, PRODUCTOS);
console.log(`Recetas examinadas: ${i.total} · válidas: ${i.validas} · inválidas: ${i.invalidas} · errores: ${i.errores.length} · avisos: ${i.avisos.length}`);
for (const e of i.errores) console.log(`ERROR  ${e.receta} · ${e.ubicacion}: ${e.mensaje}`);
for (const a of i.avisos.filter((x) => x.mensaje !== "Pendiente de revisión por un chef")) console.log(`aviso  ${a.receta} · ${a.ubicacion}: ${a.mensaje}`);
process.exit(i.errores.length ? 1 : 0);
