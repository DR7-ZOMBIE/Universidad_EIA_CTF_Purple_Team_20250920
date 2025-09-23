#!/usr/bin/env bash
set -euo pipefail

IMG="${1:-mem.raw}"

if [[ ! -f "$IMG" ]]; then
  echo "Uso: $0 mem.raw"; exit 1
fi

# Offset del tag TLBLOG dentro del binario (decimal)
OFF="$(LC_ALL=C grep -abo 'TLBLOG' "$IMG" | head -n1 | cut -d: -f1 || true)"

if [[ -n "${OFF:-}" ]] && command -v r2 >/dev/null 2>&1; then
  # r2 no-interactivo: seek al tag, s+7, XOR 0x37 sobre un bloque, imprimir con psz
  r2 -n -q -e io.cache=true -w "$IMG" -c "s $OFF; s+ 7; b 192; wox 0x37; psz @ \$\$; q"
  exit 0
fi

# Fallback puro POSIX (dd+od+awk) si no está r2 o no se halló el tag
if [[ -z "${OFF:-}" ]]; then
  echo "No se encontró 'TLBLOG' en $IMG" >&2; exit 2
fi

dd if="$IMG" bs=1 skip=$((OFF+7)) count=512 2>/dev/null \
| od -An -t u1 -v \
| awk '{for(i=1;i<=NF;i++){c=$i^55; if(c==0){print ""; exit} printf "%c", c}}'
