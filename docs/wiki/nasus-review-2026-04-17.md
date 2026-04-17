---
title: "NASUS Compose-File Review — 2026-04-17"
slug: nasus-review-2026-04-17
type: review
status: active
tags: ["homelab", "nasus", "review", "audit"]
aliases: ["nasus audit 2026-04-17"]
entities:
  primary: nasus-review-2026-04-17
  mentions: []
related: ["./README.md", "./system-overview.md"]
sources: ["host-configs/nasus/", "/volume1/docker/"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# NASUS Compose-File Review — 2026-04-17

Full audit of every `docker-compose.yml` under `/volume1/docker/` on NASUS
(`192.168.0.10`) against upstream references. Findings, severities, and
remediation follow the same conventions as the
[VPS review](./compose-review-2026-04-17.md).

- Reviewer: agent session 2026-04-17
- Scope: **16 compose files** — 14 service dirs plus `traefik/` and
  `hawser/`. `tailscale` runs out-of-band (Synology Package Center), not via
  compose. `jellyseerr` dir has orphaned data only (replaced by `seerr`).
- Method: each compose file fetched over SSH from NASUS and compared
  against upstream docs / reference compose / release notes.

Compose path convention on NASUS:

- Services: `/volume1/docker/config/<service>/docker-compose.yml`
- Traefik: `/volume1/docker/traefik/docker-compose.yml`
- Hawser: `/volume1/docker/hawser/docker-compose.yml`

All services join a single external Docker network **`traefik_traefik`** —
there is no network segmentation between the *arr suite, Plex, torrent
client, and the edge proxy.

---

## Repo-Sync Gap (meta finding)

`host-configs/nasus/` in this repo tracks only **8 of 16** services:

| Tracked in repo | Live on NASUS but NOT in repo |
|---|---|
| FlareSolverr, bazarr, plex, prowlarr, qbittorrent, radarr, sonarr, traefik | **cleanuparr, dashdot, hawser, newt, profilarr, qui, recyclarr, seerr** |

The 8 tracked files match NASUS byte-for-byte (no content drift). The problem
is coverage: changes to any of the 8 missing services are invisible to git
history. See finding **NM1** below.

`AGENTS.md` currently lists 11 services for NASUS; actual is 14 app services
+ traefik + hawser = 16. That inventory line in `AGENTS.md` needs updating.

---

## TL;DR Scoreboard

| Group | Services | Critical | High | Medium | Low |
|---|---|---|---|---|---|
| Edge/Tunnel | traefik, hawser, newt | 1 | 2 | 3 | 0 |
| *arr suite | sonarr, radarr, bazarr, prowlarr, profilarr, recyclarr | 0 | 1 | 4 | 2 |
| Torrent | qbittorrent, qui, flaresolverr, cleanuparr | 1 | 1 | 3 | 1 |
| Media | plex, seerr | 0 | 1 | 2 | 1 |
| Observability | dashdot | 0 | 1 | 1 | 0 |
| **Meta** | repo-sync | 0 | 1 | 0 | 0 |
| **total** | 16 | **2** | **7** | **13** | **4** |

---

## Critical Findings

### NC1. `traefik --api.insecure=true` with dashboard published
- **Service**: [traefik](./services-nasus/traefik.md)
- **File**: `/volume1/docker/traefik/docker-compose.yml`
- **Symptom**: Traefik runs with `--api.insecure=true` and the container
  publishes `9080:8080` on the NASUS host — meaning
  **`http://192.168.0.10:9080`** serves the full Traefik dashboard with no
  auth. Anyone on the home LAN (or reachable via the Olm tunnel — which
  includes the VPS) can read your routing table, cert expiry, entrypoints,
  middlewares, and provider credentials metadata.
- **Risk**: information disclosure; enables lateral-move planning by anyone
  on LAN or any compromised container on the `pangolin` VPS network.
- **Remediation**: either drop the port publish and access the dashboard
  via `docker exec` only, **or** switch to `--api.insecure=false` and
  expose the dashboard through Traefik itself with a BasicAuth /
  Pocket-ID middleware. See service page.

### NC2. `hawser` defaults `TOKEN` to empty and publishes docker socket proxy
- **Service**: [hawser](./services-nasus/hawser.md)
- **File**: `/volume1/docker/hawser/docker-compose.yml`
- **Symptom**: `TOKEN=${HAWSER_TOKEN:-}` with port `2375:2376` published on
  all interfaces. If `HAWSER_TOKEN` is not supplied by env at start (e.g.
  `.env` missing or renamed), Hawser starts with an **empty token**, and
  anyone who can reach NASUS on TCP 2375 gets full Docker API access — root
  equivalent on the host.
- **Risk**: critical. A misplaced `.env` rename is the difference between a
  hardened agent and an open docker socket on the LAN.
- **Remediation**: drop the `:-` default, require `${HAWSER_TOKEN:?}` so
  the service refuses to start without a token; optionally bind port to
  `127.0.0.1:2375` or a dedicated docker network instead of `0.0.0.0`;
  consider switching to Hawser "Edge mode" which removes the listen port
  entirely.

---

## High Findings

### NH1. Secrets hard-coded in `newt` compose
- **Service**: [newt](./services-nasus/newt.md)
- **File**: `/volume1/docker/config/newt/docker-compose.yml`
- `NEWT_ID` and `NEWT_SECRET` are both in the compose file. Adding this
  file to git (as `host-configs/nasus/` does for tracked files) leaks the
  tunnel credentials. Neither value should ever live outside `.env`.

### NH2. `traefik:latest` on NASUS
- Same pin-policy issue as VPS (H1 in VPS audit). NASUS Traefik has no
  CrowdSec, no access-log consumer, so a bad `latest` pull would be
  noticed even later (no logs to stream).

### NH3. `dashdot` on NASUS mounts the wrong path as host root
- **Service**: [dashdot](./services-nasus/dashdot.md)
- Volume is `/volume1/docker/config/dashdot:/mnt/host:ro` — that mounts
  dashdot's own **config directory** as the "host" it reports on. All
  disk / file-system / OS widgets show values for a ~empty folder, not for
  NASUS. The UI is essentially bogus.
- Upstream expects `/:/mnt/host:ro`.
- Also sets `privileged: true`, where on VPS we chose the safer
  `group_add: 986` pattern.

### NH4. `prowlarr:develop` (unstable channel)
- **Service**: [prowlarr](./services-nasus/prowlarr.md)
- Image is `linuxserver/prowlarr:develop` — the nightly/unstable branch.
  Unless you're actively tracking an in-progress fix, pin `:latest` (stable)
  or a concrete version.

### NH5. qBittorrent has no VPN sidecar
- **Service**: [qbittorrent](./services-nasus/qbittorrent.md)
- qBit joins the same Docker network as everything else and talks to the
  public internet via the host's default route. All torrent traffic exits
  on your ISP IP, not a VPN. Torrent-widget / webUI fine; outbound swarm
  traffic exposed.
- Not a compose bug, but a deliberate deployment choice worth documenting.

### NH6. `seerr` image comes from an unofficial fork
- **Service**: [seerr](./services-nasus/seerr.md)
- Image `ghcr.io/seerr-team/seerr:latest` is a fork of Jellyseerr. Confirm
  the fork is still maintained before the next update cycle; if upstream
  Jellyseerr has reabsorbed the changes, switch back.

### NM1. Repo-sync gap (meta)
- 8 of 16 NASUS compose files have no tracked copy in
  `host-configs/nasus/`. Listed in the repo-sync table above.
- Fix: copy the 8 missing files into `host-configs/nasus/<service>/docker-compose.yml`
  and write a short refresh script (e.g. `scripts/pull-nasus-configs.sh`) to
  rsync them periodically.

---

## Medium Findings

### NM2. Image-pin policy violations (most services)
`:latest` on: traefik, hawser, flaresolverr, bazarr, cleanuparr, dashdot,
plex, profilarr, qbittorrent, qui, radarr, recyclarr, seerr, sonarr. Only
`newt` is pinned (`1.11.0`). Same risk profile as VPS M10.

### NM3. Single flat docker network `traefik_traefik`
Every NASUS service joins the same external network. qBit, Plex, and Hawser
(which has a full Docker API socket) can reach each other freely. Segmenting
by purpose (arr / torrent / media / mgmt) is standard best practice.

### NM4. Several services have no healthcheck
- `cleanuparr`, `newt`, `profilarr`, `qui`, `recyclarr` — no healthcheck
  blocks. `stackctl`-style dashboards will show "running" regardless of
  whether the service is actually serving.

### NM5. `seerr` volume points to a legacy directory name
Volume is `/volume1/docker/config/jellyseerr:/app/config`. The **service**
got renamed to `seerr`, but the **data directory** kept the old name. This
is a footgun for backup scripts, rename-to-clean-up operators, and anyone
doing `find /volume1/docker/config -name 'docker-compose.yml'` expecting
the dir name to match the service name.

### NM6. `qui` router label calls it `flood`
Router `Host(\`flood.dennisb.xyz\`)` — legacy name from when Flood was the
tool. Mentally confusing; consider renaming router and the DNS record to
`qui.dennisb.xyz`.

### NM7. No access logs or CrowdSec on NASUS Traefik
VPS Traefik writes JSON access logs to `config/traefik/logs/access.log`
which CrowdSec ingests. NASUS Traefik has neither. All NASUS services are
behind Cloudflare Tunnel + Pangolin, but a local CrowdSec at the NASUS
Traefik would still catch LAN-side abuse.

### NM8. qBit webUI not password-separated from webUI port
Standard qBit defaults — the `WEBUI_PORT=8080` env is fine, but there is
no mention in compose of setting an admin password on first boot. Default
cred (`admin:adminadmin`) stays in play until changed in the UI.

### NM9. Plex port list incomplete for full local discovery
Only `32400:32400` exposed. If you ever need GDM/DLNA on LAN for local
players (Android TV/Chromecast), you'd also want 1900/udp, 32410-32414/udp,
32469/tcp. Currently not an issue since remote-access relay handles it,
but document the choice.

### NM10. Newt has no healthcheck
The tunnel agent exposes a status endpoint. Without a healthcheck, you
can't detect tunnel down except by hitting a downstream service.

### NM11. `seerr` has `ipv4_address` commented out with no explanation
Leaves an `#ipv4_address: 172.18.0.11` line hanging. Either re-enable with
an IPAM `ipam.config` block, or delete.

### NM12. Hawser mounts `docker.sock` read-write
Hawser intentionally needs write access (container creation, start/stop) —
but combined with NC2's auth weakness this is why NC2 is critical.
Separately tracking here for defense-in-depth review.

### NM13. `recyclarr` compose file missing trailing newline
Cosmetic — file ends with `external: true===END===` (no LF before our
`===END===` marker). Indicates the source file on NASUS has no trailing
newline. Some tools (git, POSIX `cat`) complain.

---

## Low Findings

- **NL1**. `qbittorrent` relies on default credentials until changed via UI.
- **NL2**. `plex` healthcheck hits `/identity` — fine, just note that if
  Plex Pass lapses or the server claims a new identity, the endpoint path
  can change over major versions.
- **NL3**. `flaresolverr` healthcheck hits `/` — upstream recommends
  `/v1` but ours works; cosmetic.
- **NL4**. Most services hard-code `TZ=Asia/Jerusalem` — fine, just flag
  for anyone moving NASUS or using it across DST boundaries.

---

## Remediation Plan (suggested order)

1. **NC2** — harden Hawser (token required, restrict listen interface).
2. **NC1** — secure or remove Traefik dashboard publish.
3. **NH1** — move `NEWT_*` into `.env`.
4. **NH3** — fix dashdot host mount.
5. **NM1** — sync 8 missing files into `host-configs/nasus/`.
6. **NH2 / NM2** — pin Traefik + remaining services.
7. **NH4** — switch prowlarr to a stable tag.
8. **NM4 / NM10** — add healthchecks.
9. **NM5 / NM6 / NM11 / NM13** — cosmetic renames & cleanup.
10. **NH5 / NM3** — decide on VPN sidecar for qBit and network segmentation.

Each step = one commit (NASUS-side change + updated `host-configs/nasus/`
copy + updated service wiki page).

---

## Rollback

NASUS changes are applied by SSH'ing to NASUS and editing the compose file
under `/volume1/docker/config/<service>/` then `docker compose -f ... up -d`.
Rollback:

```bash
ssh jesus@192.168.0.10 "cd /volume1/docker/config/<service> && \
  sudo cp docker-compose.yml.bak docker-compose.yml && \
  docker compose up -d"
```

Always make a `.bak` before editing a NASUS compose file. The repo copy
under `host-configs/nasus/` is *not* automatically redeployed — changes
flow **NASUS → repo**, not the other way around, until you build a sync
script.

---

## Upstream Sources Consulted

| Service | Source |
|---|---|
| traefik | <https://doc.traefik.io/traefik/operations/api/#insecure> |
| hawser | `https://github.com/finsys/hawser` + Dockhand deployment docs |
| newt | <https://github.com/fosrl/newt/releases> |
| sonarr/radarr/bazarr/prowlarr | <https://docs.linuxserver.io/images/> |
| profilarr | <https://github.com/santiagosayshey/Profilarr> |
| recyclarr | <https://recyclarr.dev/wiki/yaml/config-reference/> |
| qbittorrent | <https://docs.linuxserver.io/images/docker-qbittorrent/> |
| qui (autobrr) | <https://github.com/autobrr/qui> |
| flaresolverr | <https://github.com/FlareSolverr/FlareSolverr> |
| cleanuparr | <https://github.com/Cleanuparr/Cleanuparr> |
| plex | <https://docs.linuxserver.io/images/docker-plex/> |
| seerr | <https://github.com/seerr-team/seerr> (fork of Jellyseerr) |
| dashdot | <https://getdashdot.com/docs/installation/docker-compose> |

---

## Changelog

- 2026-04-17 — Added: initial NASUS audit. 2 critical / 7 high / 13 medium /
  4 low findings. 8 of 16 services found to be untracked in
  `host-configs/nasus/` (no content drift on the 8 that are tracked).
