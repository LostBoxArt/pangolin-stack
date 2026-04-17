---
title: "radarr"
slug: homenode-radarr
type: service
status: active
tags: ["homelab", "homenode", "service", "radarr"]
aliases: ["radarr"]
entities:
  primary: homenode-radarr
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/radarr/docker-compose.yml", "host-configs/homenode/radarr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# radarr

Movie manager. LinuxServer.io image. Twin of [sonarr](./sonarr.md), with
`/movies` instead of `/tv`.

- **Image**: `linuxserver/radarr:latest` ⚠️
- **Compose file**: `/volume1/docker/config/radarr/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/radarr/docker-compose.yml` ✓
- **Port (internal)**: `7878`
- **Router**: `radarr.example.com`
- **Volumes**:
  - `/volume1/docker/config/radarr:/config`
  - `/volume1/media/movies:/movies`
  - `/volume1/media/downloads:/downloads`

## Upstream Sources

- Image docs: <https://docs.linuxserver.io/images/docker-radarr/>

## Our Compose

```yaml
services:
  radarr:
    image: linuxserver/radarr:latest
    container_name: radarr
    restart: unless-stopped
    environment: [PUID=1000, PGID=1000, TZ=Asia/Jerusalem]
    volumes:
      - /volume1/docker/config/radarr:/config
      - /volume1/media/movies:/movies
      - /volume1/media/downloads:/downloads
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:7878/ping >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks: [traefik_traefik]
    labels:
      - "traefik.http.routers.radarr.rule=Host(`radarr.example.com`)"
      - "traefik.http.services.radarr.loadbalancer.server.port=7878"
```

## Findings

Shared with [sonarr](./sonarr.md) — same LSIO pattern, same `:latest`
drift, same hardlink design.

## Remediation

Pin the image from
<https://github.com/linuxserver/docker-radarr/pkgs/container/radarr>.

## Operational Notes

- **Quality profiles** should be managed centrally via
  [profilarr](./profilarr.md) or [recyclarr](./recyclarr.md), not edited
  by hand in Radarr's UI — your changes will get overwritten on next sync.
- Root folder: `/movies` inside the container = `/volume1/media/movies` on
  the host.
