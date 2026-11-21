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

## Functional tooling follow-up

A separate authenticated functional audit on 2026-10-27 went beyond the earlier
container/HTTP checks and MCP tool listing. No production configuration was
changed. Searches below were interactive reads; no release was grabbed, scan
started, profile synced, subtitle downloaded, or media changed.

### Arr APIs and integrations

Forty-six supported native API reads passed across Sonarr, Radarr, Prowlarr,
Bazarr, Seerr and Plex. Two additional reads from Prowlarr's own network namespace
used its actual stored URLs and credentials and reached Sonarr/Radarr successfully.
Prowlarr masks secrets in API responses; those placeholders must not be used as
credentials when testing links. Unsupported internal status URLs were excluded
from the supported API count.

| Functional path | Result |
|---|---|
| Sonarr / Radarr | Library, existing-item details, queue, root folders, configured qBittorrent client and four enabled Torznab indexers each were readable; roots reported accessible with free space |
| Prowlarr / Seerr / Bazarr / Plex | Prowlarr had five enabled indexers with no blocked status and two working stored Arr links; Seerr read both linked Arr profile/root-folder lists; Bazarr saw live Arr versions; Plex library and metadata reads passed |
| Recyclarr | Daily runs succeeded October 25–27; configured Arr quality-profile/custom-format API reads passed |
| Homarr → qbit-proxy → qBittorrent | Used Homarr's actual configured URL from its container; version, transfer and torrent reads passed, including three active uploads among 256 torrents |
| FlareSolverr / Profilarr native API | FlareSolverr readiness and `sessions.list` passed from Prowlarr's namespace; proxy tags matched enabled indexers. Profilarr's authenticated configuration/tasks/settings and both downstream Arr connections passed |

### MCP reads and write previews

All 39 advertised tools were called. Eighteen read tools exercised configured
services successfully. Their aggregate responses had no degraded-service entries;
the detail read also succeeded. The nineteenth read correctly reported an
unconfigured integration, which does not validate profile drift.

| Read tools | Result |
|---|---|
| `stack_health`, `diagnose` | Live service/evidence checks succeeded |
| `get_library`, `get_media_details`, `search_media`, `lookup_media`, `discover_media` | Actual library and external metadata reads succeeded |
| `get_queue`, `get_history`, `get_wanted`, `get_blocklist`, `get_calendar` | Existing acquisition data returned successfully |
| `get_indexers`, `get_releases`, `get_subtitles`, `get_playback`, `get_requests`, `get_metadata_issues` | Integration reads succeeded; the release query returned 11 candidates; all four reported subtitle providers were healthy |
| `get_profile_issues` | Coverage gap: returns an explanatory note because MCP has no configured Profilarr; zero issues does not mean drift was checked |

Eighteen write tools returned terminal `dry_run: true`, `applied: false`
previews without confirmation tokens. This exercises argument resolution and
planning, **not** the native apply operation. Four previews were existing-state
no-ops: `add_media`, `set_monitoring`, `update_media` and `request_media`.
The episode-file deletion preview resolved a real season with 12 files and
remained blocked by destructive-write policy.

| Write preview group | Tools exercised |
|---|---|
| Search / scan / subtitles / torrent input | `trigger_search`, `trigger_scan`, `trigger_subtitle_search`, `grab_release` |
| Library settings / removal | `add_media`, `set_monitoring`, `update_media`, `delete_media`, `delete_episode_files` |
| Queue / client / indexers | `remove_queue_item`, `clean_queue`, `pause_downloads`, `remove_blocklist_item`, `manage_indexer` |
| Requests / metadata | `respond_to_request`, `delete_request`, `request_media`, `fix_metadata` |
| Unavailable capabilities | `sync_database` refused unconfigured Profilarr; `set_watched` refused absent Jellyfin and cannot write Plex watch state |

The running compiled shared write gate and version-specific planner source were
reviewed first. Scan previews used the basic scan branch; import mappings were
excluded because their planning can POST manual-import reprocessing. The torrent
preview used an existing hash without tracker URLs; the GUID branch was excluded
because planning it performs another indexer search. MCP's audit database records
the verified preview IDs as `dry_run`; no apply or confirmation was requested.
Dry runs create MCP audit entries and can renew authentication sessions.

### Other tooling and outstanding findings

The final watchdog dry run passed all 38 checks. Hermes authenticated both
Dockhand environments, and its absolute CLI entrypoint reported nine active cron
jobs with zero doctor issues. CrowdSec's actual Traefik credential worked and
live firewall/Traefik counters increased. Both backup repositories authenticated
and passed fresh metadata checks; all three timers were enabled with successful
last runs. The earlier full data/restore rehearsals were not repeated here.

