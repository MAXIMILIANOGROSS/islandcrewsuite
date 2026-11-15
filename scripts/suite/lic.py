"""Licencias sin conexión: firma Ed25519 (puro Python, sin dependencias).
La app solo lleva la clave PÚBLICA; la privada vive solo en el Mac del propietario."""
import hashlib, json, base64, time, os

p = 2 ** 255 - 19
d = -121665 * pow(121666, p - 2, p) % p
q = 2 ** 252 + 27742317777372353535851937790883648493
def _inv(x): return pow(x, p - 2, p)
def _sha(s): return hashlib.sha512(s).digest()
def _rx(y, sg):
    if y >= p: return None
    x2 = (y * y - 1) * _inv(d * y * y + 1) % p
    if x2 == 0: return None if sg else 0
    x = pow(x2, (p + 3) // 8, p)
    if (x * x - x2) % p: x = x * pow(2, (p - 1) // 4, p) % p
    if (x * x - x2) % p: return None
    return p - x if (x & 1) != sg else x
_gy = 4 * _inv(5) % p; _gx = _rx(_gy, 0); G = (_gx, _gy, 1, _gx * _gy % p)
def _add(P, Q):
    A = (P[1] - P[0]) * (Q[1] - Q[0]) % p; B = (P[1] + P[0]) * (Q[1] + Q[0]) % p
    C = 2 * P[3] * Q[3] * d % p; D = 2 * P[2] * Q[2] % p
    E, F, Gg, H = B - A, D - C, D + C, B + A
    return (E * F % p, Gg * H % p, F * Gg % p, E * H % p)
def _mul(s, P):
    Q = (0, 1, 1, 0)
    while s > 0:
        if s & 1: Q = _add(Q, P)
        P = _add(P, P); s >>= 1
    return Q
def _eq(P, Q): return (P[0] * Q[2] - Q[0] * P[2]) % p == 0 and (P[1] * Q[2] - Q[1] * P[2]) % p == 0
def _enc(P):
    zi = _inv(P[2]); x = P[0] * zi % p; y = P[1] * zi % p
    return int.to_bytes(y | ((x & 1) << 255), 32, "little")
def _dec(s):
    y = int.from_bytes(s, "little"); sg = y >> 255; y &= (1 << 255) - 1
    x = _rx(y, sg)
    return None if x is None else (x, y, 1, x * y % p)
def _exp(sec):
    h = _sha(sec); a = int.from_bytes(h[:32], "little"); a &= (1 << 254) - 8; a |= 1 << 254; return a, h[32:]
def clave_publica(sec): return _enc(_mul(_exp(sec)[0], G))
def firmar(sec, msg):
    a, pre = _exp(sec); A = _enc(_mul(a, G))
    r = int.from_bytes(_sha(pre + msg), "little") % q; R = _enc(_mul(r, G))
    h = int.from_bytes(_sha(R + A + msg), "little") % q
    return R + int.to_bytes((r + h * a) % q, 32, "little")
def verificar(pub, msg, sig):
    if len(sig) != 64: return False
    A = _dec(pub); R = _dec(sig[:32])
    if A is None or R is None: return False
    s = int.from_bytes(sig[32:], "little")
    if s >= q: return False
    h = int.from_bytes(_sha(sig[:32] + pub + msg), "little") % q
    return _eq(_mul(s, G), _add(R, _mul(h, A)))

AQUI = os.path.dirname(os.path.abspath(__file__))
def _pub():
    return base64.b64decode(open(os.path.join(AQUI, "clave-publica.txt")).read().strip())

def crear(sec, cliente, fabricas, caduca=None):
    """caduca: 'AAAA-MM-DD' o None (perpetua). Devuelve el texto de licencia."""
    datos = json.dumps({"cliente": cliente, "fabricas": fabricas, "caduca": caduca}, ensure_ascii=False, sort_keys=True).encode("utf8")
    return base64.urlsafe_b64encode(datos).decode() + "." + base64.urlsafe_b64encode(firmar(sec, datos)).decode()

def comprobar(texto):
    """Devuelve (ok, datos_o_mensaje)."""
    try:
        a, b = texto.strip().split(".")
        datos = base64.urlsafe_b64decode(a.encode()); sig = base64.urlsafe_b64decode(b.encode())
        if not verificar(_pub(), datos, sig): return False, "La licencia no es válida."
        j = json.loads(datos.decode("utf8"))
        if j.get("caduca") and j["caduca"] < time.strftime("%Y-%m-%d"): return False, "La licencia ha caducado el " + j["caduca"] + "."
        return True, j
    except Exception:
        return False, "No se puede leer la licencia. Copia el texto completo."
