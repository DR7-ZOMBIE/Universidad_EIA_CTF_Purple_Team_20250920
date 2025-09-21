#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, os, math, json, argparse, base64

# --- HTTP helpers (requests si está, sino urllib) ---
try:
    import requests
    def http_get(url):
        r = requests.get(url, timeout=15)
        return r.status_code, r.content, dict(r.headers)
    def http_post_json(url, obj):
        r = requests.post(url, json=obj, timeout=15)
        return r.status_code, r.content, dict(r.headers)
except Exception:
    import urllib.request, urllib.error
    def http_get(url):
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            return resp.getcode(), resp.read(), dict(resp.headers)
    def http_post_json(url, obj):
        data = json.dumps(obj).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                return resp.getcode(), resp.read(), dict(resp.headers)
        except urllib.error.HTTPError as e:
            return e.code, e.read(), dict(getattr(e, "headers", {}))

# --- Bits helpers ---
def unpack_bits_lsb_first(buf: bytes, nbits_hint: int | None = None):
    """Desempaqueta bits LSB-first por byte (igual que el servidor).
       Si nbits_hint está, recorta exactamente a N bits."""
    bits = []
    for b in buf:
        # LSB primero: bit 0,1,...,7
        bits.append(b & 1)
        bits.append((b >> 1) & 1)
        bits.append((b >> 2) & 1)
        bits.append((b >> 3) & 1)
        bits.append((b >> 4) & 1)
        bits.append((b >> 5) & 1)
        bits.append((b >> 6) & 1)
        bits.append((b >> 7) & 1)
    if nbits_hint is not None and len(bits) > nbits_hint:
        bits = bits[:nbits_hint]
    return bits

def derive_128bits_fourier_like(bits, stride=4):
    """Replica la derivación del servidor:
       x[n]=+1/-1, para k=1..128: S_k = sum x[n]*sin(2π k n/N) con step=stride
       bit_k = 1 si S_k>0, si no 0."""
    N = len(bits)
    x = [1 if b else -1 for b in bits]
    out = [0]*128
    for k in range(1, 129):
        w = (2.0 * math.pi * k) / N
        s = 0.0
        # stride para acelerar y mantener el mismo signo global que el server
        for n in range(0, N, stride):
            s += x[n] * math.sin(w * n)
        out[k-1] = 1 if s > 0 else 0
    return out

def pack_128bits_lsb_first(bits128):
    """Empaqueta 128 bits (lista de 0/1) en 16 bytes LSB-first por byte."""
    if len(bits128) != 128:
        raise ValueError("bits128 debe tener longitud 128")
    out = bytearray(16)
    for i, b in enumerate(bits128):
        if b:
            out[i//8] |= (1 << (i % 8))
    return bytes(out)

def bits_to_str(bits128):
    return "".join("1" if b else "0" for b in bits128)

# --- Solver principal ---
def solve_online(base_url: str):
    base = base_url.rstrip("/")
    # 1) Metadata (para conocer N)
    code, body, _ = http_get(f"{base}/api/metadata")
    if code != 200:
        print(f"[!] No pude obtener metadata ({code})")
        return False
    meta = json.loads(body.decode("utf-8", errors="ignore"))
    N = int(meta.get("n_bits", 262144))

    # 2) Descargar qrng.bin
    code, data, _ = http_get(f"{base}/download/qrng.bin")
    if code != 200:
        print(f"[!] No pude descargar qrng.bin ({code})")
        return False

    # 3) Desempaquetar y derivar clave
    bits = unpack_bits_lsb_first(data, N)
    key_bits = derive_128bits_fourier_like(bits, stride=4)
    key_bytes = pack_128bits_lsb_first(key_bits)
    key_hex = key_bytes.hex()

    print(f"[i] N={N} bits; key_hex (derivada) = {key_hex}")

    # 4) Enviar al verificador
    code, resp, _ = http_post_json(f"{base}/api/submit", {"key_hex": key_hex})
    try:
        ans = json.loads(resp.decode("utf-8", errors="ignore"))
    except Exception:
        ans = {"ok": False, "raw": resp[:200]}
    if ans.get("ok"):
        print(f"[+] FLAG: {ans.get('flag')}")
        return True
    else:
        dist = ans.get("distance")
        if dist is not None:
            print(f"[-] Clave incorrecta. Hamming distance: {dist}")
        else:
            print(f"[-] Respuesta no válida del servidor ({code}): {ans}")
        return False

def solve_offline(bin_path: str):
    """Modo offline: lee un qrng.bin local y saca la key_hex (imprímela y pégala en la web)."""
    with open(bin_path, "rb") as f:
        data = f.read()
    N = len(data) * 8
    bits = unpack_bits_lsb_first(data, N)
    key_bits = derive_128bits_fourier_like(bits, stride=4)
    key_bytes = pack_128bits_lsb_first(key_bits)
    key_hex = key_bytes.hex()
    print(f"[i] qrng.bin local ({len(data)} bytes ~ {N} bits)")
    print(f"[+] key_hex (derivada): {key_hex}")
    print("[i] Pega ese key_hex en la UI o envíalo a /api/submit para obtener la flag.")

def main():
    ap = argparse.ArgumentParser(description="QuantumNoise solver (Fourier-like, stdlib)")
    ap.add_argument("--base", default="http://127.0.0.1:8106", help="URL base del reto (default: http://127.0.0.1:8106)")
    ap.add_argument("--file", help="Ruta a qrng.bin local (modo offline: imprime key_hex)")
    args = ap.parse_args()

    if args.file:
        if not os.path.isfile(args.file):
            print("[!] Archivo no encontrado:", args.file); sys.exit(1)
        solve_offline(args.file)
    else:
        ok = solve_online(args.base)
        sys.exit(0 if ok else 2)

if __name__ == "__main__":
    main()
