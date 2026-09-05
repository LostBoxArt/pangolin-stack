---
title: "seerr"
slug: homenode-seerr
type: service
status: active
tags: ["homelab", "homenode", "service", "seerr"]
aliases: ["seerr"]
entities:
  primary: homenode-seerr
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/seerr/docker-compose.yml", "host-configs/homenode/seerr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-09-05
last_lint: 2026-09-05
---
# seerr

Media request front-end for end users — they ask for a movie / show, it
hands the request to Sonarr / Radarr for fulfilment.

- **Image**: `ghcr.io/seerr-team/seerr:v3.4.1` ✓
- **Compose file**: `/volume1/docker/config/seerr/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/seerr/docker-compose.yml` ✓
- **Port (internal)**: `5055`
- **Router**: `request.example.com`
- **Volume**: `/volume1/docker/config/jellyseerr:/app/config` ✓ intentional legacy directory; verified live and protected by backup

## Upstream Sources

- Official project: <https://github.com/seerr-team/seerr>
- Original Jellyseerr: <https://github.com/fallenbagel/jellyseerr>
- Ancestor Overseerr: <https://github.com/sct/overseerr>

## Our Compose

```yaml
services:
  seerr:
    image: ghcr.io/seerr-team/seerr:v3.4.1
    container_name: seerr
    init: true
    restart: unless-stopped
    security_opt: ["no-new-privileges:true"]
    user: "1000:1000"
    environment:
      - LOG_LEVEL=debug
      - TZ=Asia/Jerusalem
    deploy:
      resources:
        limits: { memory: 1G }
        reservations: { memory: 512M }
    volumes:
      - /volume1/docker/config/jellyseerr:/app/config
    healthcheck:
      test: wget --no-verbose --tries=1 --spider http://localhost:5055/api/v1/status || exit 1
      start_period: 20s
      timeout: 3s
      interval: 15s
      retries: 3
    networks:
      - traefik_traefik
    labels:
      - "traefik.http.routers.seerr.rule=Host(`request.example.com`)"
      - "traefik.http.services.seerr.loadbalancer.server.port=5055"
```

### Current Deployment (verified 2026-09-05)

- Container: `seerr` on HomeNode; image `ghcr.io/seerr-team/seerr:v3.4.1`.
- Data: `/volume1/docker/config/jellyseerr:/app/config`.
- Compose source: `/volume1/docker/config/seerr/docker-compose.yml`.
- Healthcheck: healthy; internal Traefik route returned HTTP 200.
- A verified backup was taken before recreation; the database and settings
  hashes matched afterward.

## Deviations / Findings

### F-N-SEERR-1 — official Seerr project and pinned stable release (resolved 2026-09-05)
`seerr-team/seerr` is the official Seerr project. The live container was
verified at stable release `v3.4.1`, which is also the current upstream latest
release. Keep the image pinned to that tag and check the official release page
before future upgrades.

### F-N-SEERR-2 — data volume is `jellyseerr/` (intentional)
`/volume1/docker/config/jellyseerr:/app/config` is the verified live mount.
The directory name differs from the service name because this state originated
as Jellyseerr. It must not be renamed during routine maintenance. A verified
backup was created before the v3.4.1 recreation; the settings and database
hashes were unchanged.

### F-N-SEERR-3 — commented IPAM removed (resolved 2026-09-05)
The live Compose definition uses the external `traefik_traefik` network without a
hard-coded container address or dangling IPAM comment.

### F-N-SEERR-4 — mutable image tag (resolved 2026-09-05)
The image is now pinned to the verified upstream stable release `v3.4.1`.
Future upgrades must compare the official release tag and image digest first.

### F-N-SEERR-5 — `LOG_LEVEL=debug` in steady state (`low`)
Debug logging is fine when diagnosing, but leaves it in production
generates a lot of noise and bloats the `/app/config/logs/` directory.
Drop to `info` once the fork is stable in your environment.

## Remediation

No image migration is required. Keep `ghcr.io/seerr-team/seerr:v3.4.1` and
upgrade only after checking the official release and preserving a verified
backup of the `jellyseerr` data directory.
### Positive baseline items (keep these)

This is actually one of the better-hardened compose files on HomeNode:

- `init: true` — reaps zombie processes from the node runtime.
- `security_opt: no-new-privileges` — stops privilege escalation via
  setuid binaries inside the container.
- `deploy.resources.limits.memory: 1G` — prevents a runaway from OOM-ing
  the NAS.
- Explicit healthcheck with reasonable timings.

Keep all of the above when you fix the other findings.

## Operational Notes

- seerr talks to Sonarr / Radarr / Plex via their APIs. Internal
  hostnames: `http://sonarr:8989`, `http://radarr:7878`,
  `http://plex:32400`.
- Request approval / denial emits notifications — webhooks to Discord /
  Telegram work from inside the Docker network just fine.
- First-run setup: creates the admin from Plex OAuth. If Plex can't reach
  `seerr:5055` over the Docker network, setup hangs — verify with
  `docker exec seerr wget -qO- http://plex:32400/identity`.
