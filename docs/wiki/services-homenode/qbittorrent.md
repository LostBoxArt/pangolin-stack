---
title: "qbittorrent"
slug: homenode-qbittorrent
type: service
status: active
tags: ["homelab", "homenode", "service", "qbittorrent"]
aliases: ["qbittorrent"]
entities:
  primary: homenode-qbittorrent
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/qbittorrent/docker-compose.yml", "host-configs/homenode/qbittorrent/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# qbittorrent

Torrent client. LinuxServer.io image. Serves web UI at
`torrent.example.com` (Traefik-routed). **Runs with no VPN sidecar** —
outbound swarm traffic exits on the ISP IP.

- **Image**: `linuxserver/qbittorrent:latest` ⚠️
- **Compose file**: `/volume1/docker/config/qbittorrent/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/qbittorrent/docker-compose.yml` ✓
- **Port (internal)**: `8080` (WEBUI_PORT)
- **Router**: `torrent.example.com`
- **Volumes**:
  - `/volume1/docker/config/qbittorrent:/config`
  - `/volume1/media/downloads:/downloads`

## Upstream Sources

- Image docs: <https://docs.linuxserver.io/images/docker-qbittorrent/>
- qBit docs: <https://github.com/qbittorrent/qBittorrent/wiki>

## Our Compose

```yaml
services:
  qbittorrent:
    image: linuxserver/qbittorrent:latest
    container_name: qbittorrent
    restart: unless-stopped
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Jerusalem
      - WEBUI_PORT=8080
    volumes:
      - /volume1/docker/config/qbittorrent:/config
      - /volume1/media/downloads:/downloads
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:8080 >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks: [traefik_traefik]
    labels:
      - "traefik.http.routers.qbittorrent.rule=Host(`torrent.example.com`)"
      - "traefik.http.services.qbittorrent.loadbalancer.server.port=8080"
```

## Deviations / Findings

### F-N-QBIT-1 — no VPN sidecar (`high` / NH5)
qBit runs directly on the HomeNode network namespace. All outbound torrent
traffic (tracker announces, peer connections) uses the host's default
route = home ISP IP. Policy decision, not a compose bug — recorded here so
nobody mistakes it for an oversight.

If a VPN is desired, the standard pattern is:

1. Add a `gluetun` service with the VPN config.
2. Give qBit `network_mode: service:gluetun`.
3. Move qBit's Traefik labels onto the gluetun service (or keep them on
   qBit; the router just needs a reachable endpoint).

Sample:

```yaml
  gluetun:
    image: qmcgaw/gluetun:latest
    cap_add: [NET_ADMIN]
    environment:
      - VPN_SERVICE_PROVIDER=mullvad
      - VPN_TYPE=wireguard
      - WIREGUARD_PRIVATE_KEY=${MULLVAD_PRIVATE_KEY}
    networks: [traefik_traefik]

  qbittorrent:
    network_mode: service:gluetun
    # drop the `networks:` key
```

### F-N-QBIT-2 — `:latest` image (`medium` / NM2)
Pin from <https://github.com/linuxserver/docker-qbittorrent/pkgs/container/qbittorrent>.
qBit 5.1.4+ introduced the `Secure` cookie flag that broke Homarr's widget
on the CloudNode (fixed via `qbit-proxy`) — another reason to know exactly which
version is running.

### F-N-QBIT-3 — default admin password not enforced (`medium` / NM8 / `low` / NL1)
LSIO qBit starts with a randomly-generated temporary password printed to
`docker logs qbittorrent` on first boot. If that log line is ever missed,
and `admin` / `adminadmin` happens to be re-allowed by a config reset, the
UI is world-readable behind whatever auth fronts Traefik. Document the
post-install step: open the UI, change the admin password, confirm 2FA
isn't available (qBit has no built-in 2FA — rely on Pangolin auth).

## Remediation

### Fix F-N-QBIT-2

```yaml
    image: linuxserver/qbittorrent:5.1.x
```

### Fix F-N-QBIT-3

Not a compose change. Runbook:

1. First start: `docker logs qbittorrent | grep 'temporary password'`.
2. Log in with `admin` + that password.
3. Tools → Options → Web UI → change admin username + set a strong
   password.
4. Restart qBit to apply.

## Operational Notes

- `/downloads` shared with Sonarr + Radarr for hardlink imports.
- **Homarr widget from the CloudNode** uses the `qbit-proxy` sidecar on the CloudNode
  (see CloudNode [qbit-proxy](../services/qbit-proxy.md)) because of the
  `Secure` cookie issue introduced in qBit 5.1.4. Do NOT point Homarr
  directly at `https://torrent.example.com`.
- Cross-seed / autobrr: the companion [qui](./qui.md) service provides a
  nicer torrent-management UI that talks to qBit's API.
