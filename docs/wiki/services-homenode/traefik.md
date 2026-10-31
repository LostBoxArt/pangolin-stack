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
last_ingested: 2026-10-27
last_lint: 2026-04-17
---
# traefik (HomeNode)

Home-LAN reverse proxy for all HomeNode services. Terminates TLS for
`*.example.com` via Cloudflare DNS challenge. Distinct from the CloudNode Traefik.

- **Image**: `traefik:latest` ⚠️
- **Compose file**: `/volume1/docker/traefik/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/traefik/docker-compose.yml`
- **Ports**: host `80`, `443`; dashboard `8080` is container-only with no host publication
- **Networks**: `traefik_traefik` (external) — all HomeNode services join it
- **Cert resolver**: `cloudflare` (DNS-01 via Cloudflare API,
  credentials in `.env`)
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
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    command:
      - "--api.dashboard=true"
      - "--api.insecure=true"
      - "--log.level=INFO"
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
      test: ["CMD-SHELL", "wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1"]
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

### F-N-TRAEFIK-1 — host dashboard publication removed (resolved 2026-10-27)
The former `9080:8080` host publication is removed. A loopback-only binding still answered through the NAS's network path during testing, so it was insufficient. With no publication, native Mac TCP and VPS probes through both Tailscale and Olm failed to reach host port 9080. The API still uses `--api.insecure=true`; shared Docker-network peers can reach its container port, and operators use SSH forwarding.

### F-N-TRAEFIK-2 — `:latest` image (`high` / NH2)
See CloudNode F-TRAEFIK-1 for rationale — same risk, different host.

### F-N-TRAEFIK-3 — no access logs / no CrowdSec (`medium` / NM7)
Traefik's default log format is text-only and written to stdout. No JSON
access log means no CrowdSec ingestion possible even if we wanted to add a
local CrowdSec.

### F-N-TRAEFIK-4 — Docker socket access
The existing `:ro` bind is retained. It does not make Docker API access read-only; changing the socket boundary requires a separately tested access proxy.

## Remediation

### Dashboard access after F-N-TRAEFIK-1

Discover the current container address, then forward its dashboard port over SSH. Repeat discovery after container recreation:

```bash
TRAEFIK_IP=$(ssh jesus@192.168.1.10 "docker inspect traefik --format '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}'" | awk '{print $1}')
test -n "$TRAEFIK_IP" && ssh -N -L "127.0.0.1:19080:${TRAEFIK_IP}:8080" jesus@192.168.1.10
```

Open `http://127.0.0.1:19080/dashboard/`. On 2026-10-27, `/api/overview` returned 200 through this forward; the same image remained healthy, public 80/443 bindings were preserved, and Seerr, Dashdot and AdGuard HTTPS responses were unchanged.

The duplicate `dynamic/request.yaml` was removed after confirming the enabled `seerr@docker` router serves the same hostname and container port. Its HTTPS redirect remained 307. `dynamic/adguard.yaml` points to an active router-hosted AdGuard instance and is retained.

### Fix F-N-TRAEFIK-2

```yaml
    image: traefik:v3.6
```

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
