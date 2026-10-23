---
title: "traefik"
slug: cloudnode-traefik
type: service
status: active
tags: ["homelab", "cloudnode", "service", "traefik"]
aliases: ["traefik"]
entities:
  primary: cloudnode-traefik
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/core/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-23
last_lint: 2026-10-23
---
# traefik

Edge reverse-proxy and TLS terminator for everything exposed behind
`*.example.com`. Shares Gerbil's network namespace.

- **Image**: `traefik:v3.7.16` (pinned to the verified running release)
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
    image: traefik:v3.7.16
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
| Image tag | `traefik:v3.6` | `traefik:v3.7.16` | pinned to the verified running release — ✓ |
| `rules/` bind | not in upstream | `../../config/traefik/rules:/rules` | intentional — we split dynamic rules |
| Docker socket | not in upstream | mounted | intentional — Docker provider labels |
| `wud.watch=false` label | n/a | present | WUD-specific opt-out metadata; does not prove WUD is installed or prevent other Compose/Dockhand pulls |

## Findings

### F-TRAEFIK-1 — `:latest` tag (`high` / H1, resolved 2026-09-28)
Traefik minors are not always backward-compatible with middleware syntax.
If an unattended `docker compose pull` on `core` grabs a Traefik 4.x with
breaking changes, the proxy will fail to start and take down all public
routes including Pangolin itself (which you need to log in and fix).

The image is now pinned to `v3.7.16`, matching the verified running image
digest. The Badger plugin remains pinned to `v1.7.0`.

### F-TRAEFIK-3 — placeholder `*.example.com` labels burning Let's Encrypt quota (`high` / resolved 2026-09-28)
Several service compose files carried leftover Traefik router labels still
pointing at placeholder hostnames (`example.com`, `home.example.com`,
`dockhand.example.com`, `dash.example.com`,
`auth.example.com`). Pangolin generates its own routers for those services via
the `@http` provider, so the labels were redundant — but Traefik still tried to
issue a certificate for every one of them, on every start. Let's Encrypt
rejects them outright:

```
unable to generate a certificate for the domains [home.example.com]:
urn:ietf:params:acme:error:rejectedIdentifier :: Cannot issue for
"home.example.com": The ACME server refuses to issue a certificate for this
domain name, because it is forbidden by policy
```

Measured rate: **45 failed ACME orders per day** (`rejectedIdentifier` count in
`config/traefik/logs/traefik.log` before the fix; zero after). That burns the
per-account failed-validation budget that the 25 real hostnames need, so a
transient hiccup on a legitimate renewal could start hard-failing.

Fixed by deleting the six label blocks. After the change Traefik reports zero
`example.com` routers and no further rejected orders.

**Rule:** never leave Traefik router labels pointing at hostnames that are not
real, and never point two providers at the same FQDN. Either Pangolin owns a
route or a docker label does — not both.

### F-TRAEFIK-4 — CrowdSec trusted forwarded headers were wide open (`medium` / resolved 2026-09-28)
`config/traefik/rules/dynamic_config.yml` had
`ForwardedHeadersTrustedIPs: [0.0.0.0/0]`, meaning every client was trusted to
supply `X-Forwarded-For`. Traefik is directly exposed, not behind a proxy that
strips client headers, so anyone could have chosen which IP CrowdSec evaluates
and bans. Narrowed to loopback, the private ranges, `100.89.137.0/20`, and the
exact Cloudflare edge CIDRs (only the apex is still Cloudflare-proxied; every
other host is grey-cloud and hits the origin directly).

### F-TRAEFIK-2 — docker.sock mounted read-write
Traefik needs to *read* Docker events; it does not write. Some deployments
use a socket proxy (e.g. `tecnativa/docker-socket-proxy`) that exposes only
the read-only endpoints. Not flagged in this review because Gerbil namespace
sharing already means Traefik sees the host network stack, but worth
tracking as a future hardening step.

## Remediation

### Fix F-TRAEFIK-1 — pin the image (completed 2026-09-28)

```yaml
    image: traefik:v3.7.16
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
- Pangolin release notes say `3.6+` is required for all load-balancing options; deployed `v3.7.16` satisfies the requirement.[1]
- Badger remains pinned at `v1.7.0` because the same release notes report a plugin-integrity failure in `v1.8.0`; see [Badger](./badger.md).

## Sources

1. [Pangolin 1.25.3 release notes](https://github.com/fosrl/pangolin/releases/tag/1.25.3)
