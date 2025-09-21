#!/usr/bin/env bash
set -euo pipefail

IMAGE_NAME="dirtycow-redux:latest"
CONTAINER_NAME="dirtycow-redux"
HOST_PORT=8103
CTNR_PORT=8002

up() {
  docker build -t "$IMAGE_NAME" .
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
  docker run -d --name "$CONTAINER_NAME" -p ${HOST_PORT}:${CTNR_PORT} "$IMAGE_NAME"
  echo "Reto arriba: tcp://127.0.0.1:${HOST_PORT} -> container:${CTNR_PORT}"
}

clean() {
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true
  docker rmi "$IMAGE_NAME" >/dev/null 2>&1 || true
  echo "Imagen y contenedor eliminados."
}

reset() {
  clean
  up
}

connect() {
  docker exec -it "$CONTAINER_NAME" /bin/bash
}

case "${1:-}" in
  up) up ;;
  clean) clean ;;
  reset) reset ;;
  connect) connect ;;
  *)
    echo "Uso: $0 {up|clean|reset|connect}"
    exit 1
  ;;
esac
