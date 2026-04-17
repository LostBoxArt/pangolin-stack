---
title: "traefik"
slug: vps-traefik
type: service
status: active
tags: ["homelab", "vps", "service", "traefik"]
aliases: ["traefik"]
entities:
  primary: vps-traefik
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/core/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# traefik

Edge reverse-proxy and TLS terminator for everything exposed behind
`*.dennisb.xyz`. Shares Gerbil's network namespace.

- **Image**: `traefik:latest` ⚠️ (upstream pins `v3.6`)
- **Compose file**: `stacks/core/docker-compose.yml`
- **Network mode**: `service:gerbil` — all ports appear on the gerbil container
- **Config**:
  - Static: `config/traefik/traefik_config.yml`
  - Dynamic rules: `config/traefik/rules/`
  - ACME/LE certs: `config/letsencrypt/acme.json`
  - Access logs: `config/traefik/logs/access.log` (JSON)
- **Docker socket**: mounted read-write (needed for Docker provider
  label discovery)

## Upstream Sources

- Reference compose: <https://raw.githubusercontent.com/fosrl/pangolin/main/install/config/docker-compose.yml>
- Traefik docs: <https://doc.traefik.io/traefik/>

## Upstream Reference Compose

```yaml
traefik:
  image: docker.io/traefik:v3.6
  container_name: traefik
  restart: unless-stopped
  network_mode: service:gerbil
  depends_on:
    pangolin:
      condition: service_healthy
  command:
    - --configFile=/etc/traefik/traefik_config.yml
  volumes:
    - ./config/traefik:/etc/traefik:ro
    - ./config/letsencrypt:/letsencrypt
    - ./config/traefik/logs:/var/log/traefik
```

## Our Compose (relevant slice)

```56:74:stacks/core/docker-compose.yml
  traefik:
    command:
      - --configFile=/etc/traefik/traefik_config.yml
    container_name: traefik
    labels:
      - wud.watch=false
    depends_on:
      pangolin:
        condition: service_healthy
    image: traefik:latest
    network_mode: service:gerbil
    restart: unless-stopped
    volumes:
      - ../../config/traefik:/etc/traefik:ro
      - ../../config/letsencrypt:/letsencrypt
      - ../../config/traefik/logs:/var/log/traefik
      - ../../config/traefik/rules:/rules
      - /var/run/docker.sock:/var/run/docker.sock
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Image tag | `traefik:v3.6` | `traefik:latest` | ⚠️ unintentional drift |
| `rules/` bind | not in upstream | `../../config/traefik/rules:/rules` | intentional — we split dynamic rules |
| Docker socket | not in upstream | mounted | intentional — Docker provider labels |
| `wud.watch=false` label | n/a | present | tells `whatsupdocker`-style watchers to skip this image (we still pin manually) |

## Findings

### F-TRAEFIK-1 — `:latest` tag (`high` / H1)
Traefik minors are not always backward-compatible with middleware syntax.
If an unattended `docker compose pull` on `core` grabs a Traefik 4.x with
breaking changes, the proxy will fail to start and take down all public
routes including Pangolin itself (which you need to log in and fix).

The Badger plugin is already pinned in `traefik_config.yml` to
`v1.4.0` — the image should match that pin discipline.

### F-TRAEFIK-2 — docker.sock mounted read-write
Traefik needs to *read* Docker events; it does not write. Some deployments
use a socket proxy (e.g. `tecnativa/docker-socket-proxy`) that exposes only
the read-only endpoints. Not flagged in this review because Gerbil namespace
sharing already means Traefik sees the host network stack, but worth
tracking as a future hardening step.

## Remediation

### Fix F-TRAEFIK-1 — pin the image

```yaml
    image: traefik:v3.6
```

Then commit, then `./stackctl.sh pull core` to verify the right digest is
fetched, then `./stackctl.sh restart core` — remembering that **Traefik must
be recreated whenever Gerbil is recreated** (see [gerbil](./gerbil.md)).

### Future hardening (F-TRAEFIK-2, not urgent)

Swap `/var/run/docker.sock:/var/run/docker.sock` for a socket-proxy service
on the `pangolin` network and point Traefik's Docker provider at
`tcp://docker-socket-proxy:2375`.

## Operational Notes

- Traefik's container has **no own network** — `docker network inspect pangolin`
  will NOT show traefik. It is attached to gerbil's namespace.
- Logs: `config/traefik/logs/access.log` (JSON format, consumed by
  CrowdSec and the traefik-log-dashboard agent).
- Badger plugin pin is in `config/traefik/traefik_config.yml` under
  `experimental.plugins`.
