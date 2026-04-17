---
title: "qui"
slug: homenode-qui
type: service
status: active
tags: ["homelab", "homenode", "service", "qui"]
aliases: ["qui"]
entities:
  primary: homenode-qui
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/qui/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# qui

autobrr's "qui" — modern web UI for managing qBittorrent torrents (sort,
bulk re-category, cross-seed workflows, etc.).

- **Image**: `ghcr.io/autobrr/qui:latest` ⚠️
- **Compose file**: `/volume1/docker/config/qui/docker-compose.yml`
- **Tracked copy**: **not tracked** (finding NM1)
- **Port (internal)**: `7476`
- **Router**: `flood.example.com` ⚠️ (legacy name, see finding)
- **User**: `1000:1000`
- **Volume**: `/volume1/docker/config/qui:/config`

## Upstream Sources

- Project: <https://github.com/autobrr/qui>
- Image: <https://github.com/autobrr/qui/pkgs/container/qui>
- autobrr suite: <https://autobrr.com/>

## Our Compose

```yaml
services:
  qui:
    image: ghcr.io/autobrr/qui:latest
    container_name: qui
    restart: unless-stopped
    user: "1000:1000"
    environment: [TZ=Asia/Jerusalem]
    volumes:
      - /volume1/docker/config/qui:/config
    networks: [traefik_traefik]
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.flood.rule=Host(`flood.example.com`)"
      - "traefik.http.routers.flood.entrypoints=websecure"
      - "traefik.http.routers.flood.tls.certresolver=cloudflare"
      - "traefik.http.services.flood.loadbalancer.server.port=7476"
```

## Findings

### F-N-QUI-1 — router / DNS named `flood` (`medium` / NM6)
The router and service labels say `flood`, and DNS is
`flood.example.com`. This is a vestige of an earlier install where Flood
(a different project) was the UI. It's misleading — operators clicking
"flood.example.com" land on qui's UI.

Fix in two steps:

1. Add a new router `qui` pointing at the same service.
2. Add Cloudflare DNS `qui.example.com → CNAME flood.example.com`.
3. Verify both work.
4. Flip bookmarks / Homarr widgets to the new name.
5. Retire the old `flood.*` router + DNS record.

### F-N-QUI-2 — `:latest` image (`medium` / NM2)
Pin from the upstream tags.

### F-N-QUI-3 — no healthcheck (`medium` / NM4)
qui serves a web UI; `curl localhost:7476` is a valid probe.

## Remediation

### Fix F-N-QUI-1 — router rename

```yaml
    labels:
      - "traefik.enable=true"
      # new primary router
      - "traefik.http.routers.qui.rule=Host(`qui.example.com`)"
      - "traefik.http.routers.qui.entrypoints=websecure"
      - "traefik.http.routers.qui.tls.certresolver=cloudflare"
      - "traefik.http.services.qui.loadbalancer.server.port=7476"
      # legacy alias during cut-over
      - "traefik.http.routers.flood.rule=Host(`flood.example.com`)"
      - "traefik.http.routers.flood.entrypoints=websecure"
      - "traefik.http.routers.flood.tls.certresolver=cloudflare"
      - "traefik.http.routers.flood.service=qui"
```

Once traffic is fully on `qui.example.com`, delete the `flood.*` block.

### Fix F-N-QUI-3

```yaml
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:7476/ >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

## Operational Notes

- qui talks to qBit via the API; configure in qui's UI:
  `http://qbittorrent:8080` + qBit admin user/password.
- Because qui runs as `1000:1000` (not via LSIO's PUID/PGID mapping), the
  `/config` mount on the host must be owned by UID 1000. Check with
  `ls -n /volume1/docker/config/qui`.
- qui supports **multiple qBit instances** — useful if you ever add a
  VPN'd second qBit (see F-N-QBIT-1 in [qbittorrent](./qbittorrent.md)).
