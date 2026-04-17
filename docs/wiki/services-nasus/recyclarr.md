---
title: "recyclarr"
slug: nasus-recyclarr
type: service
status: active
tags: ["homelab", "nasus", "service", "recyclarr"]
aliases: ["recyclarr"]
entities:
  primary: nasus-recyclarr
  mentions: []
related: ["./README.md", "./nasus-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/recyclarr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# recyclarr

CLI + cron job that applies TRaSH-Guides recommended quality profiles and
custom formats to Sonarr / Radarr. Runs on a schedule, not a long-lived
server.

- **Image**: `ghcr.io/recyclarr/recyclarr:latest` ⚠️
- **Compose file**: `/volume1/docker/config/recyclarr/docker-compose.yml`
- **Tracked copy**: **not tracked** (finding NM1)
- **Runtime**: cron `@daily` inside the container
- **User**: `1000:1000`
- **Volume**: `/volume1/docker/config/recyclarr:/config`
- **Network**: `traefik_traefik`

## Upstream Sources

- Docs: <https://recyclarr.dev/wiki/>
- YAML reference: <https://recyclarr.dev/wiki/yaml/config-reference/>
- Image: <https://github.com/recyclarr/recyclarr/pkgs/container/recyclarr>

## Our Compose

```yaml
services:
  recyclarr:
    image: ghcr.io/recyclarr/recyclarr:latest
    container_name: recyclarr
    user: 1000:1000
    restart: unless-stopped
    networks: [traefik_traefik]
    volumes:
      - /volume1/docker/config/recyclarr:/config
    environment:
      - TZ=Asia/Jerusalem
      - CRON_SCHEDULE=@daily
      - RECYCLARR_CREATE_CONFIG=true
```

## Deviations / Findings

### F-N-RECYCLARR-1 — `:latest` image (`medium` / NM2)
Pin a release from
<https://github.com/recyclarr/recyclarr/pkgs/container/recyclarr>. Recyclarr
is generally well-behaved across minors, but config-schema deprecations
happen and `:latest` can surprise you on a daily run.

### F-N-RECYCLARR-2 — no healthcheck (`low`)
Recyclarr's container is a sleep-wait-sync loop; there's no HTTP endpoint.
A healthcheck based on `ps aux | grep recyclarr` is low-value. Skip.

### F-N-RECYCLARR-3 — compose file missing trailing newline (`low` / NM13)
The on-NASUS file ends `external: true===END===` — no final `\n`. Fix next
time you touch it. No functional impact.

### F-N-RECYCLARR-4 — not tracked in repo (`high` / NM1)

## Remediation

### Fix F-N-RECYCLARR-1

```yaml
    image: ghcr.io/recyclarr/recyclarr:7.x.x
```

## Overlap with Profilarr

See [profilarr](./profilarr.md) under **Overlap with Recyclarr** for the
"pick one per custom format" rule.

## Operational Notes

- Configuration lives in `/config/recyclarr.yml` — this is where you list
  the TRaSH guide profiles you want imported and what Sonarr/Radarr instance
  to target.
- First-run: `RECYCLARR_CREATE_CONFIG=true` auto-generates a starter config
  if `/config/recyclarr.yml` is missing. Safe to leave enabled.
- To run a sync on demand (outside cron):
  `docker exec recyclarr recyclarr sync`.
- Logs: `/config/logs/` inside the container, rotated automatically.
