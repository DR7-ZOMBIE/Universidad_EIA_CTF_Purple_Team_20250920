#!/usr/bin/env python3
import sys, os, subprocess

ALLOWED_EXT = (".mem", ".raw")
MAGIC = b"KVMEM01"

def ok_header(path):
    try:
        with open(path, "rb") as f:
            return f.read(len(MAGIC)) == MAGIC
    except Exception:
        return False

def main():
    if len(sys.argv) < 2:
        print("Uso: viewer.py <mem.raw|mem.mem>")
        sys.exit(1)
    p = sys.argv[1]
    ext_ok  = p.lower().endswith(ALLOWED_EXT)
    head_ok = ok_header(p)

    if not (ext_ok and head_ok):
        # Lanza el “ransom fake” (solo UI)
        here = os.path.dirname(os.path.abspath(__file__))
        trap = os.path.join(here, "trap_ransom.py")
        print("[!] Formato sospechoso. Activando interfaz de alerta...")
        try:
            subprocess.run([sys.executable, trap], check=False)
        except Exception:
            pass
        sys.exit(2)

    print("[+] Cabecera OK y extensión válida.")
    print("[i] Sugerencias radare2:")
    print("    r2 -e asm.arch=x86 -e asm.bits=64 -n mem.raw")
    print("    aaa; izz | grep -E 'EPTP|PML4|PDPT|PDT|PT|TLBLOG'")
    print("    /x 0f01c1    # buscar VMCALL")
    print("    px 128 @ 0x500000  # TLBLOG; XOR 0x37 para recuperar la flag")

if __name__ == "__main__":
    main()
