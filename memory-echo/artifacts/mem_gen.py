#!/usr/bin/env python3
import sys, struct, os, random

MAGIC = b"KVMEM01"
OUT   = sys.argv[1] if len(sys.argv) > 1 else "artifacts/mem.raw"

# Cambia la flag si quieres rotarla
FLAG = b"EIAPT{7103292cb6d011ca562f7c6e752a6d196251f012cc38ab467f9f5ff779926eb2}"
XOR_KEY = 0x37

SIZE = 8 * 1024 * 1024  # ~8MB
FILL = b"\x00"

# Offsets “didácticos”
OFF_PML4 = 0x0010_0000
OFF_PDPT = 0x0012_0000
OFF_PDT  = 0x0014_0000
OFF_PT   = 0x0016_0000
OFF_CODE = 0x0040_0000
OFF_TLB  = 0x0050_0000

def put(buf, off, data):
    buf[off:off+len(data)] = data

def write_ept_chain(buf):
    # Etiquetas ASCII para ayudar al jugador con strings/iz
    put(buf, OFF_PML4, b"EPTP\x00PML4\x00" + struct.pack("<Q", OFF_PDPT))
    put(buf, OFF_PDPT, b"PDPT\x00" + struct.pack("<Q", OFF_PDT))
    put(buf, OFF_PDT,  b"PDT\x00"  + struct.pack("<Q", OFF_PT))
    put(buf, OFF_PT,   b"PT\x00"   + struct.pack("<Q", OFF_CODE))
    # Una dirección “guest phys base” falsa
    put(buf, OFF_PML4 + 0x30, b"GPA\x00" + struct.pack("<Q", 0x00000000A0000000))

def write_hypercall_stubs(buf):
    # Un pequeño stub x86_64 con VMCALL (Intel) y VMMCALL (AMD)
    code = bytearray()
    # mov eax,0x1337; nop; vmcall; nop; vmcall; vmmcall
    code += b"\xB8\x37\x13\x00\x00"   # mov eax,0x1337
    code += b"\x90"                   # nop
    code += b"\x0F\x01\xC1"           # vmcall
    code += b"\x90"                   # nop
    code += b"\x0F\x01\xC1"           # vmcall
    code += b"\x0F\x01\xD9"           # vmmcall
    # padding + una pista en ASCII
    code += b"\x90" * 64
    code += b"hypercall-resto: revisar TLBLOG cerca...\x00"
    put(buf, OFF_CODE, code)

def write_tlb_log(buf):
    # “TLBLOG” + flag en XOR 0x37 + pie
    data = bytearray()
    data += b"TLBLOG\x00"
    data += bytes([b ^ XOR_KEY for b in FLAG])
    data += b"\x00ENDTLB\x00"
    put(buf, OFF_TLB, data)

def main():
    os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
    buf = bytearray(FILL * SIZE)
    put(buf, 0, MAGIC + b"\x00" * (0x200 - len(MAGIC)))  # header sencillo
    write_ept_chain(buf)
    write_hypercall_stubs(buf)
    write_tlb_log(buf)
    with open(OUT, "wb") as f:
        f.write(buf)
    print(f"[+] Generado {OUT} ({SIZE} bytes)")

if __name__ == "__main__":
    main()
