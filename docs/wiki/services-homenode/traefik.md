---
title: "traefik (HomeNode)"
slug: homenode-traefik
type: service
status: active
tags: ["homelab", "homenode", "service", "traefik"]
aliases: ["traefik (HomeNode)", "traefik"]
entities:
  primary: homenode-traefik
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/traefik/docker-compose.yml", "host-configs/homenode/traefik/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# traefik (HomeNode)

Home-LAN reverse proxy for all HomeNode services. Terminates TLS for
`*.example.com` via Cloudflare DNS challenge. Distinct from the CloudNode Traefik.

- **Image**: `traefik:v3.7.17`
- **Compose file**: `/volume1/docker/traefik/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/traefik/docker-compose.yml` (sanitized live snapshot, 2026-10-31)
- **Ports**: host `80`, `443`; ping health endpoint is container-only on `:8082`; no insecure API host endpoint is enabled
- **Networks**: `traefik_traefik` (external) — all HomeNode services join it
- **Cert resolver**: `cloudflare` (DNS-01 via Cloudflare API, credentials in `.env`)
- **API**: `api.insecure` is not enabled; a dedicated ping entrypoint on `:8082` backs the container healthcheck. Neither ping endpoint is published to the host.
- **Config**:
  - Dynamic: `/volume1/docker/traefik/dynamic/`
  - ACME: `/volume1/docker/traefik/letsencrypt/acme.json`

## Upstream Sources

- Traefik docs: <https://doc.traefik.io/traefik/>
- `--api.insecure` guidance: <https://doc.traefik.io/traefik/operations/api/#insecure>

## Our Compose

```yaml
services:
  traefik:
    image: traefik:v3.7.17
    container_name: traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    command:
      - "--api.dashboard=true"
      - "--log.level=INFO"
      - "--entrypoints.ping.address=:8082"
      - "--ping=true"
      - "--ping.entrypoint=ping"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
      - "--entrypoints.web.http.redirections.entrypoint.to=websecure"
      - "--entrypoints.web.http.redirections.entrypoint.scheme=https"
      - "--entrypoints.web.http.redirections.entrypoint.permanent=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--providers.file.directory=/etc/traefik/dynamic"
      - "--providers.file.watch=true"
      - "--certificatesresolvers.cloudflare.acme.dnschallenge=true"
      - "--certificatesresolvers.cloudflare.acme.dnschallenge.provider=cloudflare"
      - "--certificatesresolvers.cloudflare.acme.dnschallenge.resolvers=1.1.1.1:53,8.8.8.8:53"
      - "--certificatesresolvers.cloudflare.acme.email=hello@example.com"
      - "--certificatesresolvers.cloudflare.acme.storage=/letsencrypt/acme.json"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - /volume1/docker/traefik/letsencrypt:/letsencrypt
      - /volume1/docker/traefik/dynamic:/etc/traefik/dynamic
    env_file: [.env]
    healthcheck:
      test: ["CMD-SHELL", "wget -q -O /dev/null http://127.0.0.1:8082/ping || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks: [traefik_traefik]
```

## Deviations from CloudNode Traefik

| Aspect | CloudNode | HomeNode | Intent |
|---|---|---|---|
| Cert resolver | `letsencrypt` (HTTP-01) | `cloudflare` (DNS-01) | HomeNode is LAN-only; DNS-01 avoids exposing port 80 to the internet |
| Dashboard | off | on, container-only | access through SSH forwarding |
| docker.sock | read-write | read-only bind mount | socket access still permits Docker API operations; this is not API authorization |
| Access logs | JSON, consumed by CrowdSec | none | no CrowdSec on HomeNode |
| CrowdSec plugin | yes | no | no local CrowdSec |
| Network namespace | shared with Gerbil | standalone | n/a |

## Findings

### F-N-TRAEFIK-1 — host dashboard publication removed; insecure API setting removed (resolved 2026-10-31)
The former host dashboard publication and `api.insecure` setting are absent. The API is not exposed through the insecure entrypoint; the dedicated ping entrypoint on `:8082` is used only by the container healthcheck.

### F-N-TRAEFIK-2 — image pinned (resolved 2026-10-31)
HomeNode Traefik is pinned to `v3.7.17`.

### F-N-TRAEFIK-3 — no access logs / no CrowdSec (`medium` / NM7)
Traefik's default log format is text-only and written to stdout. No JSON
access log means no CrowdSec ingestion possible even if we wanted to add a
local CrowdSec.

### F-N-TRAEFIK-4 — Docker socket access
The existing `:ro` bind is retained. It does not make Docker API access read-only; changing the socket boundary requires a separately tested access proxy.

## Remediation

### Dashboard access after F-N-TRAEFIK-1

The 2026-10-27 dashboard-forward procedure is obsolete. The 2026-10-31 audit removed `api.insecure` and verified that the old API port refuses connections.

The duplicate `dynamic/request.yaml` was removed after confirming the enabled `seerr@docker` router serves the same hostname and container port. Its HTTPS redirect remained 307. `dynamic/adguard.yaml` points to an active router-hosted AdGuard instance and is retained.

### F-N-TRAEFIK-2 — image pinned (resolved 2026-10-31)
HomeNode Traefik is pinned to `v3.7.17`.

### Fix F-N-TRAEFIK-3 (optional)

```yaml
    command:
      ...
      - "--accesslog=true"
      - "--accesslog.filepath=/var/log/traefik/access.log"
      - "--accesslog.format=json"
      - "--accesslog.bufferingsize=100"
    volumes:
      - /volume1/docker/traefik/logs:/var/log/traefik
```

Only worthwhile if you plan to deploy a local CrowdSec on HomeNode.

## Operational Notes

- The `traefik_traefik` network name is the automatically-generated
  "`<project>_<network>`" form from the initial compose run; every service
  joining as `external: true` must reference the same name exactly.
- Cloudflare API token in `.env` needs `Zone:Read` + `DNS:Edit` on the
  `example.com` zone.
- Public internet reaches HomeNode services via Pangolin (CloudNode) → Newt tunnel,
  not via inbound 443. HomeNode's `443:443` is only for LAN clients.
