#!/usr/bin/env bash
set -euo pipefail

IMAGE="memory-echo:latest"
NAME="memory-echo"
HOST_PORT=8105
CTNR_PORT=80

case "${1:-}" in
  up)
    docker build -t "$IMAGE" .
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    docker run -d --name "$NAME" -p ${HOST_PORT}:${CTNR_PORT} "$IMAGE"
    echo "Memory Echo arriba: http://127.0.0.1:${HOST_PORT}"
    ;;
  reset)
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    docker rmi "$IMAGE"  >/dev/null 2>&1 || true
    docker build -t "$IMAGE" .
    docker run -d --name "$NAME" -p ${HOST_PORT}:${CTNR_PORT} "$IMAGE"
    echo "Memory Echo reiniciado: http://127.0.0.1:${HOST_PORT}"
    ;;
  logs)
    docker logs -f "$NAME"
    ;;
  connect)
    docker exec -it "$NAME" /bin/sh
    ;;
  *)
    echo "Uso: $0 {up|reset|logs|connect}"
    ;;
esac
