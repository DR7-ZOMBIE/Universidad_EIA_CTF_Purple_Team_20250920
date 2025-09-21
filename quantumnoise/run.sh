#!/usr/bin/env bash
set -euo pipefail

IMAGE="quantumnoise:latest"
NAME="quantumnoise"
HOST_PORT=8106
CTN_PORT=80

case "${1:-up}" in
  up)
    docker build -t "$IMAGE" .
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    docker run -d --name "$NAME" -p ${HOST_PORT}:${CTN_PORT} "$IMAGE"
    echo "# → http://127.0.0.1:${HOST_PORT}"
    ;;
  reset)
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    docker rmi "$IMAGE" >/dev/null 2>&1 || true
    docker build -t "$IMAGE" .
    docker run -d --name "$NAME" -p ${HOST_PORT}:${CTN_PORT} "$IMAGE"
    echo "# → http://127.0.0.1:${HOST_PORT}"
    ;;
  logs)
    docker logs -f "$NAME"
    ;;
  connect)
    docker exec -it "$NAME" /bin/bash
    ;;
  clean)
    docker rm -f "$NAME" >/dev/null 2>&1 || true
    docker rmi "$IMAGE" >/dev/null 2>&1 || true
    ;;
  *)
    echo "Uso: $0 {up|reset|logs|connect|clean}"
    exit 1
    ;;
esac
