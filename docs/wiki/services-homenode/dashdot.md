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
sources: ["/volume1/docker/config/dashdot/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# dashdot (HomeNode)

Lightweight system dashboard for HomeNode. Separate instance from the CloudNode
dashdot (which lives at [services/dashdot](../services/dashdot.md)).

- **Image**: `mauricenino/dashdot:latest` ⚠️
- **Compose file**: `/volume1/docker/config/dashdot/docker-compose.yml`
- **Tracked copy**: **not tracked** (finding NM1)
- **Port (internal)**: `3001`
- **Router**: `dash.example.com` ⚠️ **conflict** — CloudNode dashdot also uses
  this hostname. Only one will resolve depending on which Traefik answers.
  See Operational Notes below.
- **Privileged**: `true` ⚠️
- **Volume**: `/volume1/docker/config/dashdot:/mnt/host:ro` ⚠️ **wrong mount**

## Upstream Sources

- Docs: <https://getdashdot.com/docs/installation/docker-compose>
- Repo: <https://github.com/MauriceNino/dashdot>

Upstream's reference compose:

```yaml
services:
  dash:
    image: mauricenino/dashdot
    restart: unless-stopped
    privileged: true
    ports: ["3001:3001"]
    volumes:
      - /:/mnt/host:ro   # <-- full host root
```

## Our Compose

```yaml
services:
  dash:
    image: mauricenino/dashdot:latest
    container_name: dash
    restart: unless-stopped
    privileged: true
    volumes:
      - /volume1/docker/config/dashdot:/mnt/host:ro   # <-- NOT host root
    networks: [traefik_traefik]
    labels:
      - "traefik.http.routers.dash.rule=Host(`dash.example.com`)"
      - "traefik.http.services.dash.loadbalancer.server.port=3001"
```

## Deviations / Findings

### F-N-DASHDOT-1 — `/mnt/host` bound to config dir, not host root (`high` / NH3)
This is the big one. Dashdot reads CPU/RAM/disk/network via the `/mnt/host`
path. By binding it to `/volume1/docker/config/dashdot` (its own config
directory, which is ~empty), the dashboard reports nonsense:

- Disk widget: shows the tiny partition holding `/volume1/docker/config/dashdot`, not your main storage volume.
- OS widget: may crash or show "unknown" because `/mnt/host/etc/os-release` doesn't exist at that path.
- Filesystem widget: missing.

Compare CloudNode dashdot which correctly mounts `- /:/mnt/host:ro`.

Fix:

```yaml
    volumes:
      - /:/mnt/host:ro
```

Note on Synology: the root filesystem on DSM is `/` but `/volume1` is a
separate BTRFS volume. Dashdot will show `/` (DSM's root partition,
usually small, ~6GB). For the *real* big volume:

```yaml
    volumes:
      - /:/mnt/host:ro
    environment:
      - DASHDOT_FS_DEVICE_FILTER=/volume1
      - DASHDOT_FS_VIRTUAL_MOUNTS=/volume1:/volume1
```

See <https://getdashdot.com/docs/customizations/widgets#filesystem-widget>
for filter syntax.

### F-N-DASHDOT-2 — `privileged: true` (`medium`)
CloudNode dashdot uses the safer `group_add: [docker-gid]` pattern. HomeNode uses
`privileged: true` which gives the container ~root on the host. Dashdot
doesn't actually need privileged mode if `/:/mnt/host:ro` is supplied —
the read-only mount gives it everything it reads.

Fix: drop `privileged: true` and test. On DSM the docker GID is usually
`65536` or similar; find it with `getent group docker`. If removing
privileged breaks a specific widget, `cap_add: [SYS_PTRACE]` may be the
narrower fix.

### F-N-DASHDOT-3 — `:latest` image (`medium` / NM2)
Pin a release.

### F-N-DASHDOT-4 — not tracked in repo (`high` / NM1)

## Remediation

### Full fix (combined)

```yaml
services:
  dash:
    image: mauricenino/dashdot:5.x   # pin from github.com/MauriceNino/dashdot/releases
    container_name: dash
    restart: unless-stopped
    # privileged: true   <-- remove
    group_add:
      - "65536"   # replace with actual docker group on DSM
    environment:
      - DASHDOT_FS_DEVICE_FILTER=/volume1
    volumes:
      - /:/mnt/host:ro
    networks: [traefik_traefik]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dash.rule=Host(`dash.example.com`)"
      - "traefik.http.routers.dash.entrypoints=websecure"
      - "traefik.http.routers.dash.tls.certresolver=cloudflare"
      - "traefik.http.services.dash.loadbalancer.server.port=3001"
```

Validation steps after applying:

1. `docker exec dash ls /mnt/host/etc/os-release` — should succeed.
2. Hit `https://dash.example.com` → OS widget shows Synology DSM /
   Debian-derivative info.
3. Filesystem widget shows `/volume1` with the correct TB capacity.

### If privileged removal breaks a widget

- CPU frequency widget needs `SYS_RAWIO` or `SYS_PTRACE`. Add:
  ```yaml
      cap_add: [SYS_PTRACE]
  ```
- Network widget usually works without extra caps once `/:/mnt/host:ro`
  is in place.

## Operational Notes

- `dash.example.com` is claimed by **both** CloudNode dashdot (router name
  `dashdot`, see `stacks/observability/docker-compose.yml`) and HomeNode
  dashdot (router name `dash`). This is a hostname collision — whichever
  Traefik answers first wins.
- The HomeNode dashdot should use a separate hostname such as
  `dash-nas.example.com` to avoid overlap with the CloudNode router.
