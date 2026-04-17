---
title: "prowlarr"
slug: nasus-prowlarr
type: service
status: active
tags: ["homelab", "nasus", "service", "prowlarr"]
aliases: ["prowlarr"]
entities:
  primary: nasus-prowlarr
  mentions: []
related: ["./README.md", "./nasus-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/prowlarr/docker-compose.yml", "host-configs/nasus/prowlarr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# prowlarr

Indexer manager for the *arr suite — federates torrent/usenet indexers
into one API that Sonarr/Radarr query.

- **Image**: `ghcr.io/linuxserver/prowlarr:develop` ⚠️ **unstable channel**
- **Compose file**: `/volume1/docker/config/prowlarr/docker-compose.yml`
- **Tracked copy**: `host-configs/nasus/prowlarr/docker-compose.yml` ✓
- **Port (internal)**: `9696`
- **Router**: `prowlarr.dennisb.xyz`
- **Volume**: `/volume1/docker/config/prowlarr:/config`

## Upstream Sources

- Image docs: <https://docs.linuxserver.io/images/docker-prowlarr/>
- Channels: `:latest` (stable) vs `:develop` (nightly) vs `:test`
- Upstream project: <https://github.com/Prowlarr/Prowlarr>

## Our Compose

```yaml
services:
  prowlarr:
    image: ghcr.io/linuxserver/prowlarr:develop
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
      - "traefik.http.routers.prowlarr.rule=Host(`prowlarr.dennisb.xyz`)"
      - "traefik.http.services.prowlarr.loadbalancer.server.port=9696"
```

## Findings

### F-N-PROWLARR-1 — unstable tag `:develop` (`high` / NH4)
`:develop` pulls the nightly channel. Unless you're actively chasing a
specific fix, use `:latest` (stable) or a pinned version tag. Nightlies
can break indexer definitions, auth flows, or the DB schema without a
release note — and there's no downgrade path if the DB gets migrated.

### F-N-PROWLARR-2 — shared with LSIO apps
Same `:latest` / `:develop` pin-policy family as the other LSIO apps.
Fix together.

## Remediation

### Fix F-N-PROWLARR-1

Switch to the stable tag:

```yaml
    image: linuxserver/prowlarr:latest
```

Or better, a concrete release from
<https://github.com/linuxserver/docker-prowlarr/pkgs/container/prowlarr>:

```yaml
    image: linuxserver/prowlarr:1.x.x.xxxx-ls145
```

If the current install actually depends on a `:develop` feature, leave it
but add a comment saying WHY and linking to the upstream issue.

## Operational Notes

- Prowlarr pushes indexers to Sonarr / Radarr via their API keys
  (Settings → Apps → Sonarr/Radarr). Use the in-network hostnames
  `http://sonarr:8989` etc.
- FlareSolverr integration: Settings → Indexers → Configure indexer →
  "FlareSolverr URL" = `http://flaresolverr:8191`. Required for any
  indexer behind Cloudflare's anti-bot page.
- Tests failing with TLS errors usually mean the indexer's cert expired
  and Prowlarr's CA bundle needs refreshing — restart the container.
