#!/usr/bin/env python3
import sys, time, json, urllib.request, urllib.error, email.utils

DEFAULT_BASE = "http://209.159.156.142:8101"
DEFAULT_WINDOW = 5  # ±5 s como en el servidor

# ===== funciones de token (idénticas a tu backend) =====
def u64(x): return x & 0xFFFFFFFFFFFFFFFF
def ror(x,n): n &= 63; return u64((x >> n) | (x << (64-n)))
def rol(x,n): n &= 63; return u64((x << n) | (x >> (64-n)))

def mix1(t):
    C=0x9e3779b97f4a7c15; M1=0xF51C3F3D558FCCD3; M2=0xC4CEB9FE1A85EC53
    x=u64(((t^C)>>33)^t^C); x=u64(x*M1); return u64((x^(x>>33))*M2)

def mix2(x):
    C=0xC6A4A7935BD1E995; M1=0xF51C3F3D558FCCD3; M2=0xC4CEB9FE1A85EC53
    x=u64(((x^C)>>33)^x^C); x=u64(x*M1); return u64((x^(x>>33))*M2)

def jit_consts(U):
    K1=u64(rol(U,7)^0xB5E2D4C7A19F8871)
    K2=u64(rol(U,13)^0x7C8A11F0D3B42955)
    K3=u64(ror(U,19)^0xA1C3E5F7092B4D6F)
    return K1,K2,K3

def compute_token(t, U=0xA5A5A5A5A5A5A5A5):
    u=mix1(t); x=u64(u^(u>>33)); K1,K2,K3=jit_consts(U)
    r=u64(x^K1); r=ror(r,13); r=u64(r+K2); r=u64(r*K3); r=ror(r,41)
    z=mix2(r); return f"{u64(z^(z>>33)^0x27D4EB2F165667C5):016x}"
# =======================================================

def redeem_url(base):
    base = base.rstrip("/")
    return base if base.endswith("/redeem") else base + "/redeem"

def health_url(base):
    base = base.rstrip("/")
    return base + "/health"

def server_now(base):
    """Intenta leer la hora del servidor desde /health (cabecera Date).
    Si falla, retorna time.time() local."""
    try:
        with urllib.request.urlopen(health_url(base), timeout=3) as r:
            date_hdr = r.headers.get("Date")
            if date_hdr:
                dt = email.utils.parsedate_to_datetime(date_hdr)
                return int(dt.timestamp())
    except Exception:
        pass
    return int(time.time())

def zigzag_offsets(window):
    """0,-1,1,-2,2,... hasta ±window"""
    yield 0
    for k in range(1, window+1):
        yield -k
        yield +k

def try_redeem(base, window=DEFAULT_WINDOW):
    url = redeem_url(base)
    now = server_now(base)

    for d in zigzag_offsets(window):
        tok = compute_token(now + d)
        data = json.dumps({"token": tok}).encode()
        req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=4) as resp:
                body = resp.read().decode(errors="replace")
        except urllib.error.HTTPError as e:
            # Leer cuerpo de error por si retorna JSON útil
            try:
                body = e.read().decode(errors="replace")
            except Exception:
                body = ""
        except Exception as e:
            body = ""

        # Log corto en stderr (opcional)
        sys.stderr.write(f"[*] t={now+d} token={tok} => {body[:120]}\n")

        # Intenta parsear JSON y extraer flag
        try:
            j = json.loads(body)
            if isinstance(j, dict) and ("flag" in j):
                return j["flag"]
        except Exception:
            pass

        # Fallback: buscar patrón EIAPT{...} en texto
        if "EIAPT{" in body:
            start = body.find("EIAPT{")
            end = body.find("}", start)
            if end != -1:
                return body[start:end+1]

    return None

def main():
    base = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE
    flag = try_redeem(base, window=DEFAULT_WINDOW)
    if flag:
        print(flag)
        sys.exit(0)
    else:
        print("No se pudo obtener la FLAG", file=sys.stderr)
        sys.exit(2)

if __name__ == "__main__":
    main()
