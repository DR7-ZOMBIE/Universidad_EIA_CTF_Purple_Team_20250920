#!/usr/bin/env bash
# solve.sh — Explota Frostbite (Threshold Misbinding / Nonce Reuse)
# Requisitos: bash + python3 (stdlib), acceso HTTP al servicio.
set -euo pipefail

HOST="${HOST:-209.159.156.142:8101}"
PORT="${PORT:-8101}"
BASE="http://${HOST}:${PORT}"

echo "[*] Target: ${BASE}"

python3 - <<'PY'
import hashlib, json, os, sys, urllib.request, urllib.error
from urllib.parse import urlencode
from random import SystemRandom

# === Parámetros cripto (idénticos a app/config.py) ===
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
g = 5
ADMIN_MSG = "authorize:admin-panel"
P_MINUS_1 = p - 1  # ¡Clave!: firmar modulo (p-1) en el grupo multiplicativo

HOST = os.environ.get("HOST", "209.159.156.142")
PORT = os.environ.get("PORT", "8101")
BASE = f"http://{HOST}:{PORT}"

rnd = SystemRandom()

def H_int(R_int, msg):
    h = hashlib.sha256()
    h.update(R_int.to_bytes(64, 'big'))
    h.update(msg.encode())
    return int.from_bytes(h.digest(), 'big') % q

def http_post(path, data):
    url = BASE + path
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read().decode())

def http_get(path, params):
    url = BASE + path + "?" + urlencode(params)
    with urllib.request.urlopen(url, timeout=10) as r:
        return json.loads(r.read().decode())

def inv_mod(a, m):
    return pow(a, -1, m)

participants = ["A","B","C"]

print(f"[*] 1) Creando sesión con participants={participants} …")
resp = http_post("/session/start", {"participants":participants})
sid = resp["session_id"]
print(f"[+] session_id = {sid}")

print("[*] 2) Round1 (mantiene/nonces globales) …")
_ = http_post("/sign/round1", {"session_id": sid, "participants":participants})

print("[*] 3) Firma 1 sobre m1 …")
sig1 = http_post("/sign/round2", {"session_id": sid, "message":"m1"})
R = int(sig1["R"]); s1 = int(sig1["s"]); e1 = int(sig1["e"])
print(f"[+] Firma1: R={R}, s1={s1}, e1={e1}")

print("[*] 4) Round1 de nuevo (refuerza el reuse) …")
_ = http_post("/sign/round1", {"session_id": sid, "participants":participants})

print("[*] 5) Firma 2 sobre m2 (debería tener el MISMO R) …")
sig2 = http_post("/sign/round2", {"session_id": sid, "message":"m2"})
R2 = int(sig2["R"]); s2 = int(sig2["s"]); e2 = int(sig2["e"])
print(f"[+] Firma2: R={R2}, s2={s2}, e2={e2}")

if R != R2:
    print("[-] Error: R difiere entre firmas; reintenta el flujo.", file=sys.stderr)
    sys.exit(2)

print("[*] 6) Recuperando la clave privada x_total …")
num = (s1 - s2) % q
den = (e1 - e2) % q
x = (num * inv_mod(den, q)) % q
print(f"[+] x_total (privada global) = {hex(x)}")

print("[*] 7) Firmando offline el ADMIN_MSG (mod p-1) …")
k = rnd.randrange(1, q)
R_admin = pow(g, k, p)
e_admin = H_int(R_admin, ADMIN_MSG)

# ¡Aquí el FIX! s = (k + e*x) mod (p-1) para que g^s == R * Y^e (mod p)
s_admin = ( (k % P_MINUS_1) + ((e_admin % P_MINUS_1) * (x % P_MINUS_1)) ) % P_MINUS_1
print(f"[+] Firma admin: R={R_admin}, s={s_admin}, e={e_admin}")

# (Opcional) verificación rápida en el servidor
try:
    ver = http_post("/verify", {"R": R_admin, "s": s_admin, "message": ADMIN_MSG})
    print(f"[*] /verify: {ver}")
except Exception as e:
    print(f"[!] /verify falló (no es crítico): {e}")

print("[*] 8) Solicitando FLAG …")
flag_resp = http_get("/admin/flag", {"R":str(R_admin), "s":str(s_admin), "m":ADMIN_MSG})
print(f"[+] FLAG = {flag_resp.get('flag')}")
PY
