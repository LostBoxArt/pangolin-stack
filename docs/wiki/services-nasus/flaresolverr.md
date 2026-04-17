---
title: "flaresolverr"
slug: nasus-flaresolverr
type: service
status: active
tags: ["homelab", "nasus", "service", "flaresolverr"]
aliases: ["flaresolverr"]
entities:
  primary: nasus-flaresolverr
  mentions: []
related: ["./README.md", "./nasus-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/FlareSolverr/docker-compose.yml", "host-configs/nasus/FlareSolverr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# flaresolverr

Cloudflare anti-bot challenge solver. Runs a headless browser; Prowlarr
and the *arr apps proxy indexer requests through it when hitting sites
protected by Cloudflare's Under-Attack Mode / Turnstile.

- **Image**: `ghcr.io/flaresolverr/flaresolverr:latest` ⚠️
- **Compose file**: `/volume1/docker/config/FlareSolverr/docker-compose.yml`
  (note capital `F`)
- **Tracked copy**: `host-configs/nasus/FlareSolverr/docker-compose.yml` ✓
- **Port (internal)**: `8191`
- **Router**: `flaresolverr.dennisb.xyz`

## Upstream Sources

- Project: <https://github.com/FlareSolverr/FlareSolverr>
- Image tags: <https://github.com/FlareSolverr/FlareSolverr/pkgs/container/flaresolverr>

## Our Compose

```yaml
services:
  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    container_name: flaresolverr
    restart: unless-stopped
    environment:
      - LOG_LEVEL=info
      - TZ=Asia/Jerusalem
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:8191/ >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks: [traefik_traefik]
    labels:
      - "traefik.http.routers.flaresolverr.rule=Host(`flaresolverr.dennisb.xyz`)"
      - "traefik.http.services.flaresolverr.loadbalancer.server.port=8191"
```

## Deviations / Findings

### F-N-FLARE-1 — `:latest` image (`medium` / NM2)
Pin a version. FlareSolverr embeds a Chromium build; breaking changes
happen when Cloudflare ships new anti-bot iterations and the browser
version gets bumped to match.

### F-N-FLARE-2 — healthcheck path (`low` / NL3)
Upstream docs recommend `/v1` or a POST-to-`/v1` style probe. Ours hits
`/` which returns the "FlareSolverr is ready!" HTML banner. Works, just
not canonical.

### F-N-FLARE-3 — publicly routed, but does it need to be? (`low`)
Traefik exposes `flaresolverr.dennisb.xyz`. The service is only ever
consumed internally by Prowlarr / *arr apps on the same Docker network.
Public DNS + TLS for a debug endpoint is harmless but unnecessary.
Consider dropping the labels; use `http://flaresolverr:8191` from inside
the network.

## Remediation

### Fix F-N-FLARE-1

```yaml
    image: ghcr.io/flaresolverr/flaresolverr:v3.x.x
```

### Fix F-N-FLARE-3 (optional)

Remove the Traefik labels block entirely. Internal consumers don't need
DNS routing.

## Operational Notes

- Prowlarr config: Settings → Indexers → specific indexer → "FlareSolverr
  URL" = `http://flaresolverr:8191`.
- FlareSolverr is resource-heavy (spawns a browser per request). If NASUS
  CPU gets hot during indexer test storms, FlareSolverr is almost always
  the cause — check with `docker stats`.
- Sessions can leak if FlareSolverr is restarted mid-request. Restarting
  it is safe; Prowlarr will retry failed indexer calls on its own schedule.
