#!/usr/bin/env python3
"""Solo para el propietario. Crea licencias para tus clientes.
Uso:  python3 emitir-licencia.py "Casa Cecilia" carta [AAAA-MM-DD]
La clave privada se guarda FUERA del repositorio y del pendrive."""
import os, sys, base64, secrets
AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, AQUI)
import lic
T5 = "/Volumes/T5 EVO/IslandCrewAI"
CARPETA = os.path.join(T5 if os.path.isdir(T5) else os.path.expanduser("~/IslandCrewAI"), "licencias")
KP = os.path.join(CARPETA, "clave-privada.txt")
os.makedirs(CARPETA, exist_ok=True)
if not os.path.exists(KP):
    open(KP, "w").write(base64.b64encode(secrets.token_bytes(32)).decode()); os.chmod(KP, 0o600)
    print("Clave privada creada en", KP, "· GUÁRDALA en dos sitios; si la pierdes no podrás emitir más licencias.")
sec = base64.b64decode(open(KP).read().strip())
pub = base64.b64encode(lic.clave_publica(sec)).decode()
pp = os.path.join(AQUI, "clave-publica.txt")
if not os.path.exists(pp) or open(pp).read().strip() != pub:
    open(pp, "w").write(pub + "\n"); print("Clave pública escrita en", pp, "(vuelve a construir el pendrive).")
if len(sys.argv) < 3: sys.exit('Uso: emitir-licencia.py "Cliente" carta[,publicaciones,anuncios,musica] [caducidad AAAA-MM-DD]')
t = lic.crear(sec, sys.argv[1], sys.argv[2].split(","), sys.argv[3] if len(sys.argv) > 3 else None)
ok, j = lic.comprobar(t)
assert ok, j
os.makedirs(os.path.join(CARPETA, "emitidas"), exist_ok=True)
open(os.path.join(CARPETA, "emitidas", sys.argv[1].replace(" ", "-") + ".txt"), "w").write(t + "\n")
print("\nLicencia para", sys.argv[1], ":\n\n" + t + "\n")
