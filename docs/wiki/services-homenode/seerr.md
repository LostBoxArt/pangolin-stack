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
sources: ["/volume1/docker/config/seerr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# seerr

Media request front-end for end users — they ask for a movie / show, it
hands the request to Sonarr / Radarr for fulfilment.

- **Image**: `ghcr.io/seerr-team/seerr:latest` ⚠️ (**unofficial fork**)
- **Compose file**: `/volume1/docker/config/seerr/docker-compose.yml`
- **Tracked copy**: **not tracked** (finding NM1)
- **Port (internal)**: `5055`
- **Router**: `request.example.com`
- **Volume**: `/volume1/docker/config/jellyseerr:/app/config` ⚠️ legacy dir

## Upstream Sources

- This fork: <https://github.com/seerr-team/seerr>
- Original Jellyseerr: <https://github.com/fallenbagel/jellyseerr>
- Ancestor Overseerr: <https://github.com/sct/overseerr>

## Our Compose

```yaml
services:
  seerr:
    image: ghcr.io/seerr-team/seerr:latest
    container_name: seerr
    init: true
    restart: unless-stopped
    security_opt: ["no-new-privileges:true"]
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
      traefik_traefik:
#        ipv4_address: 172.18.0.11
    labels:
      - "traefik.http.routers.seerr.rule=Host(`request.example.com`)"
      - "traefik.http.services.seerr.loadbalancer.server.port=5055"
```

## Deviations / Findings

### F-N-SEERR-1 — unofficial fork (`high` / NH6)
`seerr-team/seerr` is a community fork of Jellyseerr. Before the next
upgrade cycle:

- Check if the fork is still maintained (look at commit cadence on
  <https://github.com/seerr-team/seerr>).
- Check if upstream Jellyseerr has merged whatever features pushed us to
  fork.
- If upstream has caught up, switch back to
  `fallenbagel/jellyseerr:latest` (just change the image and restart —
  the data dir is already named `jellyseerr`).

### F-N-SEERR-2 — data volume is `jellyseerr/` (`medium` / NM5)
`/volume1/docker/config/jellyseerr:/app/config` — the directory name
does NOT match the service name. A naïve backup script keyed on service
name, or a "remove unused dirs" sweep, will miss or destroy seerr's data.

Don't rename blindly — seerr writes an absolute-path-referencing SQLite
DB. Safe rename:

1. Stop seerr.
2. `mv /volume1/docker/config/jellyseerr /volume1/docker/config/seerr`.
3. Update the bind-mount in compose to
   `/volume1/docker/config/seerr:/app/config`.
4. `docker compose up -d` and smoke-test.
5. Keep the old path symlinked for a release cycle:
   `ln -s /volume1/docker/config/seerr /volume1/docker/config/jellyseerr`.

### F-N-SEERR-3 — commented IPAM with no IPAM block (`medium` / NM11)
`#ipv4_address: 172.18.0.11` is dangling — there's no `ipam.config`
definition for `traefik_traefik` in this compose, so even uncommenting it
would do nothing useful. Delete the line.

### F-N-SEERR-4 — `:latest` image (`medium` / NM2)
As with every other HomeNode service. Pin after confirming F-N-SEERR-1.

### F-N-SEERR-5 — `LOG_LEVEL=debug` in steady state (`low`)
Debug logging is fine when diagnosing, but leaves it in production
generates a lot of noise and bloats the `/app/config/logs/` directory.
Drop to `info` once the fork is stable in your environment.

## Remediation

### Fix F-N-SEERR-1 (if upstream caught up)

```yaml
    image: fallenbagel/jellyseerr:latest
    volumes:
      - /volume1/docker/config/seerr:/app/config    # after rename
```

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
