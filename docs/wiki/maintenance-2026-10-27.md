---
title: "Homelab maintenance 2026-10-27"
slug: homelab-maintenance-2026-10-27
type: review
status: active
tags: ["homelab", "maintenance", "security", "backup"]
aliases: ["deep sweep follow-up"]
entities:
  primary: homelab-maintenance-2026-10-27
  mentions: []
related: ["./index.md", "./services/olm.md", "./runbooks/monitoring-and-arr-mcp.md", "./concepts/port-matrix.md"]
sources: ["stacks/", "host-configs/", "backup.sh", "scripts/ensure-traefik-netns.sh"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-10-27
---
# Homelab maintenance 2026-10-27

This records verified live changes following the deep-sweep report. Repository
example domains and addresses remain examples; they are not a deployment plan.
Existing Bazarr and documentation edits were preserved. No broad service-version
upgrade or storage migration was included.

Ponytail `5.3.2` and I-have-ADHD `0.4.1` were installed as native Codex plugins
at user scope. Global `~/.codex/AGENTS.md` preferences activate ADHD defaults
for every response and Ponytail full for technical work, including when hooks
are unavailable. Fresh skill-catalog checks in this repository and an unrelated
directory confirmed both are enabled; installation is not project-specific.

## Observed deployment

| Component | Verified live version or role |
|---|---|
| Pangolin / Gerbil / CloudNode Traefik | 1.25.3 / 1.5.2 / v3.7.16 |
| CrowdSec Web UI / Pocket ID / Homarr | 2026.10.10 / v2.19.1 / v2.8.2 |
| Newt / Olm | 1.19.0 / 1.9.1 |
| arr-mcp / Recyclarr / Seerr | 1.44.5 / 8.8.0 / v3.5.1 |
| qbit-proxy / qBittorrent | Node 24.22.1 / qBittorrent 5.3.0 |

CloudNode has six Pangolin stacks plus Hermes-managed SearXNG/Valkey. NASUS has
15 running containers after FileFlows removal. Termix, qui, cleanuparr, and
CloudNode AdGuard are absent from the live inventory; historical pages/templates
must not be mistaken for active services. NAS AdGuard routing is separately
active and was retained.

Ordinary CloudNode-to-NAS traffic currently prefers Tailscale policy table 52.
Olm is a separate working path: a forced-interface Hawser health request returned
200 after both Olm and Newt credential rotations. A main-table route alone does
not establish which path an ordinary request used. Routing priority was preserved.

Bulk backup testing exposed a nested path: Tailscale's selected router endpoint
was itself reached through Olm. The default SSH upload showed about 18% TCP
retransmission and a congestion window of three packets. An identical connected
1 MiB upload took 31.294 seconds on that path and 0.614 seconds through a socket
explicitly bound to Olm (setup measured separately). Backups use that explicit
connection rather than changing system routing or interface MTUs. Large-copy
integrity and completion are separate acceptance checks below.

## Applied changes and evidence

| Area | Change | Verification |
|---|---|---|
| FileFlows retirement | Removed both NAS containers, dedicated images/network/config/test data, dynamic route, public resource, stale update record, deployment copies, watchdog entries, vault item, and active references | Public endpoint 404; no active Homarr/Dockhand integration, Git deployment or dedicated Cloudflare DNS record; shared media and shared icon/certificate catalogs preserved |
| Existing secret files | Recovery-kit PDF and retained user Olm config restricted to 0600 | Contents unchanged; private rollback evidence retained |
| Hermes service helper | Bootstrap import fixes the intended Python environment | Six authenticated media checks, both Dockhand environments, MCP tool listing |
| qbit-proxy | Strict upstream TLS, request deadline, stream failure handling, version-body healthcheck | Nine implementation tests; API access from Homarr network; current cookies and 204 responses covered |
| CrowdSec | Restored missing SSH hub components and added Linux collection | Config validation, healthy LAPI, authenticated firewall/Traefik bouncer requests; unrelated YAML/custom rules unchanged |
| CloudNode host ports / Homarr | Seven internal publications bound to loopback; Homarr target changed through API to homarr:7575 | Native probes and protected public boundaries retained |
| Gerbil/Traefik coupling | Startup/core control commands run an idempotent namespace guard | Fixtures cover replacement/restart/stopped/healthy/repeat; production check was a no-op |
| GeoBlock | Cache increased from 25 to 2000 after 335 distinct client hosts in 4746 recent requests | Public probes pass; country policy and fail-closed behavior preserved |
| Olm | Root-only config, restrictive umask, no secret in argv; secret rotated through API | Old secret fails/new secret passes native Argon2; identity preserved; restart and forced Olm path pass; timer resumed |
| Newt | Removed live secret from tracked wiki; canonical Git compose uses private Dockhand variables; secret rotated | Same image/networks, successful supported Git deployment, same site online, old secret invalid, forced Olm path passes |
| arr-mcp tunnel | Foreground SSH under systemd; retired cron/PID owners | Enabled/active, loopback-only listener, authenticated 39-tool listing after maintenance |
| Monitoring | Five-minute watchdog, batched NAS inspection, 403 failures, forced Olm probe, bounded local diagnostics | 38 checks healthy; 15 isolated tests; no test notifications sent |
| Release watcher | Resumed as daily local-only metadata checker, removed automatic upgrade/message behavior | Script and Hermes scheduler checks pass; historical locks/admissions retained |
| NAS management ports | Hawser restricted to NAS LAN interface; Traefik dashboard host publication removed | Hawser auth retained; dashboard unavailable through both routed paths, available via SSH forward |
| NAS routes / dashboard | Removed duplicate Seerr file route, retained active AdGuard route; corrected Dashdot host mount | Request redirect, AdGuard redirect, Dashdot metrics and public route retain expected behavior |
| Source reconciliation | Added sanitized NAS copies for missing services and current host units/scripts | Parsed compose snapshots; Newt source/runtime comparison; no populated credentials committed |
| Backup transport | Use a per-connection SSH socket bound to Olm to avoid the measured nested path | Connected 1 MiB comparison about 51 times faster; strict SSH host-key checks retained; global routing/MTUs preserved |

Newt source fix: [homelab-docker commit 36ddb834](https://github.com/LostBoxArt/homelab-docker/commit/36ddb834793c5165138c828010e7475b093dadad).
Git history and private old backups may contain previous credentials; rotation
revokes those values. Shared Git history was not rewritten.

## Backup and restore verification

The final CloudNode archive is `pangolin-backup_20261027_134620.tar.gz`,
455,954,239 bytes, mode `0600`, SHA-256
`c8b82f80e7c4e7e8b16437797e23ed5ca702bce95b21cc9749e74452ce65c43d`.
All 16 previous archives were retained during maintenance.

| Proof | Verified result |
|---|---|
| VPS to NAS | Encrypted snapshot `009bfcd3ea7cd69c65aa602f8c79c62d1a7081f426c8786d8e2d3a0f1cb487e2`; full repository read passed; the independently held Mac key recovered the entire archive with the exact SHA-256 above |
| NAS snapshot | `c8f7ec4ebdaec7e77770234bbabface144bddff2b4f7e9dcfc476acd8a85f27d`; 22,819 regular files / 3,533,248,563 bytes; 10 primary databases passed integrity checks, including two Plex native checks |
| NAS to VPS | Separate encrypted snapshot `fc056884db850b2171b4434ab52399fd17ecf58adc5b9e1be5b1472af9a2e35d`; full repository read and complete fresh-tree restore passed; manifest SHA-256 matched, including recovery with the independent Mac key |
| VPS application rehearsal | Eleven isolated clones from the final archive; persistent applications and log dashboards passed native checks. qbit-proxy's bounded upstream failure was expected because the internal-only network cannot reach the real NAS |
| Credential consistency | The final restored Pangolin database natively verified the archived Olm secret and independently recovered current Newt secret; restored CrowdSec LAPI credentials were valid |
| NAS application rehearsal | Sonarr, Radarr, Prowlarr, Bazarr, Seerr and Plex passed cold-start/local native API checks and 16 original durable table counts. Restored API keys authenticated; Plex identity and library-section count matched |
| Recovery safeguards | Root-only restore, validated inputs before shutdown, confirmed quiescence, correct ownership, WAL/SHM/hot-journal handling, no self-downgrade of the recovery tool, and exact-image no-pull recovery instructions |
| Regression checks | 14 backup cases, 7 restore tests, 5 retention tests, 7 offsite tests, 8 NAS backup tests, 4 relay tests, 15 watchdog tests and 9 proxy tests passed; separate root-container ownership/restore and isolated Docker namespace checks passed |

The Seerr status probe uses its documented `checkUpdateAvailable=false` option;
the ordinary status endpoint waits for GitHub, which is intentionally unreachable
in the rehearsal. Bazarr uses a local authenticated endpoint because its full
status endpoint queries Sonarr and Radarr. These are explicit isolation limits,
not changes to production configuration. No media downloads, playback,
transcoding, production notifications, live disaster restore, or external service
workflows were exercised. Databases are independently consistent; they are not
one cross-application transaction.

The current seven-day local retention policy now requires fresh validated
archives and preserves at least two validated generations. Encrypted repository
pruning is not automated. Password copies are independently escrowed privately
on the maintenance Mac. See [recovery commands](./runbooks/backup-recovery.md)
and [NAS recovery scope](./runbooks/backup-nasus-config.md).

Both real user-service workflows finished with `Result=success` and
`ExecMainStatus=0`, including the weekly full-data checks. Both timers are
enabled and active, and `Linger=yes` keeps them operating after logout.
At verification their next runs were 2026-10-28 03:43:36 and 2026-10-31 05:00:42
in Asia/Jerusalem, including randomized delay. The configured schedules are
daily 03:40 and Saturday 05:00, after the existing 03:00 local archive.

The final weekly workflow published NAS snapshot
`c3a8d87ea7dc7191b92bb11c4a56d9843524bb7fec91e0cebb763433c6dfd25e`,
with an identical separate-host tree at VPS snapshot
`e70c3b8ccd01d3fc5c50c3639b177749f196a1ae1952fac39bbf715639e4aa40`.
The latest VPS-on-NAS snapshot is
`49ed8521f7b8a1d98f45fcdd5d9cdede4b1dbc71392f9ff31a873d615b2b6631`;
its tree is identical to the independently recovered `009bfcd3` snapshot above.
Final full-data checks passed.

Final production checks confirmed the 13 CloudNode stack services running,
healthy where a native healthcheck exists, and Olm, its watchdog, the MCP tunnel
and firewall bouncer active. All 15 NAS production services were running and
healthy where defined. Authenticated MCP exposed 39 tools and all 38 watchdog
checks passed. There were zero owned application rehearsals, networks or backup
helpers remaining. The four owned plaintext restore trees were removed after
verification; encrypted repositories, all 17 private local archives, evidence and
independent recovery keys were retained.

## Recommendations that were not safe or justified as written

| Report recommendation | Disposition |
|---|---|
| Move media configs/downloads to NVMe, or move FileFlows temp | FileFlows is retired. The NVMe volume is a single-device array, unlike the mirrored system array. Other migrations need measured workload latency and confirmed durability/rollback; free capacity alone does not justify moving databases or downloads |
| Set swappiness to 10 because swap is allocated | Not applied. A ten-second sample showed about 12.4 GiB available RAM, zero current memory pressure, and unchanged swap-in/out counters. Existing swapped pages do not prove active swap thrashing |
| Automatically restart Docker on a Newt DNS log substring or rewrite the vendor Docker wrapper | Not applied. This can interrupt all NAS services or overwrite vendor-managed behavior; diagnose and use the recovery procedure instead |
| Delete NAS Dashdot because the public hostname routes to VPS | Incorrect premise: NAS has an active LAN router. Kept the service and fixed its host mount. ADM lacks /etc/os-release, so its OS widget still reports container Alpine |
| Enable Hawser Edge immediately | Current public Dockhand SSO returns 401 for the WSS path. Standard mode remains authenticated; its LAN binding reduces interfaces but does not isolate LAN callers |
| Allow unknown countries through GeoBlock | Not applied. That would change the security policy. A larger cache addresses observed cache churn without relaxing country filtering |
| Delete bouncers solely from last_pull age | Not sufficient evidence: live-query and stream modes have different metrics. Verify actual credential consumers before revocation |
| Replace WAN-IP discovery with an arbitrary Gerbil peer endpoint | Requires binding the endpoint to the intended Newt peer and proving equivalent whitelist semantics; an arbitrary endpoint can whitelist the wrong address |
| Clear Hermes locks/admissions and automatically upgrade Hermes | Recovered the supported job lifecycle and retained audit state. No unreviewed daemon upgrade or automatic upgrade prompt |
| Prune old Hermes backups or orphan Termix data immediately | Retained rollback data. Hermes backups use about 1.3 GiB; the unused Termix volume is nonempty (about 19 MiB). No emergency space pressure or verified replacement recovery set justifies deletion |
| Remove NAS adguard.yaml as stale | Active router backend still returns its expected redirect; retained |
| Add proxy SNI that was supposedly missing | It already existed. Retained it and fixed the actual TLS/deadline/healthcheck gaps |

These are reviewed dispositions, not queued automatic changes.

## Reproduce source checks

Run from the repository root:

```bash
bash -n backup.sh stackctl.sh startup.sh scripts/ensure-traefik-netns.sh
python3 tests/test_backup.py
python3 tests/test_backup_restore.py
python3 tests/test_backup_prune.py
python3 tests/test_nasus_backup.py
python3 tests/test_offsite_backup.py
python3 tests/test_ssh_bind_olm.py
python3 host-configs/cloudnode/hermes/scripts/test_watchdog.py
node --test qbit-proxy/index.test.js
python3 scripts/wiki_lint.py
git diff --check
```

The namespace integration test requires Docker Compose and a cached
`alpine:latest` image. Run on a Docker-enabled host (it passed on CloudNode):

```bash
python3 tests/test_core_netns.py
```

It creates a uniquely named network-disabled fixture project, exercises its
namespace replacement/restart behavior, and removes the fixture afterward.
It never recreates production Gerbil/Traefik.

Live checks and restoration commands are in the linked service/runbook pages.
Availability checks, authenticated API checks, and native Docker health are
reported separately. Full browser rendering of Homarr's widget was not exercised.
A finite maintenance test cannot guarantee every future workload or external
provider failure; the verified scope and recovery data are recorded explicitly.

## Primary documentation used

- [SQLite online backup](https://www.sqlite.org/backup.html) and [restic](https://restic.readthedocs.io/en/stable/)
- [Pangolin machine credentials](https://docs.pangolin.net/manage/clients/machine-clients) and [site credentials](https://docs.pangolin.net/manage/sites/credentials)
- [Olm 1.9.1 config loading](https://github.com/fosrl/olm/blob/1.9.1/config.go)
- [Docker published ports](https://docs.docker.com/engine/network/port-publishing/) and [volume lifecycle](https://docs.docker.com/engine/storage/volumes/)
- [Linux swappiness](https://docs.kernel.org/admin-guide/sysctl/vm.html#swappiness)

Additional version-specific sources are linked from the affected service pages.
