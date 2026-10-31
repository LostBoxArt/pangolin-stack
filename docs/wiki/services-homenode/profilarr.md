---
title: "profilarr"
slug: homenode-profilarr
type: service
status: active
tags: ["homelab", "homenode", "service", "profilarr"]
aliases: ["profilarr"]
entities:
  primary: homenode-profilarr
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/profilarr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# profilarr

Quality-profile manager for Sonarr / Radarr — keeps custom formats, quality
definitions, and naming schemes in sync across the *arr apps from a central
spec.

- **Image**: `ghcr.io/dictionarry-hub/profilarr:2.3.1` (maintained fork)
- **Compose file**: `/volume1/docker/config/profilarr/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/profilarr/docker-compose.yml` (sanitized live snapshot, 2026-10-31)
- **Port (internal)**: `6868`
- **Router**: `profilarr.example.com`
- **Volume**: `/volume1/docker/config/profilarr:/config`

## Upstream Sources

- **Upstream project**: <https://github.com/Dictionarry-Hub/Profilarr>
- **Image**: <https://ghcr.io/dictionarry-hub/profilarr>

## Our Compose

```yaml
services:
  profilarr:
    image: ghcr.io/dictionarry-hub/profilarr:2.3.1
    container_name: profilarr
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000
      - UMASK=022
      - TZ=Asia/Jerusalem
    volumes:
      - /volume1/docker/config/profilarr:/config
    networks: [traefik_traefik]
    labels:
      - "traefik.http.routers.profilarr.rule=Host(`profilarr.example.com`)"
      - "traefik.http.services.profilarr.loadbalancer.server.port=6868"
```

## Findings

### F-N-PROFILARR-1 — prior image vulnerability and maintained fork migration (resolved 2026-10-31)
The old `santiagosayshey/profilarr` build was in the affected range for
[GHSA-xhjf-xjhw-69mh](https://github.com/advisories/GHSA-xhjf-xjhw-69mh):
`>=2.0.0, <2.3.0`. A SQLite `ATTACH` issue could let a linked database read
the application database, including API keys. Deployment moved to the maintained
`ghcr.io/dictionarry-hub/profilarr:2.3.1` fork after backups.

### F-N-PROFILARR-2 — no healthcheck (`medium` / NM4)
Profilarr serves a web UI on 6868. Simple probe:

```yaml
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:6868/ >/dev/null || exit 1"]
      interval: 1m
      timeout: 10s
      retries: 3
      start_period: 30s
```

### F-N-PROFILARR-3 — source tracking (resolved 2026-10-27)
The page now documents the maintained `ghcr.io/dictionarry-hub/profilarr:2.3.1` fork and the GHSA remediation. The absence of a native healthcheck remains unchanged.

## Remediation

### Fix F-N-PROFILARR-1

```yaml
    image: ghcr.io/dictionarry-hub/profilarr:2.3.1
```

## Overlap with Recyclarr

Profilarr and [recyclarr](./recyclarr.md) solve overlapping problems.
Both can push quality profiles / custom formats into Sonarr + Radarr.

Rough split that's worked in the wild:

- **Profilarr**: UI-driven, nicer for one-off tweaking + ad-hoc imports
  from a community catalog.
- **Recyclarr**: YAML-first, CI-friendly, cron-based sync from the
  [TRaSH Guides](https://trash-guides.info/).

Running both is fine **if** they target different formats. Running both
on the same custom format is a recipe for infinite ping-pong updates
(they'll keep overwriting each other on every cycle). Pick one
per custom format.

## Operational Notes

- Profilarr connects to Sonarr / Radarr via their API keys + the
  network-internal hostnames (`http://sonarr:8989`, `http://radarr:7878`).
- `/config` contains the profile DB and any saved presets.
- **Back up `/volume1/docker/config/profilarr` before pulling a new
  image** — schema migrations are silent and not always reversible.
