#!/usr/bin/env python3
"""Limpia Supabase desde el Mac: baja cada canción al disco (T5 EVO), comprueba que el archivo llegó entero y SOLO entonces la borra de Supabase. Lo lanza el trabajador cuando pulsas «Limpiar Supabase» en la web."""
import os, urllib.request as u
DEST_SUB = "copia-de-supabase"
def limpiar(fm):
    destino = os.path.join(fm.SALIDA, DEST_SUB); os.makedirs(destino, exist_ok=True)
    total = 0; movidas = 0
    for _ in range(10):  # hasta 400 canciones por limpieza
        r = fm._web("/api/oficina/supabase-limpiar", {"accion": "lista"}) or {}; piezas = r.get("piezas") or []
        if not piezas: break
        hechas = 0
        for p in piezas:
            dst = os.path.join(destino, p["path"].replace("/", "__"))
            try:
                if not (os.path.isfile(dst) and os.path.getsize(dst) > 1000):
                    with u.urlopen(u.Request(p["url"]), timeout=300) as rr, open(dst + ".tmp", "wb") as o:
                        esp = int(rr.headers.get("Content-Length") or 0); n = 0
                        while True:
                            b = rr.read(1 << 20)
                            if not b: break
                            o.write(b); n += len(b)
                    if (esp and n != esp) or n < 1000: raise RuntimeError("archivo incompleto")
                    os.replace(dst + ".tmp", dst)
                ok = fm._web("/api/oficina/supabase-limpiar", {"accion": "liberar", "id": p["id"], "ruta_local": dst})
                if ok and ok.get("ok"): movidas += 1; hechas += 1; total += os.path.getsize(dst); print("Limpieza: pasada al disco ->", p["titulo"], flush=True)
            except Exception as e: print("Limpieza: no se toca", p["titulo"], str(e)[:80], flush=True)
        if not hechas: break
    print(f"Limpieza de Supabase: {movidas} canciones pasadas al disco, {total/1e6:.0f} MB liberados.", flush=True)
    return True
