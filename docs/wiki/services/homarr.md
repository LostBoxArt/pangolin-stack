---
title: "homarr"
slug: cloudnode-homarr
type: service
status: active
tags: ["homelab", "cloudnode", "service", "homarr"]
aliases: ["homarr"]
entities:
  primary: cloudnode-homarr
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/dashboard/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-10
last_lint: 2026-10-10
---
# homarr

Personal landing / dashboard page at `home.example.com`. Embeds widgets for
media services, torrents, system status, etc.

- **Image**: `ghcr.io/homarr-labs/homarr:v2.4.0` (stable pin — v2 migration completed and database verified)
- **Compose file**: `stacks/dashboard/docker-compose.yml`
- **Port**: `7575` (published on host, also Traefik-fronted)
- **Data**: `/opt/homarr/appdata:/appdata` (host bind, **not** inside repo)
- **TZ**: `Asia/Jerusalem`
- **Env symlink**: `stacks/dashboard/.env` → `../../.env` (required — compose auto-load picks up `HOMARR_SECRET_KEY`)

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

```22:36:stacks/dashboard/docker-compose.yml
  homarr:
    container_name: homarr
    image: ghcr.io/homarr-labs/homarr:v2.4.0
    networks:
      - pangolin
    restart: unless-stopped
    depends_on:
      - qbit-proxy
    volumes:
      - /opt/homarr/appdata:/appdata
    ports:
      - 7575:7575
    environment:
      - SECRET_ENCRYPTION_KEY=${HOMARR_SECRET_KEY}
      - TZ=Asia/Jerusalem
    extra_hosts:
      - "torrent.example.com:192.168.1.10"
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Data path | `./homarr/appdata` | `/opt/homarr/appdata` (host) | intentional — kept outside repo so backups & repo layout are cleaner |
| `depends_on: qbit-proxy` | n/a | added | intentional — qBittorrent widget needs the proxy sidecar |
| `extra_hosts` | n/a | added | intentional — resolves `torrent.example.com` to HomeNode directly |
| Port publish | `7575:7575` | same | ✓ |
| `:latest` tag | yes | no — pinned to `v2.4.0` | intentional (control over schema migrations) |
| DB env | default (`better-sqlite3` + `/appdata/db/db.sqlite`) | default | ✓ |

## Findings

### F-HOMARR-1 — `:latest` image tag → resolved, now on stable `v2.4.0` (✓)
Update 2026-05-09: Switched from `:latest` (main branch) to `v1.61.1-beta.1` (beta branch).
The beta merged 3 Node processes into 1 (#5600) plus idle-memory reduction (#5637),
cutting memory from ~595 MiB to ~181 MiB.

Update 2026-10-10: Upgraded to the pinned v2 migration release `v2.4.0`. The
SQLite database passed integrity verification after migration; the board and
application inventory remained intact. The Docker socket remains intentionally
absent.

### F-HOMARR-2 — no healthcheck (`low` / L3)
Homarr exposes a health endpoint; adding a check helps the UI to signal
startup progress and lets `stackctl.sh status` turn green reliably.

### F-HOMARR-3 — `docker.sock` mount removed (✓ resolved 2026-09-28)
Update 2026-09-28: The socket mount was removed. Homarr's `integration` table
contained only `dashDot`, `qBittorrent`, and `archiveTeamWarrior` — there was
**no Docker integration configured**, so the mount granted root-equivalent
access to any container-escape for no functional benefit. Note that mounting the
socket `:ro` would not have helped; the Docker API accepts writes through the
socket regardless of the file mode, so removal was the only meaningful fix.

Re-add only if a Docker widget is actually configured, and prefer
`docker-socket-proxy` over the raw socket if that day comes.

## Remediation

### Fix F-HOMARR-1 (resolved)

Now pinned to stable `v2.4.0`:

```yaml
    image: ghcr.io/homarr-labs/homarr:v2.4.0
```

The beta is no longer needed. Bump deliberately and check
<https://github.com/homarr-labs/homarr/releases> before doing so.

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
- **qbit-proxy Host header**: The proxy sends `Host: torrent.example.com` to
  HomeNode's Traefik. If the Traefik route on HomeNode doesn't match (e.g.
  expects the same host in its route), the integration returns 404. The `TARGET_HOST`
  env var in `qbit-proxy` must match the Traefik route.
- `SECRET_ENCRYPTION_KEY` is single-source-of-truth for encrypted
  credentials in Homarr's DB. **Do not rotate without exporting secrets
  first** — all saved service credentials become unreadable.
- Host bind path `/opt/homarr/appdata` is excluded from `backup.sh` by
  default; confirm your backup policy includes it if you want dashboard
  customization backed up.
- **Env file**: `stacks/dashboard/.env` is a symlink to `../../.env`.
  Compose only auto-loads `.env` from the compose file's directory — the
  symlink ensures `HOMARR_SECRET_KEY` resolves without `--env-file`.
