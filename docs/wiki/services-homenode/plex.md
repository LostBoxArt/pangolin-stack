---
title: "plex"
slug: homenode-plex
type: service
status: active
tags: ["homelab", "homenode", "service", "plex"]
aliases: ["plex"]
entities:
  primary: homenode-plex
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md", "../maintenance-2026-10-31.md", "../concepts/port-matrix.md"]
sources: ["/volume1/docker/config/plex/docker-compose.yml", "/volume1/docker/traefik/dynamic/plex.yaml", "/conf/config.xml", "host-configs/homenode/plex/docker-compose.yml", "docs/wiki/maintenance-2026-10-31.md"]
confidence: high
audience_level: operator
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# plex

Plex Media Server on HomeNode. The container uses host networking and serves
media directly through a WAN `32400/tcp` router forward. `plex.example.com` is
served by the local Traefik file provider; Pangolin remains the path for the web
UI only. Hardware transcoding is enabled via `/dev/dri`.

- **Image**: `linuxserver/plex:latest` ⚠️
- **Compose file**: `/volume1/docker/config/plex/docker-compose.yml`
- **Tracked copy**: `host-configs/homenode/plex/docker-compose.yml` ✓
- **Network**: `network_mode: host`; no Compose `ports:`, Docker networks, or Traefik labels
- **Media ingress**: WAN `32400/tcp` forwarded directly to the NAS
- **Web UI**: `plex.example.com` via the local Traefik file provider (`dynamic/plex.yaml`), targeting `http://<homenode-lan-ip>:32400`; Pangolin serves the web UI path
- **Remote access**: manual port mapping `32400`, relay disabled, no per-stream upload cap; published custom access URL is the WAN IP only
- **Database**: `/volume2/plex-db` (SSD) mounted at Plex's `Plug-in Support/Databases` path
- **Volumes**:
  - `/volume1/docker/config/plex:/config`
  - `/volume1/media:/media`
  - `/volume2/plex-db:/config/Library/Application Support/Plex Media Server/Plug-in Support/Databases`
- **Devices**: `/dev/dri` (Intel iGPU for Quick Sync transcoding)

## Upstream Sources

- Image docs: <https://docs.linuxserver.io/images/docker-plex/>
- Plex docs: <https://support.plex.tv/articles/categories/plex-media-server/>

## Our Compose

```yaml
services:
  plex:
    image: linuxserver/plex:latest
    container_name: plex
    restart: unless-stopped
    network_mode: host
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Jerusalem
    volumes:
      - /volume1/docker/config/plex:/config
      - /volume1/media:/media
      - /volume2/plex-db:/config/Library/Application Support/Plex Media Server/Plug-in Support/Databases
    devices:
      - /dev/dri:/dev/dri
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:32400/identity >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
```

The HomeNode Traefik file provider defines the `plex.example.com` route in
`dynamic/plex.yaml` and targets `http://<homenode-lan-ip>:32400`. Plex is not
attached to `traefik_traefik`; Docker labels cannot route to it.

## Remote Access and Traffic Paths

- The router forwards WAN `32400/tcp` directly to the NAS for media playback.
- Plex Remote Access uses manual port mapping `32400`; relay is disabled and
  there is no per-stream upload cap. The published custom access URL is the WAN
  IP only (`http://<wan-ip>:32400`).
- Media traffic bypasses Pangolin/Newt: userspace WireGuard is limited to roughly
  1–10 Mbps. Pangolin still serves the web UI.
- `*.plex.direct` is intentionally unused because client DNS rebinding
  protection blocks it.
- `plex.example.com` is routed by local Traefik to the HomeNode LAN address;
  the Pangolin path remains useful for the web UI, not media transport.

## Deviations / Findings

### F-N-PLEX-1 — `:latest` image (`medium` / NM2, open)
Pin from <https://github.com/linuxserver/docker-plex/pkgs/container/plex>.
Plex releases every ~2 weeks and LSIO mirrors quickly; `:latest` rarely
breaks, but pinning is still safer.

### F-N-PLEX-2 — optional discovery ports are not router-forwarded (`medium` / NM9)
Plex can use additional ports for **local discovery** (GDM, DLNA, older smart TVs):

- `32400/tcp` — primary API
- `1900/udp` — DLNA / SSDP discovery
- `32410/udp`, `32412/udp`, `32413/udp`, `32414/udp` — GDM auto-discovery
- `32469/tcp` — DLNA server

With host networking there is no Compose port-publishing list. These optional
discovery ports are not exposed/forwarded on the router; WAN `32400/tcp` is the
only Plex port forwarded. In particular, `1900/udp` conflicts with Synology
DLNA, so do not forward it without resolving that conflict. Local discovery
behavior that depends on these ports may be unavailable across routed networks.

### F-N-PLEX-3 — healthcheck on `/identity` (`low` / NL2)
`/identity` is a stable endpoint. The response JSON includes
`machineIdentifier`, so it also doubles as a check that Plex didn't rotate
its machine ID (which invalidates all clients' auth). If it ever changes,
every linked device needs to re-pair.

## Remediation

### Fix F-N-PLEX-1 (open)

```yaml
    image: linuxserver/plex:1.41.x
```

## Operational Notes

- **Transcoding**: `/dev/dri` gives Plex access to the Intel iGPU. Requires
  Plex Pass for hardware transcoding to actually activate. Verify:
  Settings → Transcoder → "Use hardware acceleration when available" is
  checked; look for `hwaccel qsv` in the transcode logs when playing an
  HDR → SDR conversion.
- **Library path in container**: `/media/movies`, `/media/tv` etc. remain
  unchanged and continue to map to `/volume1/media/` on the host. Plex was not
  stopped or recreated during the shared `/data` migration; its existing
  `/media` mount is still valid because the physical layout did not change.
  Sonarr/Radarr hardlinks now pass through their shared `/data` namespace,
  while Plex sees the resulting files normally.
- **Measured remote throughput**: 82 Mbps for a single stream and about 92 Mbps
  aggregate across eight streams, against roughly 190 Mbps home upload. The
  remaining gap is attributed to the path to the CloudNode, not the stack.
