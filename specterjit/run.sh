#!/usr/bin/env bash
set -euo pipefail

IMAGE="specterjit"
NAME="specterjit"
HOST_PORT="${HOST_PORT:-8102}"
CONT_PORT="${CONT_PORT:-8001}"

# Token esperado por el servidor (64-bit hex)
EXPECTED_TOKEN_DEFAULT=""

# <<< FLAG embebida aquí >>>
FLAG_DEFAULT='EIAPT{efe46620da6f12021181d9c0d7126069c8ef7ed6d7c928b54ee05a48bcc632fb}'

up() {
  echo "[*] Building image..."
  docker build -t "$IMAGE" .

  echo "[*] Running container..."
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  docker run -d \
    --name "$NAME" \
    --privileged \
    -p "${HOST_PORT}:${CONT_PORT}" \
    --restart unless-stopped \
    -e FLAG="${FLAG:-$FLAG_DEFAULT}" \
    -e EXPECTED_TOKEN="${EXPECTED_TOKEN:-$EXPECTED_TOKEN_DEFAULT}" \
    "$IMAGE"

  echo "[+] Up at http://172.30.255.144:${HOST_PORT}  (API docs: /docs)"
  echo "[+] Download binary:  http://172.30.255.144:${HOST_PORT}/download/specterjit"
  echo "[+] Redeem endpoint:  POST http://172.30.255.144:${HOST_PORT}/redeem  {\"token\":\"<hex>\"}"
}

connect() { docker exec -it "$NAME" /bin/bash; }
reset()   { docker restart "$NAME"; }
clean()   { docker rm -f "$NAME" || true; docker rmi "$IMAGE" || true; }

case "${1:-}" in
  up) up ;;
  connect) connect ;;
  reset) reset ;;
  clean) clean ;;
  *) echo "Uso: $0 {up|connect|reset|clean}"; exit 1 ;;
esac
