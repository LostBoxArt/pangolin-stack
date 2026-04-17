---
title: "gerbil"
slug: cloudnode-gerbil
type: service
status: active
tags: ["homelab", "cloudnode", "service", "gerbil"]
aliases: ["gerbil"]
entities:
  primary: cloudnode-gerbil
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/core/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# gerbil

Fossorial Gerbil — WireGuard relay between the CloudNode and remote sites. Also
owns the public HTTP/HTTPS ports (80/443); Traefik shares its network
namespace via `network_mode: service:gerbil`.

- **Image**: `fosrl/gerbil:1.3.1`
- **Compose file**: `stacks/core/docker-compose.yml`
- **Public ports**: `51820/udp` (WireGuard), `21820/udp` (Newt/Olm
  control-plane), `80/tcp`, `443/tcp`, `853/tcp` (DoT, forwarded to AdGuard)
- **Caps**: `NET_ADMIN`, `SYS_MODULE`
- **Config**: `./config/` bound at `/var/config` (key saved here)

## Upstream Sources

- Reference compose: <https://raw.githubusercontent.com/fosrl/pangolin/main/install/config/docker-compose.yml>
- Releases: <https://github.com/fosrl/gerbil/releases>

## Upstream Reference Compose

```yaml
gerbil:
  image: docker.io/fosrl/gerbil:{{.GerbilVersion}}
  container_name: gerbil
  restart: unless-stopped
  depends_on:
    pangolin:
      condition: service_healthy
  command:
    - --reachableAt=http://gerbil:3004
    - --generateAndSaveKeyTo=/var/config/key
    - --remoteConfig=http://pangolin:3001/api/v1/
  volumes:
    - ./config/:/var/config
  cap_add:
    - NET_ADMIN
    - SYS_MODULE
  ports:
    - 51820:51820/udp
    - 21820:21820/udp
    - 443:443
    - 443:443/udp   # HTTP/3 QUIC
    - 80:80
```

## Our Compose (relevant slice)

```30:54:stacks/core/docker-compose.yml
  gerbil:
    cap_add:
      - NET_ADMIN
      - SYS_MODULE
    networks:
      - pangolin
    command:
      - --reachableAt=http://gerbil:3003
      - --generateAndSaveKeyTo=/var/config/key
      - --remoteConfig=http://pangolin:3001/api/v1/gerbil/get-config
      - --reportBandwidthTo=http://pangolin:3001/api/v1/gerbil/receive-bandwidth
    container_name: gerbil
    depends_on:
      pangolin:
        condition: service_healthy
    image: fosrl/gerbil:1.3.1
    ports:
      - 51820:51820/udp
      - 21820:21820/udp
      - 443:443
      - 80:80
      - 853:853
    restart: unless-stopped
    volumes:
      - ../../config/:/var/config
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Version | templated | pinned `1.3.1` | aligned with Pangolin 1.17.x — ✓ |
| `reachableAt` port | `3004` | `3003` | **matches gerbil 1.3.1** — newer gerbil moved to 3004; don't "fix" this without a version bump |
| `remoteConfig` endpoint | `/api/v1/` | `/api/v1/gerbil/get-config` + explicit `--reportBandwidthTo` | pangolin 1.17 unified endpoints in newer builds; 1.3.1 still expects the split endpoints — ✓ |
| `443/udp` (HTTP/3) | exposed | **not exposed** | unintentional drift |
| `853/tcp` | not exposed | exposed for AdGuard DoT | intentional custom route — documented in AGENTS.md |
| Healthcheck | none | none | matches upstream |

## Findings

### F-GERBIL-1 — HTTP/3 (QUIC) port missing (`medium` / M2)
Upstream exposes `443:443/udp`. Without it, Traefik cannot negotiate HTTP/3
with clients, even if `traefik_config.yml` enables QUIC. Silent
degradation — no visible error, just "mysteriously slower" TLS handshakes on
mobile.

### F-GERBIL-2 — no healthcheck (`low` / L2)
Upstream also omits it, but Gerbil exposes `/status` on its HTTP endpoint.
Adding a healthcheck would let `stackctl.sh status` show a clearer signal
and let Traefik's `depends_on` wait for Gerbil to actually be serving.

## Remediation

### Fix F-GERBIL-1

Add `443:443/udp` to the `ports:` list:

```yaml
    ports:
      - 51820:51820/udp
      - 21820:21820/udp
      - 443:443
      - 443:443/udp
      - 80:80
      - 853:853
```

### Fix F-GERBIL-2 (optional)

```yaml
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:3003/status"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s
```

(Confirm the status path against gerbil 1.3.1 source before merging.)

## Operational Notes

- **Gerbil owns the namespace**. If you recreate gerbil, you *must* also
  recreate Traefik: `docker compose -f stacks/core/docker-compose.yml --env-file .env up -d --force-recreate traefik`. Otherwise Traefik keeps
  referencing the old network namespace and 80/443 go dark.
- **Key file** at `config/key` is the gerbil identity; do NOT delete without
  reprovisioning all connected sites.
