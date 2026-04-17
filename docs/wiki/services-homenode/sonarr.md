---
title: "sonarr"
slug: homenode-sonarr
type: service
status: active
tags: ["homelab", "homenode", "service", "sonarr"]
aliases: ["sonarr"]
entities:
  primary: homenode-sonarr
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/sonarr/docker-compose.yml", "host-configs/homenode/sonarr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# sonarr

TV series manager. LinuxServer.io image.

- **Image**: `linuxserver/sonarr:latest` ⚠️
- **Compose file**: `/volume1/docker/config/sonarr/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/sonarr/docker-compose.yml` ✓
- **Port (internal)**: `8989`
- **Router**: `sonarr.example.com` (Traefik cert resolver `cloudflare`)
- **Volumes**:
  - `/volume1/docker/config/sonarr:/config`
  - `/volume1/media/tv:/tv`
  - `/volume1/media/downloads:/downloads`
- **Env**: `PUID=1000`, `PGID=1000`, `TZ=Asia/Jerusalem`

## Upstream Sources

- Image docs: <https://docs.linuxserver.io/images/docker-sonarr/>
- Releases: <https://github.com/linuxserver/docker-sonarr/releases>

## Our Compose

```yaml
services:
  sonarr:
    image: linuxserver/sonarr:latest
    container_name: sonarr
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Jerusalem
    volumes:
      - /volume1/docker/config/sonarr:/config
      - /volume1/media/tv:/tv
      - /volume1/media/downloads:/downloads
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:8989/ping >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks: [traefik_traefik]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.sonarr.rule=Host(`sonarr.example.com`)"
      - "traefik.http.routers.sonarr.entrypoints=websecure"
      - "traefik.http.routers.sonarr.tls.certresolver=cloudflare"
      - "traefik.http.services.sonarr.loadbalancer.server.port=8989"
```

## Deviations / Findings

The pattern here is shared with **radarr / bazarr / prowlarr / profilarr** —
read all four as a group. Common items:

- **`:latest` image** (`medium` / NM2) — pin to a LSIO-tagged release.
  LSIO images rebuild against upstream Sonarr releases; `:latest` follows
  the default channel. Pinning keeps your upgrade cadence intentional.
- **Healthcheck is good**: `/ping` is the canonical endpoint.
- **Media paths are correct**: `/tv` for library, `/downloads` for inbox.
  Matches qBit's `/volume1/media/downloads` bind so the downloaded file's
  path inside qBit == the path Sonarr sees (critical for hardlinks /
  atomic moves).

## Remediation

### Pin the image

Pick the current tag from <https://github.com/linuxserver/docker-sonarr/pkgs/container/sonarr>:

```yaml
    image: linuxserver/sonarr:4.0.x   # match the Sonarr release you want
```

## Operational Notes

- **Hardlinks**: both `/tv` (library) and `/downloads` (inbox) live on
  `/volume1/media/` on the host, same filesystem → Sonarr uses hardlinks
  for imports (zero-copy, zero-seed-loss). Verify with `ls -li` showing
  matching inode counts after a test import.
- API key is persisted in `/config/config.xml` — needed by qBit cross-seed
  scripts and Prowlarr sync.
- Sonarr v4 has a different DB schema than v3; downgrades require restoring
  a pre-upgrade backup from `/config/Backups/`.