| Finding | Action / interpretation |
|---|---|
| Sonarr: 73 queue warnings; Radarr: one | Historical audit snapshot: all 74 records predated October 27 UTC. The subsequent authorized [queue cleanup](#authorized-queue-cleanup) inspected complete downloads and resolved the supported imports before dismissing stale entries; it also included unknown-media rows and newly arrived invalid releases |
| Profilarr MCP compatibility | Installed legacy Flask API exposes `/api/tasks` and `/api/arr/config`; the MCP adapter requires `/api/v1/status` and `/api/v1/arr`. Keep it disconnected until a supported migration and profile ownership with Recyclarr are reviewed. Git Sync job success does not prove Arr profile freshness; stored app-sync timestamps were from 2025-10-24 |
| Arr warnings | Sonarr/Radarr report `AllowedHostsCheck`; any restriction must retain the verified proxy/internal callers. Prowlarr reports a patch update; it was not upgraded during verification |
| Historical metadata / credentials | `ARR_MCP_VERSION=1.21.2` overrides reported metadata despite the pinned 1.44.5 image. A legacy `.env` CrowdSec key is rejected, while inspected active consumers use working credentials; do not revoke keys based only on this stale value |
| Verification limits | Native apply workflows, fresh notification delivery, a new CAPTCHA challenge, browser widget rendering, Pocket ID/WebAuthn/OIDC login and router AdGuard configuration were not exercised. Termix and CloudNode AdGuard are retired templates. Successful reads/previews are not an exhaustive end-to-end test of every stack |

Evidence is retained privately under
`~/.codex/backups/homelab-tooling-check-20261027-130209/`, including
`native-audit-complete.json`, `network-tooling/functional-results.json`,
`non-arr-summary.md`, `mcp-reads/`, `mcp-dryruns/` and
`mcp-audit-outcomes.json`. Raw responses can include private media metadata and
remain outside Git.

For routine read-only verification, run on CloudNode as the Hermes owner:

```bash
python3 "$HOME/.hermes/scripts/home-services.py" verify
python3 "$HOME/.hermes/scripts/home-services.py" mcp-status
python3 "$HOME/.hermes/scripts/service-watchdog.py" --dry-run
"$HOME/.local/bin/hermes" cron doctor
```

Expected results: all verifier entries succeed, MCP reports 39 tools for this
release, watchdog reports 38 checks with no failures, and cron doctor reports
zero issues. These routine commands do not repeat the individual MCP functional
calls. The private audit harnesses retain those exact calls; every write call
sets boolean `dry_run: true` and omits `confirm`.

Planner behavior was checked against the running write gate and
[arr-mcp 1.44.5 write protocol](https://github.com/bardesss/arr-mcp/blob/v1.44.5/docs/writes.md).
The Profilarr API mismatch was checked against the installed Flask routes and
[the version-specific adapter](https://github.com/bardesss/arr-mcp/blob/v1.44.5/src/services/profilarr.ts).

## Authorized queue cleanup

The user subsequently authorized queue cleanup. The fresh snapshot included
unknown-media items: 75 Sonarr rows and two Radarr rows, covering 24 distinct
downloads. qBittorrent had 257 torrent records. Work was grouped by exact
download ID, because removing one season-pack row affects the whole download.

| Work | Verified result |
|---|---|
| Useful imports | Recovered 13 missing main episodes and applied 25 improvements accepted by native per-file validation and the existing quality/custom-format configuration. Existing-state duplicates and rejected upgrades were excluded |
| Incorrect episode associations | Sonarr's saved import history proved nine episode files had been assigned one slot too early. Corrected associations using existing library paths, then renamed those files from the vacant tail of the chain. No global naming setting was changed; the season now has all 12 main episodes |
| Invalid downloads | Initially found seven executable-only entries and one archive-only entry. All payload files were deselected and absent. Removed only their torrent records with `deleteFiles=false` and blocklisted the releases with immediate replacement searches suppressed. A further executable-only release arrived through normal RSS during verification and was handled under the same policy |
| Stale entries / valid seeds | Dismissed verified duplicates using queue-only ignore, after checking the current episode/movie files. Kept both movie editions and valid download sources. One completed pack followed the existing post-import category policy into `seeding`; its source relocation was verified rather than treated as deletion |
| Unmatched media | Kept two complete torrents in `manual-review`. Disabled automatic management only on those two before changing category, so their existing paths and files were retained. No missing series/movie was added, and no unknown title was guessed into the library |

Imports used explicit episode IDs and the native `ManualImport` command with
`importMode: copy`. Only selected, validated files were submitted. Quality and
language metadata came from the service's own file analysis. Native command
completion was followed by episode/file/path checks; completion alone was not
treated as proof of success. Existing-file reassociation used library paths
without a download ID, and each subsequent rename required an absent destination.
The unmonitored special remained with the seeded source rather than being guessed
into an episode slot.

Queue-only dismissal explicitly used:

```text
DELETE /api/v3/queue/{id}?removeFromClient=false&blocklist=false&skipRedownload=true&changeCategory=false
```

For invalid releases, only `blocklist` changed to `true`; their client records
were removed separately with qBittorrent's `deleteFiles=false`. Arr's
`removeFromClient=true` was excluded because these deployed versions request
download-data deletion. MCP destructive permissions remained disabled.

### Recovery and verification

Before writes, online Sonarr/Radarr database snapshots passed SQLite integrity
checks, and 48 torrent/fastresume files were saved for the 24 affected downloads.
All 132 existing library files had verified recovery hardlinks. The database and
torrent-state recovery archive was also copied privately to the Mac. Recovery
data is retained: configuration backups alone do not protect media replaced by
an upgrade.

Separate post-change Sonarr/Radarr snapshots also passed SQLite checks; all 498
torrent/fastresume files for the 249 retained torrents were saved. That recovery
archive was copied privately to the Mac without replacing the pre-change copy.

Thirteen copied media files passed full SHA-256 comparisons against their current
download sources, covering 19,569,026,702 bytes on each side. The 25 hardlinked
imports were verified by device/inode and size. The existing post-import policy
relocated a complete torrent across bind-mount aliases, so source verification
followed its current qBittorrent path. A native torrent integrity recheck was
used for the relocated source and the retained review torrent whose file
timestamp changed.

Exact plans, native responses, before/after metadata, recovery locations and
verification results are private under
`~/.codex/backups/homelab-queue-cleanup-20261027-155044/`. Media titles, hashes,
credentials and recovery database contents remain outside Git. Final queue and
integrity results are in `final-verification.private.json`,
`copied-media-sha256.private.json` and `native-recheck-results.json`.

The supported behavior was checked against the deployed
[Sonarr queue controller](https://github.com/Sonarr/Sonarr/blob/v4.0.20.3014/src/Sonarr.Api.V3/Queue/QueueController.cs),
[Radarr queue controller](https://github.com/Radarr/Radarr/blob/v6.4.4.10685/src/Radarr.Api.V3/Queue/QueueController.cs),
[Sonarr manual-import service](https://github.com/Sonarr/Sonarr/blob/v4.0.20.3014/src/NzbDrone.Core/MediaFiles/EpisodeImport/Manual/ManualImportService.cs),
and [qBittorrent API](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-5.0)).

Final native verification returned **Sonarr 0 / Radarr 0 queue rows**. Nine
invalid torrent records were removed and blocklisted, including the release that
arrived during the cleanup. The 249 retained torrents were all in healthy upload
states: 242 `stalledUP` and seven actively uploading. The two native integrity
rechecks completed at 100% and returned to seeding. Verification accounted for
all 84 original download files, including 15 relocated by the existing category
policy, and all 132 library recovery links. All 38 imports and nine corrected
associations remained valid. The final service-watchdog dry run passed 38 checks.

The two items in `manual-review` still require a decision about library ownership;
their data and seeding were preserved. Recovery links and snapshots are retained
until the result has been accepted. No recurring queue-cleanup job was installed.
Plex service availability passed, but the bounded read-only follow-up did not
confirm its episode indexing. No forced Plex refresh or metadata repair was run.

## Primary documentation used

- [SQLite online backup](https://www.sqlite.org/backup.html) and [restic](https://restic.readthedocs.io/en/stable/)
- [Pangolin machine credentials](https://docs.pangolin.net/manage/clients/machine-clients) and [site credentials](https://docs.pangolin.net/manage/sites/credentials)
- [Olm 1.9.1 config loading](https://github.com/fosrl/olm/blob/1.9.1/config.go)
- [Docker published ports](https://docs.docker.com/engine/network/port-publishing/) and [volume lifecycle](https://docs.docker.com/engine/storage/volumes/)
- [Linux swappiness](https://docs.kernel.org/admin-guide/sysctl/vm.html#swappiness)

Additional version-specific sources are linked from the affected service pages.
