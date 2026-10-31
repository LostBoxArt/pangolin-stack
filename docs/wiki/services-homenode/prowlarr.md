---
title: "prowlarr"
slug: homenode-prowlarr
type: service
status: active
tags: ["homelab", "homenode", "service", "prowlarr"]
aliases: ["prowlarr"]
entities:
  primary: homenode-prowlarr
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/prowlarr/docker-compose.yml", "host-configs/homenode/prowlarr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# prowlarr

Indexer manager for the *arr suite — federates torrent/usenet indexers
into one API that Sonarr/Radarr query.

- **Image**: `ghcr.io/linuxserver/prowlarr:2.7.0` (stable pin; the former `:develop` channel finding is resolved)
- **Compose file**: `/volume1/docker/config/prowlarr/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/prowlarr/docker-compose.yml` (sanitized live snapshot, 2026-10-31)
- **Port (internal)**: `9696`
- **Router**: `prowlarr.example.com`
- **Volume**: `/volume1/docker/config/prowlarr:/config`

## Upstream Sources

- Image docs: <https://docs.linuxserver.io/images/docker-prowlarr/>
- Channels: `:latest` (stable) vs `:develop` (nightly) vs `:test`
- Upstream project: <https://github.com/Prowlarr/Prowlarr>

## Our Compose

```yaml
services:
  prowlarr:
    image: ghcr.io/linuxserver/prowlarr:2.7.0
    container_name: prowlarr
    restart: unless-stopped
    environment: [PUID=1000, PGID=1000, TZ=Asia/Jerusalem]
    volumes:
      - /volume1/docker/config/prowlarr:/config
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:9696/ping >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks: [traefik_traefik]
    labels:
      - "traefik.http.routers.prowlarr.rule=Host(`prowlarr.example.com`)"
      - "traefik.http.services.prowlarr.loadbalancer.server.port=9696"
```

## Findings

The former `:develop` finding is resolved: the deployed image is now pinned to `ghcr.io/linuxserver/prowlarr:2.7.0`.

### F-N-PROWLARR-2 — shared with LSIO apps
Same `:latest` / `:develop` pin-policy family as the other LSIO apps.
Fix together.

## Remediation

The former `:develop` remediation is resolved by the deployed `2.7.0` pin. Retain the exact pin and review the upstream release before changing it.

## Operational Notes

- Prowlarr pushes indexers to Sonarr / Radarr via their API keys
  (Settings → Apps → Sonarr/Radarr). Use the in-network hostnames
  `http://sonarr:8989` etc.
- FlareSolverr integration: Settings → Indexers → Configure indexer →
  "FlareSolverr URL" = `http://flaresolverr:8191`. Required for any
  indexer behind Cloudflare's anti-bot page.
- Tests failing with TLS errors usually mean the indexer's cert expired
  and Prowlarr's CA bundle needs refreshing — restart the container.
