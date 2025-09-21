#!/usr/bin/env bash
set -euo pipefail

IMAGE="saml-hydra:latest"
NAME="saml-hydra"
HOST_PORT=8104
CTNR_PORT=80

up() {
  docker build -t "$IMAGE" .
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  docker run -d --name "$NAME" -p ${HOST_PORT}:${CTNR_PORT} "$IMAGE"
  echo "SAML Hydra arriba: http://127.0.0.1:${HOST_PORT}"
}

clean() {
  docker rm -f "$NAME" >/dev/null 2>&1 || true
  docker rmi "$IMAGE" >/dev/null 2>&1 || true
  echo "Imagen y contenedor eliminados."
}

reset() { clean; up; }
connect() { docker exec -it "$NAME" /bin/sh; }

case "${1:-}" in
  up) up ;;
  clean) clean ;;
  reset) reset ;;
  connect) connect ;;
  *) echo "Uso: $0 {up|clean|reset|connect}" ; exit 1 ;;
esac
