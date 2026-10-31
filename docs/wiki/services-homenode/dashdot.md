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
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# dashdot (HomeNode)

System dashboard for HomeNode, separate from [CloudNode Dashdot](../services/dashdot.md). The NAS instance is active and remains deployed.

- **Image**: `mauricenino/dashdot:latest`; observed running version `6.3.4` on 2026-10-27.
- **Compose file**: `/volume1/docker/config/dashdot/docker-compose.yml`.
- **Tracked copy**: `host-configs/homenode/dashdot/docker-compose.yml` (sanitized live snapshot, 2026-10-31).
- **Internal port**: `3001`, routed by HomeNode Traefik at `dash.example.com`.
- **Host access**: unprivileged; `no-new-privileges` is enabled, with `/:/mnt/host:ro`.

## Upstream-supported configuration (reference)

The [official Compose installation](https://getdashdot.com/docs/installation/docker-compose) specifies the host root mount and privileged mode. The [6.3.4 setup implementation](https://github.com/MauriceNino/dashdot/blob/v6.3.4/apps/server/src/setup.ts) reads host network paths and enters the host network namespace through `/mnt/host`.

```yaml
services:
  dash:
    image: mauricenino/dashdot:latest
    container_name: dash
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
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

The NAS's DSM root mount does not expose `/volume1`, so the storage widget
is empty there. This is a Synology mount limitation, not evidence that the
service is missing storage data.

## Host mount repair (2026-10-27)

The previous mount exposed the application's config directory as `/mnt/host`. It was changed to the NAS root read-only, matching the official installation. On 2026-10-31, privileged mode was removed and `no-new-privileges` added. The storage widget remains empty because DSM's root mount does not expose `/volume1`.

The 2026-10-27 host-mount repair was verified at that time. The 2026-10-31 audit found the NAS DSM root mount does not expose `/volume1`, so the storage widget is currently empty. This Synology limitation persists with the unprivileged container and read-only root mount.

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

The HomeNode instance now runs unprivileged with `no-new-privileges`; the prior privileged mode was removed on 2026-10-31. This does not change the NAS limitation that its DSM root mount does not expose `/volume1`.
- The image tag remains `latest`; this maintenance used the existing cached image and performed no version upgrade.
- CloudNode and HomeNode both route `dash.example.com` on separate proxies. DNS and the selected proxy determine which instance is reached. Preserve the active NAS instance; a hostname migration requires checking its callers first.
