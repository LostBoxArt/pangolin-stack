---
title: "bazarr"
slug: homenode-bazarr
type: service
status: active
tags: ["homelab", "homenode", "service", "bazarr"]
aliases: ["bazarr"]
entities:
  primary: homenode-bazarr
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/bazarr/docker-compose.yml", "host-configs/homenode/bazarr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# bazarr

Subtitle manager for Sonarr + Radarr. LinuxServer.io image.

- **Image**: `linuxserver/bazarr:latest` ⚠️
- **Compose file**: `/volume1/docker/config/bazarr/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/bazarr/docker-compose.yml` ✓
- **Port (internal)**: `6767`
- **Router**: `bazarr.example.com`
- **Volumes**:
  - `/volume1/docker/config/bazarr:/config`
  - `/volume1/media/movies:/movies`
  - `/volume1/media/tv:/tv`

## Upstream Sources

- Image docs: <https://docs.linuxserver.io/images/docker-bazarr/>
- Project: <https://www.bazarr.media/>

## Our Compose

```yaml
services:
  bazarr:
    image: linuxserver/bazarr:latest
    container_name: bazarr
    restart: unless-stopped
    environment: [PUID=1000, PGID=1000, TZ=Asia/Jerusalem]
    volumes:
      - /volume1/docker/config/bazarr:/config
      - /volume1/media/movies:/movies
      - /volume1/media/tv:/tv
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:6767/system/status >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks: [traefik_traefik]
    labels:
      - "traefik.http.routers.bazarr.rule=Host(`bazarr.example.com`)"
      - "traefik.http.services.bazarr.loadbalancer.server.port=6767"
```

## Deviations / Findings

- **`:latest` image** (`medium` / NM2).
- **Healthcheck**: `/system/status` is the canonical endpoint for Bazarr
  (not `/ping`, unlike Sonarr/Radarr). Correct.
- **Volumes match Sonarr/Radarr**: Bazarr sees `/movies` and `/tv` at the
  same paths those apps use, which is what Bazarr's
  "path mappings" config expects. No extra path mapping needed in the UI.

## Remediation

Pin the image from
<https://github.com/linuxserver/docker-bazarr/pkgs/container/bazarr>.

## Operational Notes

- Bazarr needs API keys from Sonarr + Radarr (Settings → Sonarr /
  Settings → Radarr). Because all three containers share the
  `traefik_traefik` network, use `http://sonarr:8989` and
  `http://radarr:7878` — no LAN IP, no public DNS round-trip.
- If subtitle downloads stall, check Bazarr's providers panel for
  rate-limit status. OpenSubtitles.com VIP is usually the failure mode.
