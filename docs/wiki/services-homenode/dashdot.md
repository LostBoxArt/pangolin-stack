---
title: "dashdot (HomeNode)"
slug: homenode-dashdot
type: service
status: active
tags: ["homelab", "homenode", "service", "dashdot"]
aliases: ["dashdot (HomeNode)", "dashdot"]
entities:
  primary: homenode-dashdot
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/dashdot/docker-compose.yml", "host-configs/homenode/dashdot/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-04-17
---
# dashdot (HomeNode)

System dashboard for HomeNode, separate from [CloudNode Dashdot](../services/dashdot.md). The NAS instance is active and remains deployed.

- **Image**: `mauricenino/dashdot:latest`; observed running version `6.3.4` on 2026-10-27.
- **Compose file**: `/volume1/docker/config/dashdot/docker-compose.yml`.
- **Tracked copy**: `host-configs/homenode/dashdot/docker-compose.yml` (sanitized addresses).
- **Internal port**: `3001`, routed by HomeNode Traefik at `dash.example.com`.
- **Host access**: existing `privileged: true`, with `/:/mnt/host:ro`.

## Supported configuration

The [official Compose installation](https://getdashdot.com/docs/installation/docker-compose) specifies the host root mount and privileged mode. The [6.3.4 setup implementation](https://github.com/MauriceNino/dashdot/blob/v6.3.4/apps/server/src/setup.ts) reads host network paths and enters the host network namespace through `/mnt/host`.

```yaml
services:
  dash:
    image: mauricenino/dashdot:latest
    container_name: dash
    restart: unless-stopped
    privileged: true
    volumes:
      - /:/mnt/host:ro
    networks:
      - traefik_traefik
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dash.rule=Host(`dash.example.com`)"
      - "traefik.http.routers.dash.entrypoints=websecure"
      - "traefik.http.routers.dash.tls.certresolver=cloudflare"
      - "traefik.http.services.dash.loadbalancer.server.port=3001"

networks:
  traefik_traefik:
    external: true
```

## Host mount repair (2026-10-27)

The previous mount exposed the application's config directory as `/mnt/host`. It now exposes the NAS root read-only, matching the official installation. Only Dashdot was recreated, using the same cached image, environment and existing privileges.

Verification confirmed the mounted host's `/volume1`, `/proc` mount table and network sysfs are visible. The dashboard returned HTTPS 200 and its API continued reporting four CPU cores, 16.5 GB RAM and six storage entries, including the 12 TB array. Those hardware metrics were already present before repair; the change supplies the missing host filesystem paths.

The NAS runs ASUSTOR ADM and lacks the standard host `etc/os-release` file. The OS widget still reports the container's Alpine release. Do not assume the mount repairs that separate OS identification limitation.

```bash
docker inspect dash --format '{{json .Mounts}}'
docker exec dash test -d /mnt/host/volume1
docker exec dash test -d /mnt/host/sys/class/net
docker exec traefik wget -qO- http://dash:3001/info
docker exec traefik wget -qO- http://dash:3001/load/ram
```

Expected: the mount source is `/`, destination `/mnt/host`, read-only; host paths exist; API responses contain current metrics. Before any further recreation, save the current Compose file. Rollback restores the prior mount line and recreates only `dash` with `--no-deps --pull never`.

## Operational boundaries

- Existing privileged mode was retained because it is part of the documented setup. Removing it or guessing replacement capabilities needs separate widget testing.
- The image tag remains `latest`; this maintenance used the existing cached image and performed no version upgrade.
- CloudNode and HomeNode both route `dash.example.com` on separate proxies. DNS and the selected proxy determine which instance is reached. Preserve the active NAS instance; a hostname migration requires checking its callers first.
