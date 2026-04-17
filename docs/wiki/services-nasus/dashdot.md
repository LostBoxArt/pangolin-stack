---
title: "dashdot (NASUS)"
slug: nasus-dashdot
type: service
status: active
tags: ["homelab", "nasus", "service", "dashdot"]
aliases: ["dashdot (NASUS)", "dashdot"]
entities:
  primary: nasus-dashdot
  mentions: []
related: ["./README.md", "./nasus-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/dashdot/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# dashdot (NASUS)

Lightweight system dashboard for NASUS. Separate instance from the VPS
dashdot (which lives at [services/dashdot](../services/dashdot.md)).

- **Image**: `mauricenino/dashdot:latest` ⚠️
- **Compose file**: `/volume1/docker/config/dashdot/docker-compose.yml`
- **Tracked copy**: **not tracked** (finding NM1)
- **Port (internal)**: `3001`
- **Router**: `dash.dennisb.xyz`
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
      - "traefik.http.routers.dash.rule=Host(`dash.dennisb.xyz`)"
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

Compare VPS dashdot which correctly mounts `- /:/mnt/host:ro`.

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
VPS dashdot uses the safer `group_add: [docker-gid]` pattern. NASUS uses
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
      - "traefik.http.routers.dash.rule=Host(`dash.dennisb.xyz`)"
      - "traefik.http.routers.dash.entrypoints=websecure"
      - "traefik.http.routers.dash.tls.certresolver=cloudflare"
      - "traefik.http.services.dash.loadbalancer.server.port=3001"
```

Validation steps after applying:

1. `docker exec dash ls /mnt/host/etc/os-release` — should succeed.
2. Hit `https://dash.dennisb.xyz` → OS widget shows Synology DSM /
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

- Two dashdots now: `dash.dennisb.xyz` is NASUS and is currently broken
  per F-N-DASHDOT-1. VPS dashdot is at `dashdot.dennisb.xyz` (or similar,
  per VPS compose).
- If you really just want a NASUS dashboard and VPS dashboard to be
  differentiated, consider naming the router `dash-nas.dennisb.xyz` to
  avoid confusion with VPS `dash.dennisb.xyz`.
