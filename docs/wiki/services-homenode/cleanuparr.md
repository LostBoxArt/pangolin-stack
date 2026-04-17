---
title: "cleanuparr"
slug: homenode-cleanuparr
type: service
status: active
tags: ["homelab", "homenode", "service", "cleanuparr"]
aliases: ["cleanuparr"]
entities:
  primary: homenode-cleanuparr
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/cleanuparr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# cleanuparr

Automated cleanup for qBit / Sonarr / Radarr — removes failed / stalled /
redundant downloads so they stop taking up disk and swarm slots.

- **Image**: `ghcr.io/cleanuparr/cleanuparr:latest` ⚠️
- **Compose file**: `/volume1/docker/config/cleanuparr/docker-compose.yml`
- **Tracked copy**: **not tracked** (finding NM1)
- **Port (internal)**: `11011`
- **Router**: `cleanuparr.example.com`
- **Volume**: `/volume1/docker/config/cleanuparr:/config`

## Upstream Sources

- Project: <https://github.com/Cleanuparr/Cleanuparr>
- Image: <https://github.com/Cleanuparr/Cleanuparr/pkgs/container/cleanuparr>

## Our Compose

```yaml
services:
  cleanuparr:
    image: ghcr.io/cleanuparr/cleanuparr:latest
    container_name: cleanuparr
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Jerusalem
    volumes:
      - /volume1/docker/config/cleanuparr:/config
    networks: [traefik_traefik]
    labels:
      - "traefik.http.routers.cleanuparr.rule=Host(`cleanuparr.example.com`)"
      - "traefik.http.services.cleanuparr.loadbalancer.server.port=11011"
```

## Findings

### F-N-CLEANUPARR-1 — `:latest` image (`medium` / NM2)
Pin a release. Cleanuparr is relatively young and active; its config
schema has changed between releases.

### F-N-CLEANUPARR-2 — no healthcheck (`medium` / NM4)
Web UI on 11011 responds to HTTP; add a simple probe:

```yaml
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:11011/ >/dev/null || exit 1"]
      interval: 1m
      timeout: 10s
      retries: 3
      start_period: 30s
```

### F-N-CLEANUPARR-3 — not tracked in repo (`high` / NM1)

## Remediation

### Fix F-N-CLEANUPARR-1

```yaml
    image: ghcr.io/cleanuparr/cleanuparr:vX.Y
```

## Operational Notes

- Cleanuparr connects to qBit + Sonarr + Radarr via their APIs; configure
  in the UI under "Applications". Use in-network hostnames
  (`http://qbittorrent:8080`, etc.).
- **Dangerous rules** to understand before enabling:
  - *Remove stalled downloads* can nuke torrents that are "stalled" simply
    because their tracker is slow.
  - *Remove failed imports* will delete files that Sonarr/Radarr couldn't
    classify — double-check the grab history if a missing episode shows up.
- All Cleanuparr actions are logged to `/config/logs/`; review after the
  first week.
