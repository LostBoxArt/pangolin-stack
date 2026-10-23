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
last_ingested: 2026-10-23
last_lint: 2026-10-23
---
# gerbil

Fossorial Gerbil — WireGuard relay between the CloudNode and remote sites. Also
owns the public HTTP/HTTPS ports (80/443); Traefik shares its network
namespace via `network_mode: service:gerbil`.

- **Image**: `fosrl/gerbil:1.5.2`
- **Compose file**: `stacks/core/docker-compose.yml`
- **Public ports**: `51820/udp` (WireGuard), `21820/udp` (Newt/Olm
  control-plane), `80/tcp`, `443/tcp`
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
    image: fosrl/gerbil:1.5.2
    ports:
      - 51820:51820/udp
      - 21820:21820/udp
      - 443:443
      - 80:80
    restart: unless-stopped
    volumes:
      - ../../config/:/var/config
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Version | templated | pinned `1.5.2` | running with Pangolin `1.25.3` as verified 2026-10-23 — ✓ |
| `reachableAt` port | `3004` | `3003` | **verified still correct on gerbil 1.5.2** — `3003` answers, `3004` refuses; don't "fix" this without re-testing |
| `remoteConfig` endpoint | `/api/v1/` | `/api/v1/gerbil/get-config` + explicit `--reportBandwidthTo` | historical test on Gerbil 1.5.2 / Pangolin 1.24.0 — ✓ |
| `443/udp` (HTTP/3) | exposed | **not exposed** | unintentional drift |
| `853/tcp` | not exposed | removed 2026-09-28 | AdGuard CloudNode stack is gone; no listener remains |
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

### F-GERBIL-3 — dead `853/tcp` publish (resolved 2026-09-28)
The unused `853:853` mapping was removed during the planned Gerbil recreation.
Gerbil and Traefik were recreated together and public routing remained healthy.

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

(Confirm the status path against the running gerbil 1.5.2 before merging.)

## Operational Notes

- **Gerbil owns the namespace**. If you recreate gerbil, you *must* also
  recreate Traefik: `docker compose -f stacks/core/docker-compose.yml --env-file .env up -d --force-recreate traefik`. Otherwise Traefik keeps
  referencing the old network namespace and 80/443 go dark.
- **Key file** at `config/key` is the gerbil identity; do NOT delete without
  reprovisioning all connected sites.
