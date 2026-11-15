#!/usr/bin/env python3
"""Asistente: rellena las 7 claves que necesita Cabra Beats personal en .env.local. Lo que escribes NO se ve ni se guarda en ningún otro sitio.
Reutiliza lo que ya tengas en ~/.islandcrew-env. Uso: python3 scripts/rellenar-claves.py"""
import os, re, sys, getpass
AQUI = os.path.dirname(os.path.abspath(__file__)); ENV = os.environ.get("ENV_LOCAL", os.path.join(AQUI, "..", ".env.local")); VIEJO = os.environ.get("ENV_MAC", os.path.expanduser("~/.islandcrew-env"))
CLAVES = [
    ("SUPABASE_SERVICE_ROLE_KEY", "Supabase → tu proyecto → Project Settings → API → «service_role» (botón Reveal). Empieza por eyJ… o sb_secret_…", True),
    ("CRON_SECRET", "La contraseña interna del trabajador del Mac (suele estar ya en tu Mac).", True),
    ("GEMINI_API_KEY", "Google AI Studio → aistudio.google.com/apikey → Create API key (gratis). Empieza por AIza…", True),
    ("GROQ_API_KEY", "console.groq.com → API Keys → Create (gratis). Empieza por gsk_…", True),
    ("YOUTUBE_CLIENT_ID", "Google Cloud Console → APIs y servicios → Credenciales → tu cliente OAuth → «ID de cliente». Termina en .apps.googleusercontent.com", False),
    ("YOUTUBE_CLIENT_SECRET", "En ese mismo cliente OAuth → «Secreto del cliente». Empieza por GOCSPX-…", True),
    ("COLMENA_ACTIVA", "Interruptor: escribe 1", False),
]
def leer(ruta):
    d = {}
    try:
        for l in open(ruta, encoding="utf8"):
            m = re.match(r'^\s*(?:export\s+)?([A-Z0-9_]+)=(.*)$', l.rstrip("\n"))
            if m: d[m.group(1)] = m.group(2).strip().strip('"').strip("'")
    except FileNotFoundError: pass
    return d
def valido(v): return bool(v) and "[SENSITIVE]" not in v
def escribir(clave, valor):
    lineas = open(ENV, encoding="utf8").read().split("\n") if os.path.exists(ENV) else []
    nuevo = f'{clave}="{valor}"'; hecho = False
    for i, l in enumerate(lineas):
        if re.match(rf'^{clave}=', l): lineas[i] = nuevo; hecho = True
    if not hecho: lineas.append(nuevo)
    open(ENV, "w", encoding="utf8").write("\n".join(lineas).rstrip("\n") + "\n")
def main():
    actual, viejo = leer(ENV), leer(VIEJO)
    print("\nVamos a rellenar las claves de Cabra Beats personal. Lo que escribas no se muestra. Si no tienes una, pulsa Intro y la dejamos para luego.\n")
    for k, ayuda, secreta in CLAVES:
        if valido(actual.get(k, "")): print(f"✔ {k}: ya está."); continue
        if valido(viejo.get(k, "")): escribir(k, viejo[k]); print(f"✔ {k}: la he cogido de tu Mac ({os.path.basename(VIEJO)})."); continue
        print(f"\n{k}\n  Dónde: {ayuda}")
        v = (getpass.getpass("  Pega aquí (no se ve): ") if secreta else input("  Pega aquí: ")).strip().strip('"').strip("'")
        if v: escribir(k, v); print(f"  ✔ guardada ({len(v)} caracteres)")
        else: print("  — saltada")
    final = leer(ENV); falta = [k for k, _, _ in CLAVES if not valido(final.get(k, ""))]
    print("\n" + ("✔ Listas las 7 claves." if not falta else "Faltan: " + ", ".join(falta)))
if __name__ == "__main__": main()
