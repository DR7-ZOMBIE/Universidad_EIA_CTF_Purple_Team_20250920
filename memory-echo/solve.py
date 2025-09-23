#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, re

XOR_KEY = 0x37
TAG = b"TLBLOG\x00"

def extract_flag(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    off = data.find(TAG)
    if off < 0:
        raise SystemExit(f"[-] No se encontró 'TLBLOG' en {path}")
    i = off + len(TAG)  # empieza después del \x00
    out = bytearray()
    limit = min(len(data), i + 4096)
    while i < limit:
        b = data[i] ^ XOR_KEY
        if b == 0: break
        out.append(b); i += 1
    s = out.decode(errors="ignore")
    m = re.search(r"EIAPT\{[0-9a-fA-F]+\}", s)
    return m.group(0) if m else s

def main():
    img = sys.argv[1] if len(sys.argv) > 1 else "mem.raw"
    print(extract_flag(img))

if __name__ == "__main__":
    main()
