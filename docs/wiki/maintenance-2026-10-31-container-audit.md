---
title: "Homelab maintenance 2026-10-31 — full container audit and remediation"
slug: homelab-maintenance-2026-10-31-container-audit
type: review
status: active
tags: ["homelab", "maintenance", "containers", "security", "traefik", "crowdsec", "qbit"]
aliases: ["container audit 2026-10-31", "stack remediation"]
entities:
  primary: homelab-maintenance-2026-10-31-container-audit
  mentions: []
related: ["./index.md", "./maintenance-2026-10-31.md", "./maintenance-2026-10-27.md", "./concepts/port-matrix.md", "./services/traefik.md", "./services-homenode/traefik.md", "./services/crowdsec.md"]
sources: ["docker ps on both hosts", "docker inspect", "upstream release APIs", "/conf/config.xml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# Homelab maintenance 2026-10-31 — full container audit and remediation

Audited all 31 running containers (15 CloudNode, 16 HomeNode), compared every
image with its upstream release, read the live Compose and static config, and
probed the public edge. Changes below were applied one at a time with a
verification step after each.

## What was actually exposed

Forcing the LAN-only hostnames to the public edge IP fails the TLS handshake,
so only the nine Pangolin resources are internet-reachable: `auth`, `base`,
`crowdsec`, `dash`, `dockhand`, `home`, `plex`, `request`, `traefik-logs`.
Everything else (`torrent`, `profilarr`, `sonarr`, `radarr`, `bazarr`,
`prowlarr`, `flaresolverr`, `adguard`, `nasus`) is reachable only on the LAN or
through the Olm/Newt tunnel.

## Changes — CloudNode

1. **Traefik `v3.7.16` → `v3.7.17`.** Docker socket remounted read-only.
2. **Traefik API hardened.** `api.insecure: false`; the dashboard is no longer
   served on an unauthenticated port. A dedicated `ping` entrypoint on `:8080`
   backs the container healthcheck, so health checks no longer require the API.
3. **Access log redaction.** `Authorization` is now `drop` instead of `keep`;
   the log had recorded bearer tokens verbatim. Verified the current log has no
   `Authorization` field.
4. **CrowdSec AppSec (WAF) enabled.** The collections were installed but nothing
   listened on `7422`. In CrowdSec 1.8.2 the listener is an *acquisition source*,
   not a top-level key: `source: appsec`, `listen_addr: 0.0.0.0:7422`,
   `appsec_config: crowdsecurity/appsec-default` in
   `config/crowdsec/acquis.d/appsec.yaml`. The Traefik plugin option
   `CrowdsecAppsecEnabled` is now `true`.
5. **Homarr `v2.8.2` → `v2.10.1`** with a pre-upgrade `appdata` archive
   (`~/backups/homarr-appdata-20261031-202355.tgz`). Migrations completed.
6. **CrowdSec Web UI `2026.10.10` → `2026.10.13`.**
7. **Pocket-ID `ALLOW_DOWNGRADE=true` removed** — the flag let an older image
   start against a newer database.
8. **Traefik log dashboard pinned `3.1.1`.**

## Changes — HomeNode

1. **Profilarr moved to the maintained fork.** `santiagosayshey/profilarr:latest`
   (June build, label `version=beta`) → `ghcr.io/dictionarry-hub/profilarr:2.3.1`.
   The old build is inside the `GHSA-xhjf-xjhw-69mh` range
   (`>=2.0.0, <2.3.0`): a crafted SQLite `ATTACH` can read the app database and
   the API keys in it. Database and Compose backed up first.
2. **qBittorrent publishes `6881/tcp` and `6881/udp`**, plus one OPNsense WAN
   forward to the NAS. Previously the ports were only exposed, with no UPnP and
   no forward, so the client was outbound-only.
3. **Newt secret moved out of Compose.** The literal in
   `/volume1/docker/config/newt/docker-compose.yml` did **not** match the value
   the running container used — it was a stale credential. The live value was
   read from the container, written to `.env` (`0600`), and Compose now uses
   `${NEWT_ID}` / `${NEWT_SECRET}`. The tunnel was verified after recreation.
4. **arr-mcp `1.44.5` → `1.50.0`** and the contradicting
   `ARR_MCP_VERSION=1.21.2` override removed.
5. **Recyclarr `8.8.0` → `8.8.1`.**
6. **Hawser `latest` → `0.2.53`**; its `.env` permission tightened to `0600`.
7. **Prowlarr `:develop` → `2.7.0`** — nightly channel replaced with a stable pin.
8. **Seerr `LOG_LEVEL=debug` → `info`.**
9. **dashdot no longer runs `privileged`**; it keeps the read-only host mount and
   gains `no-new-privileges`.
10. **HomeNode Traefik `latest` → `3.7.17`**, `api.insecure` removed, dedicated
    `ping` entrypoint on `:8082` backing the healthcheck.

## Router

Two NAT rules were added on the WAN interface (`opt5`, PPPoE) for
`tcp/6881` and `udp/6881` to the NAS, each with `pass=rule` so OPNsense creates
the linked WAN filter rule. They load as:

```
nat on pppoe0 inet proto tcp from (pppoe0:network) to 192.168.0.10 port = 6881 -> ...
pass in quick on pppoe0 ... proto tcp from any to 192.168.0.10 port = 6881 ...
pass in quick on pppoe0 ... proto udp from any to 192.168.0.10 port = 6881 ...
```

Config backup: `/root/config.xml.bak-qbit-20261031-203424`.

## Verified

| Check | Result |
|---|---|
| CloudNode containers | all healthy after changes |
| HomeNode containers | all up; all upgraded ones healthy |
| Public edge (9 resources) | 401/200/307 as before, no 5xx |
| LAN-only hostnames via tunnel | 200/302/303/401 as before |
| AppSec listener | `Appsec listening on 0.0.0.0:7422` |
| AppSec block | virtual-patch payload → `403`, normal request → `200` |
| AppSec false positives | none across the nine public sites |
| Traefik API (both hosts) | connection refused on the old API port |
| Traefik ping | `OK` on both hosts |
| qBittorrent `6881/tcp` from internet | open |
| Plex `32400/tcp` from internet | open (control) |
| Newt tunnel | WebSocket established, UDP relay flowing |
| Homarr migrations | `Migration complete`, local 200 |
| Profilarr | `Server ready`, `version 2.3.1`, healthy |

## Decisions

- **AppSec is in-band, `ban` remediation is per-request only.** The engine has
  no generic XSS/SQLi rule set: `appsec-default` is virtual patching plus a few
  product-specific rules. That is why a hand-written XSS payload is *not*
  blocked, while a known CVE path is. Add `crowdsecurity/appsec-generic-rules`
  only if you accept a higher false-positive rate.
- **Trusted client IPs bypass AppSec.** Requests whose resolved client IP is in
  `ClientTrustedIPs` skip the WAF. The VPS address is trusted for health probes;
  Cloudflare-forwarded clients are not, and `ForwardedHeadersTrustedIPs` stays
  scoped to Cloudflare plus RFC1918.
- **No `no-new-privileges` sweep** on the 14 remaining NAS containers: none of
  them add capabilities, so the flag would be cosmetic churn.
- **Linuxserver `:latest` tags left alone.** Each app draws from its own stable
  branch; pinning them individually adds update toil without a safety gain.
- **FlareSolverr kept.** It is effectively legacy in 2026 (Byparr is the modern
  drop-in) but the current image is the latest release and still works; the
  public Traefik label is inert because the hostname is not a Pangolin resource.
- **dashdot storage widget stays empty on the NAS.** The container mounts the
  DSM root filesystem, which does not expose `/volume1`; this is a Synology
  limitation, unchanged by dropping `privileged`.

## Behaviour notes

- Profilarr now answers `303` on `/` (redirect to login) instead of `200`.
- AppSec adds a request round-trip to CrowdSec on `7422`. The plugin timeout is
  10 s; `CrowdsecAppsecUnreachableBlock: true` means a dead AppSec fails closed.
  Monitor CrowdSec health if you change that.
- `qBittorrent` was already correct on CSRF, host-header validation, and
  reverse-proxy support. The only gap was connectability.

## Rollback

- Compose/config backups: `/volume1/docker/config/.audit-backups/*.20261031` on
  the NAS, `config/traefik/traefik_config.yml.bak-20261031-audit` and
  `config/crowdsec/config.yaml.bak-20261031-audit` on the CloudNode.
- Homarr data: `~/backups/homarr-appdata-20261031-202355.tgz`.
- Router: `/root/config.xml.bak-qbit-20261031-203424`.
- AppSec: delete `config/crowdsec/acquis.d/appsec.yaml` and set
  `CrowdsecAppsecEnabled: false`.

## Follow-up 2026-11-01 — qBittorrent seeding saturated the HDD array

After the 6881/tcp+udp publication and router forward landed, qBittorrent became
inbound-connectable and served ~25 MB/s upload. Serving 274 torrents off the
4-disk RAID5 produced 1500–2000 random reads/s: `md1` and `dm-2` sat at 100 %
util, iowait 77 %, load average 20–30 with one runnable process.

Docker health checks for `bazarr` and `radarr` (10 s timeout, 3 retries) timed
out during those stalls and Docker reported them unhealthy. Neither container
restarted; the alerts were transient and the apps were fine.

Applied live through the WebUI API (`/api/v2/app/setPreferences`):

| Setting | Before | After |
| --- | --- | --- |
| `queueing_enabled` | false | true |
| `max_active_uploads` | 100 | 15 |
| `max_active_torrents` | 100 | 60 |
| `up_limit` | 0 (unlimited) | 10 MiB/s |

Result: `md1` util 40 %, `dm-2` 45–55 %, `some avg10` I/O pressure 98 % → 22 %,
load average 30 → 4. Upload settled at the 10 MiB/s cap.

- Persisted by qBittorrent in `qBittorrent.conf` as
  `Session\QueueingSystemEnabled=true`, `Session\MaxActiveUploads=15`,
  `Session\MaxActiveTorrents=60`, `Session\GlobalUPSpeedLimit=10240`.
- Rollback: POST `{"up_limit":0,"queueing_enabled":false}` to the same endpoint.
- TorrentLeech ratio is unaffected in practice: seeding time keeps accruing and
  10 MiB/s is still far above the line needed for 1:1.
- Known noise, not fixed: at startup qBittorrent tries to move torrents from
  `/downloads/...` to `/data/downloads/...`. Both mounts resolve to the same
  host directory (`/volume1/media`), so every move fails with `Invalid argument`.
  Harmless and pre-existing (36 occurrences in the previous log too).

### Rollback (this follow-up)

- No files changed outside qBittorrent's own config; the API settings above are
  the only state.

### Follow-up 2026-11-01 — night boost and 30-day cleanup

- **Night window**: qBittorrent's bandwidth scheduler runs 01:00–07:00 every day with
  alternate limits of 20 MiB/s up/down; the rest of the day stays at 10 MiB/s.
  Measured at 20 MiB/s: `md1` 45–53 % util, I/O pressure `avg10` ~25 %, load 3.7 —
  acceptable. The 15-active-upload queue limit, not the byte cap, is what keeps the
  array responsive.
- In qBittorrent 5.3 the scheduler day field is a single-choice enum exposed as
  `1=Weekdays`, `2=Weekend`, `3..9=Mon..Sun`. The int API rejects `127`; "every day"
  only round-trips through the preference string (`Scheduler\days=EveryDay`), which is
  what is set in `qBittorrent.conf`.
- **30-day cleanup**: `max_seeding_time=43200`, `max_inactive_seeding_time=43200`,
  action `RemoveWithContent`. Enabling it dropped the torrent list from 274 to 85 and
  shrank `/volume1/media/downloads` from ~1.4 TB to 910 GB (only ~500 GB physically
  freed; the rest were hardlinks to seeded library copies). Library sizes were
  unchanged (`movies` 824 GB, `tv` 3.3 TB) and all remaining torrents resolve inside
  `/downloads` or `/data/downloads`.
- 24 torrents survived the first pass because they carried a per-torrent
  `seeding_time_limit=-1` (unlimited), which overrides the global limit. All torrents
  were normalised to `-2` (use global) via `POST /api/v2/torrents/setShareLimits`,
  which removed them. Any torrent that arrives with an explicit `-1` will ignore the
  30-day rule.
- Side finding: the alternate speed mode had latched on with the stock 10 KiB/s alt
  limit, which had silently reduced upload to ~1 KB/s. Alt limits are now 20 MiB/s.
