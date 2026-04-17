---
title: "dockhand"
slug: vps-dockhand
type: service
status: active
tags: ["homelab", "vps", "service", "dockhand"]
aliases: ["dockhand"]
entities:
  primary: vps-dockhand
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/management/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# dockhand

Modern replacement for Portainer — container + compose-stack management,
both for the VPS (local docker.sock) and NASUS (remote Hawser agent over
TCP). Fronted at `dockhand.dennisb.xyz`.

- **Image**: `fnsys/dockhand:latest` ⚠️
- **Compose file**: `stacks/management/docker-compose.yml`
- **Internal port**: `3000` (Traefik-fronted)
- **Data**: `./data/dockhand/` → `/app/data`
- **Bind**: `/home/jesus/pangolin-stack/stacks:/home/jesus/pangolin-stack/stacks`
  — needed so Dockhand can read/write compose files for git-based stacks
- **Socket**: `/var/run/docker.sock`
- **Running as**: `user: "0:0"` + `group_add: "986"`

## Upstream Sources

- Reference compose: <https://github.com/Finsys/dockhand/blob/main/docker-compose.yaml>
- Deployment docs: <https://finsys-dockhand.mintlify.app/deployment/docker-compose>
- User manual: <https://dockhand.pro/manual/>

## Upstream Reference Compose

```yaml
services:
  dockhand:
    image: fnsys/dockhand:latest
    container_name: dockhand
    restart: unless-stopped
    ports:
      - 3000:3000
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - dockhand_data:/app/data

volumes:
  dockhand_data:
```

## Our Compose (relevant slice)

```10:36:stacks/management/docker-compose.yml
  dockhand:
    image: fnsys/dockhand:latest
    container_name: dockhand
    networks:
      - pangolin
    restart: unless-stopped
    user: "0:0"
    group_add:
      - "986" # docker group
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ../../data/dockhand:/app/data
      - /home/jesus/pangolin-stack/stacks:/home/jesus/pangolin-stack/stacks
    environment:
      - TZ=UTC
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.dockhand-redirect.rule=Host(`dockhand.dennisb.xyz`)"
      - "traefik.http.routers.dockhand-redirect.entrypoints=web"
      - "traefik.http.routers.dockhand-redirect.middlewares=redirect-to-https@file"
      - "traefik.http.routers.dockhand.rule=Host(`dockhand.dennisb.xyz`)"
      - "traefik.http.routers.dockhand.entrypoints=websecure"
      - "traefik.http.routers.dockhand.tls.certresolver=letsencrypt"
      - "traefik.http.routers.dockhand.middlewares=security-headers@file"
      - "traefik.http.services.dockhand.loadbalancer.server.port=3000"
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Data volume | named `dockhand_data` | bind `../../data/dockhand` | intentional — keeps data in repo tree for backup |
| Stacks bind mount | none | `/home/jesus/pangolin-stack/stacks` | intentional — git stack deploys |
| `user: "0:0"` + `group_add: "986"` | not set | set | documented by Dockhand manual as the fix for socket-permission issues |
| `:latest` tag | upstream default | same | drift risk |
| Port publish | `3000:3000` | not published | ✓ Traefik-fronted |
| `TZ=UTC` | not set | set | consistency |

## Findings

### F-DOCKHAND-1 — `:latest` image tag (`medium` / M6, M10 scope)
Dockhand maintains its own SQLite schema and migrates on startup. A breaking
release shipped as `:latest` could migrate the DB *forward* before we know
about it, making rollback non-trivial.

Dockhand does tag releases (see <https://hub.docker.com/r/fnsys/dockhand/tags>),
and they include a stable `baseline` stream.

### F-DOCKHAND-2 — host-absolute stacks bind (`low`)
The `/home/jesus/pangolin-stack/stacks:/home/jesus/pangolin-stack/stacks`
bind mount uses an absolute host path. If the repo ever moves on disk,
Dockhand's saved git-stack paths will break. Not an urgent fix; just a
gotcha recorded for future agents.

## Remediation

### Fix F-DOCKHAND-1

Pick the latest tagged release from
<https://hub.docker.com/r/fnsys/dockhand/tags>, e.g.:

```yaml
    image: fnsys/dockhand:df2ca0e3-baseline
```

Verify by logging in after restart that the stacks list is intact.

### Optional: future-proof F-DOCKHAND-2

Use a relative path via an env var in `.env` if Dockhand supports
path-translation. Currently the absolute mount is the officially supported
pattern for git-stack deploys.

## Operational Notes (summary; full detail in `AGENTS.md`)

- Public API: `https://dockhand.dennisb.xyz/api/` — but for automation go
  through the container's internal IP on the VPS
  (`docker inspect -f '{{...}}' dockhand`) to skip Pocket-ID.
- Remote host **NASUS** is registered with env `env=2`, host `192.168.0.10`,
  TCP port `2375`, Hawser token in `.env`.
- Git stacks: deploy with `POST /api/git/stacks/{id}/deploy`; headless via
  webhook URL from the UI.
- Activity audit: `GET /api/activity`.
