// Genera src/data/modulos.generated.json leyendo la aplicación real. Se ejecuta solo antes de cada build (prebuild).
import { writeFileSync, mkdirSync } from "node:fs";
const { descubrir, informe } = await import("../src/lib/registro-modulos/descubrir.ts");
const modulos = descubrir(process.cwd());
mkdirSync("src/data", { recursive: true });
writeFileSync("src/data/modulos.generated.json", JSON.stringify({ version: 1, informe: informe(modulos), modulos }, null, 1) + "\n");
console.log(`registro-modulos: ${modulos.length} módulos descubiertos`);
