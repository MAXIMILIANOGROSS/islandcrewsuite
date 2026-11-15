#!/usr/bin/env python3
"""Voz neuronal gratuita (Kokoro) como proceso aparte, para el worker. Se ejecuta con el python del entorno kokoro-venv.
Protocolo: lee líneas JSON {"texto","voz","vel","wav"} por stdin; responde una línea "ok" o "error: ..." por cada una."""
import json, sys
import numpy as np, soundfile as sf
from kokoro import KPipeline
pipe = KPipeline(lang_code="e")
print("listo", flush=True)
for linea in sys.stdin:
    try:
        p = json.loads(linea); v = "ef_dora" if p.get("voz") == "mujer" else "em_alex"
        tr = [np.asarray(a) for _, _, a in pipe(p["texto"], voice=v, speed=float(p.get("vel", 0.93)))]
        if not tr: print("error: sin audio", flush=True); continue
        sf.write(p["wav"], np.concatenate(tr), 24000); print("ok", flush=True)
    except Exception as e: print("error: " + str(e)[:200].replace("\n", " "), flush=True)
