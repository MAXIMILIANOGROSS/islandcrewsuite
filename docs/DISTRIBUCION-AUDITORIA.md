# Island Crew Suite — Auditoría de distribución (Fases 1-3)

Fecha: 2026-11-15. Solo lectura: no se ha reconstruido, comprimido ni sobrescrito nada.

## 1. Lo que existe hoy (verificado)

| Pieza | Estado real |
|---|---|
| Instaladores Mac | `Instalar-Mac.command` (69 líneas), `Desinstalar-Mac.command`, `Instalar-Motores-Mac.command` (47 líneas, sin probar de punta a punta) |
| Instalador Windows | `Instalar-Windows.bat` + `instalar.ps1` + `Desinstalar.ps1`. **Nunca probado en un PC real** |
| Motores Windows | No existe instalador |
| Empaquetado | `construir-usb.sh`, `comprimir-usb.sh` (LIGERO, xz), `armar-completa.sh` |
| Paquetes LIGERO | `win.tar.xz` 55 MB, `mac-arm64.tar.xz` 42 MB, `mac-x64.tar.xz` 47 MB; zip total 137 MB (generado 15-nov, con paquetes de las 17:03: **sin** los cambios de Conexiones/traducciones/fotos de hoy) |
| Licencias | `lic.py`: firma Ed25519 propia, verificación offline con clave pública. Separa descarga de activación (la descarga no necesita licencia; el uso sí) |
| Actualizaciones | **No existe** sistema de actualización ni número de versión en la instalación |
| Descarga con reanudación / SHA-256 | **No existe** |
| Manifiesto | **No existe** (borrador abajo) |

## 2. Inventario real de COMPLETO (medido, no supuesto)

Total de la carpeta PENDRIVE 100G: **28 GB** (medido con `du`).

| Componente | Tamaño | Nota |
|---|---|---|
| checkpoints/acestep-v15-turbo | 4,5 GB | modelo de música |
| checkpoints/acestep-5Hz-lm-1.7B | 3,5 GB | |
| checkpoints/acestep-5Hz-lm-0.6B | 1,3 GB | |
| checkpoints/Qwen3-Embedding-0.6B | 1,1 GB | |
| checkpoints/vae | 323 MB | |
| ollama-models (qwen2.5:7b) | 4,4 GB | |
| rvc (total) | 12 GB | ver hallazgos |
| acestep (código) | 333 MB | |
| hf-cache | 325 MB | |
| app-musica | 45 MB | |
| kokoro | 256 KB | |

La suma de las partes medidas no llega a 28 GB: el resto está en carpetas ocultas dentro de `rvc` (entornos/dependencias) que el `du` por carpeta visible no desglosó. **Pendiente de desglosar** antes del manifiesto definitivo.

## 3. Hallazgos que cambian la decisión

1. **Voz personal dentro de COMPLETO.** `rvc/assets/weights` contiene `VozMaximiliano.pth` y `mivoz.pth`. Son modelos de la voz del propietario: **no deben ir en un paquete que se entrega a clientes** sin decisión expresa.
2. **`rvc/logs` pesa 1,5 GB**: son registros de entrenamiento, no hacen falta para funcionar. Candidatos a excluir (no se borra nada: solo se excluye del paquete).
3. **Licencias de modelos sin verificar.** `LICENCIAS.txt` cubre FFmpeg, Python, Pillow y segno, pero **no** ACE-Step, RVC, Kokoro, Qwen ni Ollama. Hay que comprobar sus derechos de redistribución comercial antes de ofrecerlos en un paquete. Regla propuesta: si no se puede redistribuir, el instalador los descarga del origen oficial en el equipo del cliente.
4. **FFmpeg con componentes GPL** ya se distribuye en LIGERO: está documentado en `LICENCIAS.txt`; mantener.
5. El repo de GitHub es **público**: ahí solo debe haber instaladores pequeños y código, nunca modelos ni voces.

## 4. Arquitectura propuesta

- **Manifiesto central** `manifest.json` (versión, canal stable/beta, componentes con id, versión, tamaño, SO, arquitectura, URL, SHA-256, dependencias, requisitos).
- **LIGERO** → GitHub Releases (límite 2 GB por archivo; 137 MB cabe).
- **Modelos y motores** → componentes opcionales y bajo demanda: se descargan desde su origen oficial cuando la licencia lo permite, o desde almacenamiento propio si se contrata.
- **COMPLETO** → pendrive (offline) o, en partes (`.part01…`), almacenamiento de objetos. Tarifas de R2 y similares: **por verificar** antes de recomendar; no se contrata nada sin autorización.
- **Actualizaciones**: el manifiesto compara versiones por componente y descarga solo lo que cambió.
- **Gestor de descargas**: reanudable (HTTP Range), SHA-256, reintentos, comprobación de espacio, registro sin secretos.

## 5. Borrador de manifiesto (sin hashes, solo estructura real)

```json
{
  "product": "Island Crew Suite",
  "version": "PENDIENTE",
  "channels": ["stable", "beta"],
  "components": [
    {"id": "core-mac-arm64", "size_mb": 42, "required": true},
    {"id": "core-mac-x64",   "size_mb": 47, "required": true},
    {"id": "core-win",       "size_mb": 55, "required": true},
    {"id": "acestep",        "size_mb": 333},
    {"id": "acestep-checkpoints", "size_mb": 10700},
    {"id": "ollama-qwen2.5-7b", "size_mb": 4400},
    {"id": "rvc-engine",     "size_mb": "PENDIENTE de desglose"},
    {"id": "kokoro",         "size_mb": 0.25}
  ],
  "sha256": "PENDIENTE: se calcula al generar los paquetes"
}
```

## 6. Fases siguientes (nada se ejecuta sin tu visto bueno)

1. Verificar Conexiones y traducciones en la Suite instalada (bloquea cualquier reconstrucción).
2. Decidir qué se hace con las voces `.pth` y con `rvc/logs`.
3. Comprobar licencias de redistribución de cada modelo.
4. Escribir `generar-manifiesto.sh` y `generar-checksums.sh` (solo crean archivos nuevos).
5. Número de versión en la instalación + gestor de descargas + actualizaciones.
6. Instalador modular con selección de componentes.
7. Pruebas reales: Mac ARM (disponible), Mac Intel y Windows (sin máquina disponible: **pendientes**).

## 7. Estado

| Elemento | Estado | Verificación |
|---|---|---|
| LIGERO | zip existente (137 MB), desactualizado | tamaño medido; sin ejecutar instalación limpia |
| COMPLETO | carpeta de 28 GB, sin zip | tamaño medido |
| macOS ARM | instalador existe | usado en esta máquina |
| macOS Intel | paquete existe | sin probar |
| Windows | instalador existe | sin probar |
| Descargas reanudables | no existe | — |
| Actualizaciones | no existe | — |
| Licencias | funcionan | firma Ed25519, verificación local |
| Hosting | sin decidir | coste actual: 0 € |
| Web de descargas | no existe | — |
