---
title: "homarr"
slug: vps-homarr
type: service
status: active
tags: ["homelab", "vps", "service", "homarr"]
aliases: ["homarr"]
entities:
  primary: vps-homarr
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/dashboard/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# homarr

Personal landing / dashboard page at `home.dennisb.xyz`. Embeds widgets for
media services, torrents, system status, etc.

- **Image**: `ghcr.io/homarr-labs/homarr:latest` ⚠️
- **Compose file**: `stacks/dashboard/docker-compose.yml`
- **Port**: `7575` (published on host, also Traefik-fronted)
- **Data**: `/opt/homarr/appdata:/appdata` (host bind, **not** inside repo)
- **Socket**: `/var/run/docker.sock` (for Docker integration widgets)
- **TZ**: `Asia/Jerusalem`

## Upstream Sources

- Install docs: <https://homarr.dev/docs/getting-started/installation/docker/>
- Releases: <https://github.com/homarr-labs/homarr/releases>

## Upstream Reference Compose

```yaml
services:
  homarr:
    container_name: homarr
    image: ghcr.io/homarr-labs/homarr:latest
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock   # optional
      - ./homarr/appdata:/appdata
    environment:
      - SECRET_ENCRYPTION_KEY=
    ports:
      - '7575:7575'
```

## Our Compose (relevant slice)

```22:46:stacks/dashboard/docker-compose.yml
  homarr:
    container_name: homarr
    image: ghcr.io/homarr-labs/homarr:latest
    networks:
      - pangolin
    restart: unless-stopped
    depends_on:
      - qbit-proxy
    volumes:
      - /opt/homarr/appdata:/appdata
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - 7575:7575
    environment:
      - SECRET_ENCRYPTION_KEY=${HOMARR_SECRET_KEY}
      - TZ=Asia/Jerusalem
    extra_hosts:
      - "torrent.dennisb.xyz:192.168.0.10"
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.homarr.rule=Host(`home.dennisb.xyz`)"
      - "traefik.http.routers.homarr.entrypoints=websecure"
      - "traefik.http.routers.homarr.tls.certresolver=letsencrypt"
      - "traefik.http.routers.homarr.middlewares=geoblock@file,security-headers@file"
      - "traefik.http.services.homarr.loadbalancer.server.port=7575"
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Data path | `./homarr/appdata` | `/opt/homarr/appdata` (host) | intentional — kept outside repo so backups & repo layout are cleaner |
| `depends_on: qbit-proxy` | n/a | added | intentional — qBittorrent widget needs the proxy sidecar |
| `extra_hosts` | n/a | added | intentional — resolves `torrent.dennisb.xyz` to NASUS directly |
| Port publish | `7575:7575` | same | ✓ |
| `:latest` tag | yes | yes | drift risk |
| DB env | default (`better-sqlite3` + `/appdata/db/db.sqlite`) | default | ✓ |

## Findings

### F-HOMARR-1 — `:latest` image tag (`medium` / M10 scope)
Homarr ships a lot of schema migrations. A jump from, say, 1.58 to 1.60
triggered on an unattended pull will auto-migrate the SQLite DB *forward*.
If you later want to roll back, the old image won't understand the new
schema.

### F-HOMARR-2 — no healthcheck (`low` / L3)
Homarr exposes a health endpoint; adding a check helps the UI to signal
startup progress and lets `stackctl.sh status` turn green reliably.

### F-HOMARR-3 — `docker.sock` is optional, still mounted
Fine — we use docker-integration widgets. Just noted for clarity: if you
ever decide to disable docker widgets, drop the socket mount for defense in
depth.

## Remediation

### Fix F-HOMARR-1

Pin a release:

```yaml
    image: ghcr.io/homarr-labs/homarr:1.59.1
```

Keep an eye on <https://homarr.dev/blog> for breaking-change notices before
bumping.

### Fix F-HOMARR-2

```yaml
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:7575/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

(Verify the exact health path against your installed Homarr version — it
moved from `/api/healthcheck` to `/api/health` around 1.x.)

## Operational Notes

- **qBittorrent widget quirk** (Homarr v0.15+ with qBittorrent v5.1.4+):
  the secure-cookie flag breaks the widget. We work around it with the
  `qbit-proxy` sidecar — see [qbit-proxy](./qbit-proxy.md).
- `SECRET_ENCRYPTION_KEY` is single-source-of-truth for encrypted
  credentials in Homarr's DB. **Do not rotate without exporting secrets
  first** — all saved service credentials become unreadable.
- Host bind path `/opt/homarr/appdata` is excluded from `backup.sh` by
  default; confirm your backup policy includes it if you want dashboard
  customization backed up.
