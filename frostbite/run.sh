#!/usr/bin/env bash
set -euo pipefail

IMAGE="frostbite"
NAME="frostbite"
HOST_PORT="8101"
CONT_PORT="8000"

up() {
  echo "[*] Building image..."
  docker build -t "$IMAGE" .
  echo "[*] Running container..."
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  docker run -d --name "$NAME" -p "${HOST_PORT}:${CONT_PORT}" --restart unless-stopped \
    -e PUBLIC_HOST="172.30.255.144" \
    -e ADMIN_MSG="authorize:admin-panel" \
    -e FLAG="EIAPT{a16005a6d088406f4e6337aa7c74c0cbc5421a0d646f0763386abd05074c1116}" \
    "$IMAGE"
  echo "[+] Up at http://172.30.255.144:${HOST_PORT}  (docs: /docs)"
}

connect() {
  docker exec -it "$NAME" /bin/bash
}

reset() {
  echo "[*] Restarting container..."
  docker restart "$NAME"
}

clean() {
  echo "[*] Stopping & removing..."
  docker rm -f "$NAME" || true
  echo "[*] Removing image..."
  docker rmi "$IMAGE" || true
}

case "${1:-}" in
  up) up ;;
  connect) connect ;;
  reset) reset ;;
  clean) clean ;;
  *)
    echo "Uso: $0 {up|connect|reset|clean}"; exit 1 ;;
esac
