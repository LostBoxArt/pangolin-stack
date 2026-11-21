#!/bin/bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose=(docker compose -f "$ROOT_DIR/stacks/core/docker-compose.yml" --env-file "$ROOT_DIR/.env")

gerbil_id=$("${compose[@]}" ps --all -q gerbil)
traefik_id=$("${compose[@]}" ps --all -q traefik)
if [[ -z "$gerbil_id" || -z "$traefik_id" ]]; then
    echo "Gerbil and Traefik must exist before checking their network namespace." >&2
    exit 1
fi
for container_id in "$gerbil_id" "$traefik_id"; do
    if [[ $(docker inspect -f '{{.State.Running}}' "$container_id") != true ]]; then
        echo "Gerbil and Traefik must be running before checking their network namespace." >&2
        exit 1
    fi
done

case $(docker inspect -f '{{.HostConfig.NetworkMode}}' "$traefik_id") in
    container:*) ;;
    *) echo "Traefik is not configured to share a container network namespace." >&2; exit 1 ;;
esac

network_namespace() {
    docker exec "$1" readlink /proc/1/ns/net
}

gerbil_ns=$(network_namespace "$gerbil_id")
traefik_ns=$(network_namespace "$traefik_id")
if [[ "$gerbil_ns" == "$traefik_ns" && "$gerbil_ns" == net:* ]]; then
    echo "Gerbil and Traefik share the current network namespace."
    exit 0
fi

echo "Traefik uses an old network namespace; recreating only Traefik." >&2
"${compose[@]}" up -d --no-deps --pull never --force-recreate traefik

gerbil_id=$("${compose[@]}" ps -q gerbil)
traefik_id=$("${compose[@]}" ps -q traefik)
if [[ -z "$gerbil_id" || -z "$traefik_id" ]]; then
    echo "Core containers are not running after recovery." >&2
    exit 1
fi
gerbil_ns=$(network_namespace "$gerbil_id")
traefik_ns=$(network_namespace "$traefik_id")
if [[ "$gerbil_ns" != "$traefik_ns" || "$gerbil_ns" != net:* ]]; then
    echo "Traefik network namespace recovery failed." >&2
    exit 1
fi
echo "Traefik now shares Gerbil's network namespace."
