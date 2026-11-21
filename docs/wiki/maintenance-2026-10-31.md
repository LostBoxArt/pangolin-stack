---
title: "Homelab maintenance 2026-10-31 — Plex remote streaming"
slug: homelab-maintenance-2026-10-31
type: review
status: active
tags: ["homelab", "maintenance", "plex", "firewall", "network"]
aliases: ["plex host networking", "plex remote access 32400"]
entities:
  primary: homelab-maintenance-2026-10-31
  mentions: []
related: ["./index.md", "./services-homenode/plex.md", "./concepts/port-matrix.md", "./maintenance-2026-10-27.md"]
sources: ["/volume1/docker/config/plex/docker-compose.yml", "/volume1/docker/traefik/dynamic/plex.yaml", "/conf/config.xml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# Homelab maintenance 2026-10-31 — Plex remote streaming

Verified live changes on the HomeNode NAS (`nasus`) and the OPNsense router.
Repository addresses and hostnames stay sanitized.

## Why

Remote Plex playback was capped at 74–78 Mbps and every remote client appeared
as `172.18.0.1` in the server log. Docker bridge networking puts the userland
proxy in front of Plex, which masks client IPs and limits throughput (documented
by linuxserver/Plex and Plex's own network guide). The tunnel path through
Pangolin/Newt is userspace WireGuard and is limited to roughly 1–10 Mbps, so it
must never carry media traffic.

## Changes

1. **Plex runs with host networking.** `network_mode: host`, no `ports:` block,
   no Traefik labels. Plex binds `32400` directly on the NAS host, so clients
   reach it without the Docker proxy.
2. **Plex database moved to the NVMe SSD.** `Plug-in Support/Databases` is now a
   bind mount to `/volume2/plex-db` (394 MB copied, `uid/gid 1000`, container
   confirms `/dev/md2`). The old copy on `/volume1` is kept for rollback. The
   server log had shown `SLOW QUERY: 900 ms`.
3. **Traefik route moved to the file provider.** `dynamic/plex.yaml` serves
   `plex.example.com` from `http://<homenode-lan-ip>:32400`. Docker labels were
   removed because the container is no longer on the `traefik_traefik` network.
4. **Router NAT added.** WAN `TCP 32400` is forwarded to the NAS `32400` with a
   linked filter pass rule. This is the only new inbound port.
5. **Plex remote access set to manual.** Manual port mapping `32400`, relay
   disabled, `WanPerStreamMaxUploadRate=0`, server published to Plex Online.
   Published custom access URL is `http://<wan-ip>:32400` only; the tunnel URL
   and `plex.direct` URLs were removed.

## Decisions

- Media bypasses Pangolin entirely. Pangolin/Newt stays in place for the web UI
  and non-media services.
- `plex.example.com` keeps pointing at the CloudNode/Pangolin path for the web
  UI. A direct home-HTTPS variant on 443 was considered and rejected.
- `*.plex.direct` stays unused: the phone's DNS resolver applies rebinding
  protection and blocks it, which broke app connectivity when it was published.

## Verified

| Check | Result |
|---|---|
| Plex container | healthy, no errors after recreation |
| Local Plex `/identity` | 200 |
| `plex.example.com` via local Traefik | 200 |
| `plex.example.com` via Pangolin | 200 |
| Direct WAN `32400` `/identity` | 200, mapping state `Mapped` |
| Client IP in server log | real remote IP, no `172.18.0.1` |
| Throughput, single remote stream | 82 Mbps (was 74–78) |
| Throughput, 8 parallel streams | ~92 Mbps aggregate |
| Home upload to Cloudflare | ~190 Mbps |
| Plex database filesystem in container | `/dev/md2` (SSD) |

The remaining gap between ~92 Mbps and the ~190 Mbps home upload is the path to
the CloudNode, not the stack.

## Behaviour notes

- Hi10P sources always transcode on iOS; a 1080p 10 Mbps cap forces an 8-bit
  H.264 transcode (~8 Mbps), which is expected.
- Direct play versus transcode is visible in the Plex dashboard and in the
  server log (`directPlay=1`, `relayed=0`).
- A stuck "buffering" client was a dead cached connection, not a server fault;
  restarting the app cleared it.

## Rollback

- Compose backup: `/volume1/docker/config/plex/docker-compose.yml.bak-20261031-195046`.
- Traefik dynamic files backed up under `/volume1/docker/backups/`.
- Old database copy remains on `/volume1` until a few clean days have passed.
- Router config backup: `/root/config.xml.bak-plex-20261031-192251`.
