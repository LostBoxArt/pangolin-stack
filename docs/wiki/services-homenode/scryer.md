---
title: "scryer"
slug: homenode-scryer
type: service
status: active
tags: ["homelab", "homenode", "service", "scryer"]
aliases: ["scryer"]
entities:
  primary: homenode-scryer
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "../system-overview.md", "./sonarr.md", "./radarr.md", "./bazarr.md", "./seerr.md", "./prowlarr.md"]
sources: ["/volume1/docker/config/scryer/docker-compose.yml", "host-configs/homenode/scryer/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-11-07
last_lint: 2026-11-07
---
# scryer

Unified media manager (movies + series + anime) that replaced the Sonarr / Radarr /
Bazarr / Profilarr / Recyclarr write path and the Seerr request front-end.
Rust application, single container.

- **Image**: `ghcr.io/scryer-media/scryer:0.21.24` (pinned; the tag has no `v` prefix)
- **Compose file**: `/volume1/docker/config/scryer/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/scryer/docker-compose.yml` (sanitized live snapshot, 2026-11-07)
- **Port (internal)**: `8080`; host publish `127.0.0.1:8099` (loopback only)
- **Router**: `request.example.com` (the only public media front door)
- **Volumes**: `/volume1/docker/config/scryer:/config`, `/volume1/media:/data`
  (single mount — required for hardlink imports), `/volume2/backups/scryer:/backups`
- **Healthcheck**: `wget -q -O /dev/null -T 5 http://127.0.0.1:8080/health/ready`

## Upstream Sources

- Image: `ghcr.io/scryer-media/scryer`

## Our Compose

```yaml
services:
  scryer:
    image: ghcr.io/scryer-media/scryer:0.21.24
    container_name: scryer
    restart: unless-stopped
    init: true
    security_opt: ["no-new-privileges:true"]
    environment:
      - TZ=Asia/Jerusalem
      - PUID=1000
      - PGID=1000
      - UMASK=022
      - SCRYER_PUBLIC_URL=https://request.example.com
      - SCRYER_BACKGROUND_ACQUISITION=true
      - SCRYER_WEBAUTHN_RP_ID=request.example.com
      - SCRYER_WEBAUTHN_RP_ORIGIN=https://request.example.com
      - SCRYER_WEBAUTHN_RP_NAME=Scryer
    ports:
      - "127.0.0.1:8099:8080"
    volumes:
      - /volume1/docker/config/scryer:/config
      - /volume1/media:/data
      - /volume2/backups/scryer:/backups
    healthcheck:
      test: ["CMD", "wget", "-q", "-O", "/dev/null", "-T", "5", "http://127.0.0.1:8080/health/ready"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks: [traefik_traefik]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.scryer-main.rule=Host(`request.example.com`)"
      - "traefik.http.routers.scryer-main.entrypoints=websecure"
      - "traefik.http.routers.scryer-main.tls.certresolver=cloudflare"
      - "traefik.http.routers.scryer-main.service=scryer-svc"
      - "traefik.http.services.scryer-svc.loadbalancer.server.port=8080"
```

## Libraries

Three libraries, all monitored, all using hardlink-or-copy import:

| Library | Root | Plex path |
|---|---|---|
| Movies | `/data/movies` | `/media/movies` |
| Series | `/data/tv` | `/media/tv` |
| Anime | `/data/anime` | `/media/anime` |

## Dependencies that must stay running

- **Prowlarr** — Scryer's indexer parent plus four Prowlarr-managed torrent children.
  Stopping Prowlarr removes the managed indexers.
- **qBittorrent** — the only download client. Scryer ships Weaver (Usenet), SABnzbd,
  NZBGet and HTTP as built-in client types but **no torrent client**; the official
  qBittorrent download-client plugin (v4.0.0) must be installed or all automatic
  acquisition is silently skipped.
- **Plex** — media server, path mapping `/media => /data`.

No Usenet is used in this homelab.

## Findings

### F-N-SCRYER-1 — no healthcheck on the original cutover (resolved 2026-11-07)

The container was created without a `healthcheck` block, so `docker ps` reporting
`Up` proved only that the process existed. A readiness probe
(`GET /health/ready` -> `{"status":"ok","ready":true}`) was verified, and the
healthcheck above was added and confirmed `healthy` with zero restarts.

**Gotcha:** Scryer binds IPv4 only. Inside the container `localhost` resolves to
`::1` first, so `http://localhost:8080/...` is refused. Use `127.0.0.1` in any
in-container probe.

### F-N-SCRYER-2 — season folder template mismatch caused mass re-download

Scryer's default season template was `Season {season}`, producing `Season 7`, while
the library stores Sonarr-style `Season 07`. Scryer therefore treated existing
seasons as missing and grabbed whole-season and complete-series packs. Fixed by
setting Series **and** Anime renaming to `Season {season:2}` and merging the
unpadded directories on disk.

### F-N-SCRYER-3 — "upgrades allowed" caused 4K re-downloads

Every quality profile had upgrades enabled, so all 1080p movies were re-grabbed at
2160p. Upgrades are now disabled on the 1080P, 4K and Anime profiles.

## Operational Notes

- **First-hours CPU load is expected** — artwork encoding, hash backfill and media
  analysis. Let library scans finish before judging performance.
- **`/config` holds the encryption key** for stored credentials. Losing it loses
  every saved API key and password. Back up `/config` before upgrades.
- Scryer cannot move a title between libraries; `updateTitle` rejects a facet change
  with `CATALOG_CHANGING_TITLE_FACET_UNSUPPORTED`. A library split requires a
  catalog rebuild (move folders, rescan, re-add, then delete the duplicates).
- Scryer exposes `/compat/sonarr` and `/compat/radarr` endpoints for arr-shaped
  API access.
- No per-user request quotas and no issue reporting (unlike Seerr). Library
  permissions support `request` and `autoApproveRequests` per user.
- `SCRYER_BACKGROUND_ACQUISITION` was used as an emergency brake during the
  over-acquisition incident. It is currently `true`; do not infer safety from the
  former brake.

## Verify safely

```bash
docker inspect scryer --format '{{.State.Status}} {{.State.Health.Status}}'
docker exec scryer wget -q -O - http://127.0.0.1:8080/health/ready
```

Expected: `running healthy` and `{"status":"ok","ready":true}`. Do not submit media
requests or trigger searches to test availability: they can create downloads.
