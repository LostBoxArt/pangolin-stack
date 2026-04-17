---
title: "dashdot"
slug: cloudnode-dashdot
type: service
status: active
tags: ["homelab", "cloudnode", "service", "dashdot"]
aliases: ["dashdot"]
entities:
  primary: cloudnode-dashdot
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/observability/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# dashdot

Lightweight CloudNode system dashboard (CPU, RAM, storage, network). Runs behind
Traefik at `dash.example.com`.

- **Image**: `mauricenino/dashdot:latest` ⚠️
- **Compose file**: `stacks/observability/docker-compose.yml`
- **Port**: `3001` (internal) → Traefik
- **Host mount**: `/:/mnt/host:ro` (for disk metrics)

## Upstream Sources

- Install docs: <https://getdashdot.com/docs/installation/docker-compose>
- Repo: <https://github.com/mauricenino/dashdot>
- Config docs: <https://getdashdot.com/docs/configuration>

## Upstream Reference Compose

```yaml
services:
  dash:
    image: mauricenino/dashdot:latest
    restart: unless-stopped
    privileged: true
    ports:
      - '80:3001'
    volumes:
      - /:/mnt/host:ro
```

Upstream *recommends* `privileged: true`. We explicitly avoid this and use
`group_add: "986"` instead — see finding F-DASHDOT-1.

## Our Compose (relevant slice)

```59:79:stacks/observability/docker-compose.yml
  dashdot:
    image: mauricenino/dashdot:latest
    container_name: dashdot
    networks:
      - pangolin
    restart: unless-stopped
    ports:
      - 3001:3001
    group_add:
      - "986"  # docker group
    environment:
      - DASHDOT_WIDGET_LIST=os,cpu,storage,ram,network
    volumes:
      - /:/mnt/host:ro
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dashdot.rule=Host(`dash.example.com`)"
      - "traefik.http.routers.dashdot.entrypoints=websecure"
      - "traefik.http.routers.dashdot.tls.certresolver=letsencrypt"
      - "traefik.http.routers.dashdot.middlewares=geoblock@file,security-headers@file"
      - "traefik.http.services.dashdot.loadbalancer.server.port=3001"
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| `privileged: true` | yes | **no**, replaced by `group_add: 986` | ✓ intentional hardening |
| `:latest` tag | recommended | same | drift risk |
| `DASHDOT_WIDGET_LIST` | default (all) | explicit subset | intentional |
| Port publish | `80:3001` | `3001:3001` | intentional — Traefik fronts it |

## Findings

### F-DASHDOT-1 — we're better than upstream on privilege (`low` / L5)
Documented here so future agents don't "helpfully" add `privileged: true`
back. `group_add: "986"` gives dashdot the host's `docker` group GID — which
is all it actually needs for disk I/O stats via the `/mnt/host` bind mount.

**Do not** set `privileged: true` unless dashdot grows a feature that
genuinely needs it (GPU temps via nvidia-smi is one such case, in which
case use the `:nvidia` image tag and `deploy.resources.reservations.devices`
rather than going fully privileged).

### F-DASHDOT-2 — `:latest` tag (`medium` / M10 scope)
Dashdot's release cadence is slower than Traefik's but the image has had
behavioral regressions (e.g. widget name renames). Pin to a release from
<https://github.com/MauriceNino/dashdot/releases>.

## Remediation

### Fix F-DASHDOT-2

```yaml
    image: mauricenino/dashdot:5.8.1   # or current tagged release
```

### Optional: add healthcheck

Upstream does not ship one, but the Node server serves a tiny static page on
`/` — an HTTP probe is trivial:

```yaml
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:3001"]
      interval: 1m
      timeout: 5s
      retries: 3
      start_period: 30s
```

## Operational Notes

- Widgets can be reordered by changing `DASHDOT_WIDGET_LIST` order.
- Storage widget can show multiple partitions if you add the `filesystems`
  filter via `DASHDOT_FS_DEVICE_FILTER`.
- If disk I/O metrics show `--`, the `group_add: 986` GID is wrong for this
  host — check `getent group docker` and update the number.
