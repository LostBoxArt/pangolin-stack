---
title: "plex"
slug: nasus-plex
type: service
status: active
tags: ["homelab", "nasus", "service", "plex"]
aliases: ["plex"]
entities:
  primary: nasus-plex
  mentions: []
related: ["./README.md", "./nasus-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/plex/docker-compose.yml", "host-configs/nasus/plex/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# plex

Plex Media Server. Serves `plex.dennisb.xyz` (Traefik-routed) and direct
LAN clients. Hardware transcoding enabled via `/dev/dri`.

- **Image**: `linuxserver/plex:latest` ⚠️
- **Compose file**: `/volume1/docker/config/plex/docker-compose.yml`
- **Tracked copy**: `host-configs/nasus/plex/docker-compose.yml` ✓
- **Port**: `32400:32400` (required for remote-access claim)
- **Router**: `plex.dennisb.xyz`
- **Volumes**:
  - `/volume1/docker/config/plex:/config`
  - `/volume1/media:/media`
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
    environment:
      - PUID=1000
      - PGID=1000
      - TZ=Asia/Jerusalem
    ports:
      - "32400:32400"
    volumes:
      - /volume1/docker/config/plex:/config
      - /volume1/media:/media
    devices:
      - /dev/dri:/dev/dri
    healthcheck:
      test: ["CMD-SHELL", "curl -fsS http://127.0.0.1:32400/identity >/dev/null || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s
    networks: [traefik_traefik]
    labels:
      - "traefik.http.routers.plex.rule=Host(`plex.dennisb.xyz`)"
      - "traefik.http.services.plex.loadbalancer.server.port=32400"
      - "traefik.http.services.plex.loadbalancer.server.scheme=http"
```

## Deviations / Findings

### F-N-PLEX-1 — `:latest` image (`medium` / NM2)
Pin from <https://github.com/linuxserver/docker-plex/pkgs/container/plex>.
Plex releases every ~2 weeks and LSIO mirrors quickly; `:latest` rarely
breaks, but pinning is still safer.

### F-N-PLEX-2 — only `32400/tcp` exposed (`medium` / NM9)
For **full local discovery** (GDM, DLNA, older smart TVs) Plex wants:

- `32400/tcp` — primary API (we have this)
- `1900/udp` — DLNA / SSDP discovery
- `32410/udp`, `32412/udp`, `32413/udp`, `32414/udp` — GDM auto-discovery
- `32469/tcp` — DLNA server

We skip all of these. Remote access via Plex Relay and direct via
`plex.dennisb.xyz` both still work. Only the "cast from a Smart TV by
double-pressing Plex in the nav bar" flow breaks. Acceptable trade-off if
you only use Plex apps on PC / phone / Android TV.

To add them back:

```yaml
    ports:
      - "32400:32400"
      - "1900:1900/udp"
      - "32410:32410/udp"
      - "32412:32412/udp"
      - "32413:32413/udp"
      - "32414:32414/udp"
      - "32469:32469/tcp"
```

Note `1900/udp` frequently conflicts with Synology's DLNA service — kill
it in Package Center first.

### F-N-PLEX-3 — healthcheck on `/identity` (`low` / NL2)
`/identity` is a stable endpoint. The response JSON includes
`machineIdentifier`, so it also doubles as a check that Plex didn't rotate
its machine ID (which invalidates all clients' auth). If it ever changes,
every linked device needs to re-pair.

## Remediation

### Fix F-N-PLEX-1

```yaml
    image: linuxserver/plex:1.41.x
```

## Operational Notes

- **Transcoding**: `/dev/dri` gives Plex access to the Intel iGPU. Requires
  Plex Pass for hardware transcoding to actually activate. Verify:
  Settings → Transcoder → "Use hardware acceleration when available" is
  checked; look for `hwaccel qsv` in the transcode logs when playing an
  HDR → SDR conversion.
- **Library path in container**: `/media/movies`, `/media/tv` etc. match
  the subdirs under `/volume1/media/` on the host. Must match whatever
  Radarr / Sonarr use for hardlinks to work (they do).
- **Remote access via Pangolin**: `plex.dennisb.xyz` → VPS Traefik → Olm
  tunnel → NASUS Traefik → Plex. Two hops of reverse proxy, but works.
  Plex mobile apps that don't accept the cert chain fall back to Plex
  Relay (32400 on plex.tv).
