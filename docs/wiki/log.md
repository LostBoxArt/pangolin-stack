---
title: "Wiki Log"
slug: wiki-log
type: log
status: active
tags: ["homelab", "wiki", "log"]
aliases: ["maintenance log"]
entities:
  primary: wiki-log
  mentions: []
related: ["./README.md", "./maintenance-workflow.md", "./index.md"]
sources: ["AGENTS.md"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-10-27
---
# Wiki Log

Append-only record of structural wiki changes, maintenance passes, and review
artifacts.

## [2026-04-17] bootstrap | initial service audit
- Added the first dated compose review at
  `docs/wiki/compose-review-2026-04-17.md`.
- Added CloudNode service pages under `docs/wiki/services/`.
- Established findings, severities, and remediation snippets per service.

## [2026-04-17] structure | LLM-wiki entry points and workflow
- Added `docs/wiki/system-overview.md` as the fast orientation page.
- Added `docs/wiki/maintenance-workflow.md` to define ingest, answer, and lint
  behavior for future agents.
- Added `docs/wiki/llm-wiki-pattern.md` to capture the adopted external best
  practices and how they map to this homelab.
- Added `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` as machine-oriented
  entry points.
- Updated `docs/wiki/README.md` to link the new pages and removed broken links
  to HomeNode pages that are not yet present in the repo.

## [2026-04-17] structure | HomeNode namespace ingestion and machine entry-point refresh
- Updated `docs/wiki/README.md` to include the HomeNode service TOC and HomeNode review link.
- Updated `docs/wiki/system-overview.md` to reflect current dual-host coverage and HomeNode operational rules.
- Refreshed `docs/wiki/maintenance-workflow.md` for `services-homenode/` pages and HomeNode live-host sync rules.
- Refreshed `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` so machine entry points cover both CloudNode and HomeNode.
- Added namespace guidance to `docs/wiki/llm-wiki-pattern.md` for duplicate service names across hosts.

## [2026-04-17] structure | phase-1 schema groundwork
- Added `docs/wiki/index.md` as a flat content catalog for agents and humans.
- Added `docs/wiki/glossary.md` for repeated homelab term disambiguation.
- Added frontmatter to existing wiki pages so typed metadata is now available across the current corpus.
- Refreshed top-level entry points so `README.md`, `llms.txt`, `llms-full.txt`, and `system-overview.md` reference the new index/glossary layer.

## [2026-04-17] structure | hosts networks runbooks and lint foundation
- Added host pages for the CloudNode and HomeNode under `docs/wiki/hosts/`.
- Added network pages for `pangolin` and `traefik_traefik` under `docs/wiki/networks/`.
- Added foundational runbooks for Gerbil/Traefik recreation, Pocket-ID data migration, and Olm reachability checks under `docs/wiki/runbooks/`.
- Added `scripts/wiki_lint.py` for mechanical wiki checks and refreshed entry-point pages to reference the new structure.

## [2026-04-17] maintenance | lint-safe research note and HomeNode cross-link cleanup
- Added complete frontmatter metadata to `docs/wiki/llm-wiki-research-and-best-practices.md` and converted raw placeholder wikilink examples to lint-safe placeholder syntax.
- Fixed the `services-homenode/recyclarr.md` cross-link so it points cleanly to `profilarr.md` without a broken anchor.
- Re-ran `scripts/wiki_lint.py` and cleared all reported issues.

## [2026-04-17] structure | concept and decision layer seed
- Added `docs/wiki/concepts/port-matrix.md` as the first cross-cutting topology concept page.
- Added initial decision records for version pinning, CloudNode Traefik/Gerbil namespace sharing, and HomeNode live-first sync workflow.
- Refreshed `index.md`, `README.md`, `llms.txt`, `llms-full.txt`, and `system-overview.md` to expose the new knowledge-layer pages.

## [2026-04-17] maintenance | index wording cleanup
- Tightened truncated descriptions in `docs/wiki/index.md` for the CloudNode review, HomeNode review, `services/adguard-home.md`, and `services-homenode/newt.md` entries so the flat catalog reads cleanly for future agents.
- Re-ran `scripts/wiki_lint.py` and kept the wiki clean.

## [2026-04-17] maintenance | AGENTS read-path clarification
- Added a maintenance-workflow note that if a broad repo scan flags `AGENTS.md`, agents should read it directly rather than skip the repo briefing.
- Re-ran `scripts/wiki_lint.py` after the note update and kept the wiki clean.

## [2026-04-17] structure | raw/source ingest layer and semantic health-check loop
- Added `docs/wiki/raw/README.md` and `docs/wiki/raw/articles/README.md` as the new immutable ingest layer for external source captures.
- Added `docs/wiki/sources/README.md` plus a source-summary page for the AskVibecoders excerpt about Karpathy-style LLM wiki maintenance.
- Added a paired raw capture for the user-pasted AskVibecoders excerpt because Reddit blocked direct retrieval from this environment.
- Updated `README.md`, `index.md`, `maintenance-workflow.md`, `llm-wiki-pattern.md`, `llms.txt`, and `llms-full.txt` so future cron runs know to use `raw/`, `sources/`, and semantic health checks as part of continuous wiki optimization.

## [2026-04-18] maintenance | AGENTS direct-read surfaced in machine entry points
- Added the `AGENTS.md` direct-read fallback note to `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` so future agents do not skip the repo briefing when broad scans flag it.
- Patched the `pangolin-stack-wiki-maintenance` skill with the same repo-specific pitfall.

## [2026-04-18] maintenance | home-only boundary surfaced in machine entry points
- Added a home-only scope-boundary note to `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` so future agents do not mix work/HPC guidance into homelab answers.

## [2026-04-18] maintenance | stale memory fact removed and index link fixed
- Removed the stale Hermes memory fact claiming `hermes web` is an alias for `hermes dashboard`, plus the related garbage entity rows extracted from it.
- Fixed the inline CloudNode dashdot backlink in `docs/wiki/index.md` so the HomeNode dashdot entry points to the correct wiki path.
- Re-ran `scripts/wiki_lint.py` and kept the wiki clean.

## [2026-04-19] maintenance | gerbil service page backfilled
- Added `docs/wiki/services/gerbil.md` so the existing README, index, manifest, host, decision, and runbook backlinks now resolve to a concrete CloudNode service page.
- Re-ran `scripts/wiki_lint.py` and kept the wiki clean.

## [2026-04-19] maintenance | workflow boundary cleanup
- Corrected `docs/wiki/maintenance-workflow.md` so dated reviews and service pages remain classified as synthesized wiki content rather than raw sources.
- Added a cron-maintenance guardrail to the freshness loop so routine wiki upkeep does not create duplicate or self-referential cron jobs/prompts.
- Re-ran `scripts/wiki_lint.py` and kept the wiki clean.

## [2026-04-19] maintenance | cron guardrail surfaced in machine entry points
- Added the no-recursive-cron maintenance guardrail to `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` so future agents see it before making routine wiki changes.
- Patched the `pangolin-stack-wiki-maintenance` skill to match the same cron-maintenance restriction.

## [2026-04-19] maintenance | latest-review selection clarified
- Updated `docs/wiki/README.md`, `docs/wiki/llms.txt`, `docs/wiki/llms-full.txt`, and `docs/wiki/maintenance-workflow.md` so future agents explicitly prefer the newest dated CloudNode/HomeNode review files instead of assuming the currently named ones stay latest forever.
- Re-ran `scripts/wiki_lint.py` and kept the wiki clean.

## [2026-04-19] maintenance | dockhand and hawser live-update findings captured
- Updated `docs/wiki/services/dockhand.md` with the verified post-update Dockhand state: app version `1.0.18`, health-check verification, DB backup path, and the note that `pending_container_updates` can remain stale after manual updates.
- Updated `docs/wiki/services-homenode/hawser.md` with the verified Hawser recovery/update result: `0.2.24 -> 0.2.40`, current digest, and the control-path caveat for agent self-updates.
- Updated `docs/wiki/hosts/homenode.md` with the SSH-plus-sudo recovery note for Hawser on HomeNode.

## [2026-04-19] maintenance | safe-wrapper command path surfaced
- Updated `AGENTS.md` to use `/usr/local/sbin/hermes-safe-service` and `/usr/local/sbin/hermes-safe-logs` for Olm status/log/restart examples instead of raw `sudo systemctl` or `journalctl`.
- Refreshed `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` so future agents see the same CloudNode safe-wrapper rule before operating on `olm`, `olm-watchdog`, or `hermes-gateway`.
- Re-ran `scripts/wiki_lint.py` and kept the wiki clean.

## [2026-04-20] maintenance | cron no-compose-edit rule surfaced
- Refreshed `docs/wiki/maintenance-workflow.md`, `docs/wiki/llms.txt`, and `docs/wiki/llms-full.txt` so routine wiki-maintenance cron runs explicitly avoid compose-file edits as well as recursive cron churn.
- Re-ran `scripts/wiki_lint.py` and kept the wiki clean.

## [2026-04-20] maintenance | HomeNode repo-sync gap surfaced in machine guidance
- Clarified in `docs/wiki/maintenance-workflow.md` that HomeNode service work must use the live compose first and create the matching `host-configs/homenode/` tracked copy when `NM1` means no repo copy exists yet.
- Refreshed `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` so future agents do not assume every HomeNode service already has a tracked repo compose file.

## [2026-04-20] maintenance | HomeNode tracked-copy creation rule aligned
- Refreshed `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` so HomeNode service work now explicitly says to create `host-configs/homenode/<service>/docker-compose.yml` when `NM1` means the tracked mirror is still missing.
- Patched the `pangolin-stack-wiki-maintenance` skill with the same repo-specific pitfall.

## [2026-04-20] maintenance | missing wiki index entries and frontmatter fixed
- Added `aliases: ["badger"]` to `services/badger.md` frontmatter (was the only CloudNode service page missing it).
- Added `badger` and `olm` entries to `docs/wiki/index.md` CloudNode Services section so the flat catalog covers all service pages.
- Re-ran `scripts/wiki_lint.py` — all 58 files pass clean.

## [2026-04-20] maintenance | AGENTS.md inventory and llms-full.txt deduplicated
- Removed duplicate `apps` row and corrected `homenode-apps` in `AGENTS.md` (dropped `badger`, `pocket-id`, `quay`; fixed `flaresolverr` spelling; added `qbittorrent`, `dashdot`).
- Removed redundant duplicate intro paragraph in `docs/wiki/llms-full.txt`.
- Re-ran `scripts/wiki_lint.py` — all 58 files pass clean.

## [2026-04-21] maintenance | badger and olm service pages corrected to match repo reality
- Rewrote `docs/wiki/services/badger.md` so it describes Badger as the Traefik CrowdSec bouncer plugin (`config/traefik/traefik_config.yml`, `v1.4.0`) rather than a non-existent container.
- Rewrote `docs/wiki/services/olm.md` so it describes Olm as the CloudNode systemd tunnel service (`1.4.4`, `--override-dns=false`, `hermes-safe-service` wrappers) rather than a non-existent container.
- Added `badger` and `olm` to `docs/wiki/README.md` Core section and to `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` CloudNode service lists.
- Completed the truncated `docs/wiki/maintenance-workflow.md` "Additional high-value page families" section.
- Re-ran `scripts/wiki_lint.py` — all files pass clean.

## [2026-04-21] maintenance | wiki mechanical cleanup and skill drift flagged
- Removed empty bullet points from `docs/wiki/README.md` (Core section) and `docs/wiki/index.md` (CloudNode Services section).
- Removed orphan text fragments in `docs/wiki/README.md` that described non-existent `raw/` and `sources/` pages.
- Removed empty `## Raw Sources` and `## Source Pages` sections from `docs/wiki/index.md` since the directories do not exist.
- Removed broken links to `./raw/README.md` and `./sources/README.md` from `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt`.
- Removed three truncated/incomplete sentences about external articles and raw sources from `llms.txt` and `llms-full.txt`.
- Fixed malformed code block line in `AGENTS.md` (`||` leak in file tree diagram).
- Updated `last_lint` timestamps in `README.md` and `index.md` to 2026-04-21.
- Re-ran `scripts/wiki_lint.py` — all files pass clean.
- Flagged `pangolin-stack-wiki-maintenance` skill for manual update: it still uses deprecated "VPS/NASUS" terminology and references `nasus-review-*.md`, `services-nasus/`, and `host-configs/nasus/` which were renamed to CloudNode/HomeNode on 2026-04-21. Security scan blocked automated skill patching this session.

## [2026-04-21] service | landing page redesigned and deployed
- Complete visual redesign of `example.com` landing page following Anthropic's
  "frontend-design" skill principles: bold aesthetic direction, distinctive
  typography, intentional spatial composition.
- Key changes: full-page layout replacing centered card, Cormorant Garamond
  serif + Outfit sans-serif fonts, warm industrial palette (near-black with
  copper accents), structural grid lines, film-grain noise overlay, large
  avatar with rotating amber ring and pulsing glow, staggered entrance
  animations, 3+2 centered link grid, corner bracket framing.
- All 5 links preserved (Email, LinkedIn, GitHub, X, Steam) with icons.
- Bio, focus tags, and "Built by me. Hosted at home." footer retained.
- Responsive single-column layout for mobile.
- Respects `prefers-reduced-motion`.
- Deployed to live nginx container at `sites/dennisb-landing/`.
- Updated `docs/wiki/services/landing.md` to reflect new design.

## [2026-04-21] maintenance | repo public-ready cleanup and live config fixes
- Ran `git-filter-repo` to purge `config/config.yml` (secrets), `config/db/db.sqlite.fresh`
  (binary DB), and `config/traefik/rules/resource-overrides.yml.back` (basic-auth hash)
  from all history.
- Replaced all real addresses/domains/names with generic examples across history
  (real domain → `example.com`, internal range → `192.168.1.x`, `NASUS` → `HomeNode`,
  `VPS` → `CloudNode`, etc.).
- Removed `sites/dennisb-landing/` from git history and added to `.gitignore`.
- Fixed `.gitignore` paths: `config/config.yml`, `config/pangolin/config.yml`, backup
  patterns, and SQLite fresh files.
- Restored `config/config.yml` symlink (`→ pangolin/config.yml`) after `git-filter-repo`
  deleted it; documented the symlink requirement in `docs/wiki/services/pangolin.md`
  as finding `F-PANGOLIN-3`.
- Restored `sites/dennisb-landing/` from `/tmp/github-check-2` backup after the
  directory was lost during cleanup.
- Fixed `stacks/apps/docker-compose.yml` landing volume from hardcoded
  `/opt/homelab/sites/example-landing` to relative `../../sites/dennisb-landing`.
- Updated `docs/wiki/services/landing.md` to reflect the actual `dennisb-landing`
  path and gitignored status.
- Replaced dead Fastmail SMTP credentials in `config/pangolin/config.yml` with
  Gmail placeholder values (`smtp.gmail.com`, app-password ready).
- Re-ran `scripts/wiki_lint.py` — all files pass clean.

## [2026-04-21] service | adguard-home removed
- Stopped and removed `adguard-home` container (`stacks/dns/docker-compose.yml`).
- Removed `dns` stack from `startup.sh` phase 2.
- Marked `docs/wiki/services/adguard-home.md` as `status: removed`, added removal note and config backup path.
- Removed AdGuard Home from `docs/wiki/README.md`, `docs/wiki/index.md`, `docs/wiki/hosts/cloudnode.md`.
- Removed DNS-over-HTTPS section and service table entry from `README.md` and `INFRASTRUCTURE.md`.
- Updated `docs/wiki/compose-review-2026-04-17.md` scoreboard to mark `dns` stack as **removed 2026-04-21**.
- Config preserved at `./config/adguard-home/` in case restoration is needed.
- iPhone now uses `1.1.1.1` directly.

## [2026-04-21] service | linkstack replaced by bespoke landing page
- Added `docs/wiki/services/landing.md` documenting the new static landing page
  at `example.com` (nginx:alpine, `sites/example-landing/`).
- Archived `docs/wiki/services/linkstack.md` — marked `status: archived`, added
  archive note, and cross-linked to `landing.md`.
- Updated `stacks/apps/docker-compose.yml` to replace the `linkstack` service
  with `landing`.
- Updated `docs/wiki/README.md`, `docs/wiki/index.md`, `docs/wiki/system-overview.md`
  to reference `landing` instead of `linkstack`.
- Updated `docs/wiki/compose-review-2026-04-17.md` scoreboard and upstream
  reference table to reflect the replacement; added changelog entry.
- Updated `AGENTS.md` inventory and volume notes.
- Re-ran `scripts/wiki_lint.py` — all files pass clean.

## [2026-04-21] maintenance | skill and machine entry points updated
- Patched `pangolin-stack-wiki-maintenance` skill: replaced all deprecated "VPS/NASUS" terminology with "CloudNode/HomeNode", updated paths from `services-nasus/` / `nasus-review-*.md` / `host-configs/nasus/` to `services-homenode/` / `homenode-review-*.md` / `host-configs/homenode/`.
- Removed `adguard-home` from `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` active CloudNode service lists since the service was removed on 2026-04-21.
- Re-ran `scripts/wiki_lint.py` — all files pass clean.

## [2026-04-21] maintenance | badger and olm service pages recreated and indexes repaired
- Recreated missing `docs/wiki/services/badger.md` and `docs/wiki/services/olm.md` (log previously claimed they existed, but they were not on disk; pages now document Badger as the Traefik CrowdSec plugin and Olm as the CloudNode systemd tunnel service).
- Added `badger` and `olm` to `docs/wiki/index.md`, `docs/wiki/README.md`, and `docs/wiki/hosts/cloudnode.md` CloudNode service lists.
- Added `badger` to `docs/wiki/system-overview.md` Core section.
- Removed stale `dns` stack from startup order and removed dead `dns.example.com` public endpoint from `docs/wiki/system-overview.md` following AdGuard removal on 2026-04-21.
- Updated `last_lint` timestamps on modified pages.
- Re-ran `scripts/wiki_lint.py` — all files pass clean.

## [2026-04-22] maintenance | runbook leaks and memory compression
- Fixed `docs/wiki/runbooks/403-all-sites.md`: replaced remaining real domain, real IP, and stale internal IP with generic examples; updated "VPS" references to "CloudNode".
- Fixed `docs/wiki/services/adguard-home.md`: replaced historical endpoint domain leak with `dns.example.com`.
- Compressed memory fact_store: removed duplicate password facts (2×) and duplicate docker-exec tip (1×), updated remaining fact with deprecated `VPS/NASUS` terminology to `CloudNode/HomeNode`.
- Re-ran `scripts/wiki_lint.py` — all files pass clean.

## [2026-04-22] maintenance | 403 runbook surfaced in machine entry points
- Added `docs/wiki/runbooks/403-all-sites.md` to `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` so future agents discover the CrowdSec-fails-closed runbook from machine-oriented manifests.
- Re-ran `scripts/wiki_lint.py` — all files pass clean.

## [2026-04-21] incident | CrowdSec container exit caused global 403s
- **Symptom**: All Cloudflare-fronted sites returned 403. Both home ISP and cellular affected.
- **Initial misdiagnosis**: Assumed Cloudflare IP blocking or WAF challenge.
- **Actual root cause**: `crowdsec` container (not `crowdsec-web-ui`) had exited ~23 minutes prior. Traefik's `websecure` entrypoint applies `crowdsec@file` middleware to every request by default. With the CrowdSec LAPI unreachable, the plugin returned 403 for all traffic.
- **Fix**: `docker start crowdsec` — immediate restoration of all sites.
- **Lesson**: When all sites return 403 simultaneously, check `docker ps -a | grep crowdsec` first. The CrowdSec bouncer plugin fails closed (blocks) when LAPI is unreachable.
- **Cleanup**: Removed unnecessary `reverse_tunnel` SSH key from `~/.ssh/authorized_keys` and reverted `GatewayPorts` (still needs sudo to complete).
- **New runbook**: `docs/wiki/runbooks/403-all-sites.md`

## [2026-04-21] incident | HomeNode SSH through Olm tunnel blocked
- **Symptom**: Termix web SSH to HomeNode (`192.168.1.10`) failed with "Connection lost before handshake". CloudNode direct SSH worked initially, then also broke.
- **Initial misdiagnosis**: Asustor `sshd` penalty table blocking Docker bridge IP `172.20.0.2` due to `sshd-session` seccomp crash (SIGSYS/syscall 87).
- **Actual root cause**: The CloudNode OpenSSH client (10.0p1-5ubuntu5) had an incompatibility with Asustor's custom `sshd-session` binary that triggered seccomp crashes on certain key exchange paths.
- **Fix**: `apt upgrade` on the CloudNode updated OpenSSH client to `10.0p1-5ubuntu5.1`. After the update, SSH from CloudNode to HomeNode through the tunnel worked immediately.
- **Lesson**: The "penalty table" was a symptom of the real issue (client-induced `sshd-session` crash), not the root cause. Restarting Asustor `sshd` cleared the table temporarily, but the crash reoccurred on every connection attempt from the old client version.
- **Important**: Asustor `sshd` restart via `SIGHUP` does NOT clear the penalty table — the PID stays the same. A hard restart (`kill -9`) or ADM GUI toggle is required to wipe it.
- **New runbook**: Added SSH troubleshooting section to `docs/wiki/runbooks/403-all-sites.md` and updated `asustor-ssh-penalty-fix` skill with corrected findings.

## [2026-04-22] maintenance | AGENTS.md drift cleanup and wiki last_lint repair
- Removed stale `dns` stack and AdGuard Home references from `AGENTS.md` (stack table, startup order, service inventory, public endpoints, dedicated section); corrected stack count from 7 to 6.
- Fixed malformed markdown table syntax in `AGENTS.md` stack table (extra leading pipes).
- Updated stale `last_lint: 2026-04-17` to `2026-04-21` in `docs/wiki/compose-review-2026-04-17.md` and `docs/wiki/services/pangolin.md` to match their last modification dates.
- Re-ran `scripts/wiki_lint.py` — all 55 files pass clean.

## [2026-04-22] maintenance | autonomous memory and skill hygiene pass
- Fixed `~/.hermes/memories/MEMORY.md`: corrected stale HomeNode IP from `192.168.0.10` to `192.168.1.10`, updated deprecated `VPS/NASUS` terminology to `CloudNode/HomeNode`, and fixed network range from `192.168.0.0/24` to `192.168.1.0/24`.
- Removed stale LinkStack replacement preference from `~/.hermes/memories/USER.md` (completed 2026-04-21).
- Sanitized remaining real data leaks in `docs/wiki/log.md`: removed real ISP IP, fixed `192.168.0.10` → `192.168.1.10` in incident entries, replaced `dennisb.xyz` with `example.com` in service descriptions, and updated `VPS` → `CloudNode` in incident narrative.
- Patched 7 skills for deprecated terminology and wrong IPs:
  - `home/homelab-automation`: `VPS/Nasus` → `CloudNode/HomeNode`
  - `home/pangolin-networking`: `VPS` → `CloudNode`
  - `home/traefik-routing`: `VPS stack` → `CloudNode stack`
  - `home/seerr-media-requests`: `192.168.0.10` → `192.168.1.10` (3×)
  - `devops/dockhand-hawser-monitoring`: `NASUS` → `HomeNode`, `192.168.0.10` → `192.168.1.10`, `NAS host` → `HomeNode host`
  - `devops/pangolin-service-swap`: `NASUS` → `HomeNode`
  - `software-development/hermes-gateway-live-session-guardrails`: `VPS` → `CloudNode`
- Removed unused one-time research artifact `~/.hermes/skills/ai-pricing-research.md`.
- Re-ran `scripts/wiki_lint.py` — all files pass clean.

## [2026-10-27] maintenance | FileFlows removal and initial hardening

- Removed FileFlows and its DV watcher from HomeNode: containers, dedicated network, images, application data, test media and dynamic route. Removed the CloudNode public resource, pending update, deployment copies, watchdog entries, active inventories, obsolete guidance and vault entry. Shared infrastructure, historical records and private rollback copies were preserved.
- Fixed the Hermes service-check bootstrap; read-only checks and the authenticated 39-tool MCP connection pass.
- Hardened qbit-proxy on Node 24 with upstream TLS verification, a 10-second request deadline and an end-to-end version healthcheck. Regression checks cover current qBittorrent port-specific cookies and 204 responses. API checks pass from Homarr's network; full browser widget rendering was not tested.
- Made backup outputs private, added missing site/proxy/CrowdSec content, and replaced Pangolin's live database copy with a validated online snapshot. Existing archives were retained. Other live database snapshots and a full application restore drill remain outstanding.
- Restricted the NAS recovery-kit PDF and the user-owned Olm credential copy to mode 0600 without changing their contents. Olm's service configuration and credential rotation remain outstanding. Added isolated backup and proxy regression checks; preserved pre-existing Bazarr edits and documentation changes.

## [2026-10-27] maintenance | supported fixes and recovery verification

- Installed Ponytail and I-have-ADHD at Codex user scope, with global standing
  defaults and fresh cross-project skill-catalog checks.
- Completed the earlier Olm work and rotated the exposed Newt credential;
  canonical Newt Git source uses private Dockhand variables. Repaired CrowdSec
  SSH protection, management bindings, Homarr targeting, conditional namespace
  recovery, NAS dashboard access and host mounting, and duplicate routing.
- Supervised the loopback MCP tunnel with systemd, fixed watchdog coverage and
  timing, and resumed the release checker as a local read-only job. Authenticated
  MCP exposes 39 tools and all 38 watchdog checks pass.
- Completed independent database snapshots, encrypted cross-host copies, recovery
  key verification, six NAS application cold starts with 16 durable table checks,
  and the private VPS application rehearsal. Fixed restore quiescence, ownership,
  SQLite sidecars, current-tool preservation, image recovery and retention guards.
- Diagnosed nested Tailscale-over-Olm packet loss and installed a tested
  per-backup SSH relay, preserving global routing and MTUs. Added sanitized
  sources and current runbooks; retained pre-existing user edits. See the
  [dated maintenance record](./maintenance-2026-10-27.md) for exact artifacts,
  schedules, verification limits and reviewed exclusions.

## [2026-11-21] migration | NASUS to pure storage, all workloads to rammus

- Renamed the compute host `pn62` to `rammus` (`192.168.0.12`): hostname,
  `/etc/hosts`, Hawser `AGENT_NAME`, Dockhand environment, OPNsense static DHCP
  mapping, and AdGuard rewrites.
- Moved every application off NASUS to rammus under `/opt/docker/stacks/` with
  appdata at `/opt/docker/config/`: `newt`, `traefik`, `plex`, `qbittorrent`,
  `prowlarr`, `scryer`, `arr-mcp`, `dashdot`, `hawser`. NASUS now runs **zero
  containers**; fourteen stopped copies remain as a rollback path.
- Added `docs/wiki/hosts/rammus.md` and rewrote
  `docs/wiki/hosts/homenode.md` as a storage-only host page.
- Switched the NASUS NFS client mounts from `soft,timeo=50,retrans=3` to
  `hard,timeo=600,retrans=2`; `soft` produced `EIO` from slow RAID5 commits.
  Removed the `systemd` automount triggers, which left containers reading empty
  directories after an idle expiry.
- Replaced `RequiresMountsFor` with `Wants=` + `After=` on the four mount units
  in `/etc/systemd/system/docker.service.d/nfs.conf`. The previous form would
  stop Docker from starting at all whenever NASUS was down or still booting.
- Preserved Plex library identity (`MachineIdentifier` unchanged) and moved it
  onto the rammus iGPU (`/dev/dri`, `renderD128`); removed the stale
  `HardwareDevicePath`, set `autoEmptyTrash="0"` and
  `TranscoderTempDirectory=/transcode`.
- qBittorrent keeps identical container paths (`/data`, `/downloads`) so all 39
  torrents needed no recheck; incomplete downloads now land on local SSD via
  `/data/downloads/incomplete`. `Session\TempPathEnabled` enabled.
- Pointed Pangolin targets `request.dennisb.xyz` and `plex.dennisb.xyz` at
  `192.168.0.12`, and moved the OPNsense NAT forwards for 32400 and 6881 from
  `.10` to `.12`.
- LAN DNS is AdGuard Home on OPNsense (`:53`), not unbound. All rewrites were
  repointed to `.12`; `dash-nas` was removed with the NASUS `dash` container.
- Fixed two production breaks found during verification: a leftover NASUS
  `newt-watchdog` cron that kept resurrecting a duplicate tunnel client (moved
  to rammus, now on `/etc/cron.d/newt-watchdog`), and `qbit-proxy` on the
  CloudNode still targeting the dead `192.168.0.10:443`.
- Hardened `/usr/local/sbin/rammus-backup.sh`: it now refuses to run when
  `/mnt/nasus/backups` is not a mountpoint, aborts if the appdata copy is under
  100 MB, and includes `/etc/cron.d`, `/etc/systemd/system`, `/usr/local`, and
  `/home/jesus/.ssh`. The earlier runs had copied about 12 KB of 2.5 GB.
- Bound Hawser to `192.168.0.12:2375` (was `0.0.0.0`) and gave it a real bind
  mount for `/data/stacks` instead of an anonymous volume.
- Added `docs/wiki/hosts/rammus.md`, updated `system-overview.md`, `index.md`,
  and `log.md`; `scripts/wiki_lint.py` reports zero errors and zero warnings.
- Open: no availability or certificate-expiry alerting exists.
- Removed the five dead AdGuard rewrites (`sonarr`, `radarr`, `bazarr`,
  `profilarr`, `flaresolverr`) after confirming they were stopped before the
  migration and had no container on either host. Rewrites went from 16 to 11;
  `AdGuardHome --check-config` passed, then the plugin was restarted. The five
  names now fall through to the Cloudflare record instead of returning a Traefik
  404. Backup: `/usr/local/AdGuardHome/AdGuardHome.yaml.bak-pre-deadrewrites`.
- Updated `/etc/hosts` on the CloudNode: `nasus`, `sonarr`, `radarr`, `bazarr`,
  `prowlarr`, `profilarr`, `torrent`, and `adguard` were still pinned to
  `192.168.0.10`. That static override, not DNS, was why four Homarr tiles showed
  red after the move — AdGuard was already answering `.12`. `dash-nas` was
  dropped from the pin list with the retired NASUS dashboard.
- Repointed ten `extra_hosts` entries in `stacks/dashboard/docker-compose.yml`
  from `192.168.0.10` to `192.168.0.12`. These pins live in the Homarr
  **container's** `/etc/hosts`, so they override both AdGuard and the host
  resolution and must be updated whenever an application changes address.
- Rewrote `docs/wiki/README.md` coverage from two hosts to three, and corrected
  the healthcheck claims against `docker inspect`: real healthchecks exist for
  `traefik`, `plex`, `prowlarr`, `scryer`, `arr-mcp`, and `hawser`;
  `newt`, `qbittorrent`, and `dashdot` have none.
- Corrected `INFRASTRUCTURE.md`: the network diagram previously showed
  Pangolin/Gerbil/CrowdSec inside the "home network" block and had orphaned
  boxes. It now shows CloudNode, then LAN with rammus and NASUS side by side.
  Also fixed the Dockhand env IDs (`3` = Rammus), the tunnel route
  (`192.168.0.0/24`), and the widget `extra_hosts` path.
- `concepts/port-matrix.md` now lists the ports actually published on rammus:
  2375 bound to `.12`, 3003 and 6881 on all interfaces, and 8099/6060 on
  loopback. Noted that UFW does not filter published container ports.
- Dropped the same four dead names (`sonarr`, `radarr`, `bazarr`, `profilarr`)
  from the CloudNode `/etc/hosts` pin and from the Homarr `extra_hosts` block,
  then recreated Homarr. Container checks: `nasus` 200, `torrent` 200,
  `prowlarr` 302, `adguard` 301. Six pins remain, all pointing at
  `192.168.0.12`.
- Verified Plex hardware transcoding on rammus with a live session: the
  transcoder ran `-hwaccel vaapi -hwaccel_device /dev/dri/renderD128,driver=iHD`
  with a `h264_vaapi` encoder and a fully GPU filter chain
  (`hwupload` → `deinterlace_vaapi` → `scale_vaapi`). The process held
  supplementary group `993` (`render`), which is the requirement that makes
  VAAPI work inside the container. Recorded the check in `hosts/rammus.md`,
  including the fallback-to-CPU symptom (no `vaapi` entries in the process args).
- Root-caused the scryer → qBittorrent failure. `scryer` (`172.19.0.6`) sends
  **no** credentials — no `/auth/login`, no `SID`, no `Authorization` header — and
  has only ever worked because of `AuthSubnetWhitelistEnabled=true`. The migration
  lost the `172.19.0.0/16` entry, every poll got `403`, and scryer escalated a
  back-off (`escalation_level 3`, `disabled_until`) that kept the warning firing
  for ~25 minutes after the whitelist was fixed. An attempt to disable the
  whitelist broke scryer *and* the CloudNode `qbit-proxy`; both were restored.
- Corrected a wrong intermediate diagnosis: `.2` on `traefik_traefik` is
  **Traefik**, not scryer. A capture attributed to scryer was Traefik relaying a
  browser session, which produced a false "scryer uses HTTP Basic auth" theory.
- Recorded the container IP map, the back-off behaviour, and the whitelist
  security debt in `AGENTS.md` and `hosts/rammus.md`. Open: scryer has no
  credentials configured, and the whitelist bypasses qBittorrent auth for six
  CIDRs including the now-nonexistent `172.18.0.0/16`.

## [2026-11-21] verification | two independent audits, corrections applied

Two read-only audit agents reviewed the migration independently: one against live
infrastructure, one against documentation accuracy.

- **Corrected `docs/wiki/hosts/homenode.md`:** it claimed all 14 stopped NASUS
  containers were `restart=no`. Nine are; `sonarr`, `radarr`, `bazarr`,
  `recyclarr`, and `profilarr` are still `unless-stopped`. The two dangerous ones
  (`newt`, `plex`) are genuinely `restart=no`, so a reboot cannot create a
  duplicate identity — but an ADM "start all" would revive the other five.
- **Corrected the Dockhand environment ID** in `AGENTS.md`, `README.md`, and
  `INFRASTRUCTURE.md`: the home environment is `env=3` (Rammus). `env=2` is the
  dead `Nasus` entry. The `curl` examples all used `env=2`.
- **Added a "Rollback to NASUS" section** to `hosts/rammus.md`, naming the
  appdata that has diverged (`qbittorrent`, `plex-db`, `prowlarr`, `scryer`,
  `arr-mcp`, and `/opt/docker/qbit-incomplete`, which exists only on rammus) and
  the five places that must be repointed.
- **Marked all 17 `services-homenode/*` pages `status: historical`** with a
  banner under the title. Several read as current instructions and would have
  led someone to deploy to NASUS.
- **Bound dashdot to `192.168.0.12:3003`** instead of all interfaces. Image
  unchanged, still serving 200. UFW does not filter published container ports,
  so the bind address is the only real control.
- **Documented, not fixed:** the backup has no history and copies live SQLite
  files while they are open (`sqlite3` is not installed on rammus, so a hot copy
  is not possible from the host); two OPNsense rules still allow `.10:2375`; NFS
  exports use `no_root_squash,async` across several subnets; `plex` and
  `qbittorrent` can start against an empty `/mnt/nasus/media` if NASUS is slower
  than rammus at boot. Plex's `autoEmptyTrash="0"` prevents the worst outcome.
- **Added `runbooks/add-rammus-service.md`** — the five places that must agree
  for a new hostname: compose, AdGuard rewrite, CloudNode `/etc/hosts`, Homarr
  `extra_hosts`, Pangolin target. This is the exact class of failure that caused
  the red dashboard tiles.
- Repository-wide: `192.168.1.x` in the runbooks corrected, `192.168.0.x`
  everywhere. `scripts/wiki_lint.py`: zero errors, zero warnings.
- **Added backup history to `/usr/local/sbin/rammus-backup.sh`.** Before each
  rsync, `opt-docker-latest` is hardlink-snapshotted to `opt-docker-YYYYMMDD`
  (`cp -al`) and the oldest beyond seven are pruned. Verified on run: identical
  inode, link count 2, so the snapshot costs no extra space on NASUS. Without
  this, an accidental appdata deletion would have been mirrored into the only
  copy on the next 03:30 run. Backup of the previous script:
  `rammus-backup.sh.bak-pre-snapshots`.
- **Gated the NFS-dependent containers on the mount actually existing.**
  `Wants=`/`After=` alone guaranteed ordering, not success, so a slow NASUS would
  have started `plex` and `qbittorrent` against an empty `/mnt/nasus/media`.
  Both now use `restart: "no"` (the only policy whose boot behaviour is certain),
  and `nasus-media-apps.service` starts them only when
  `mountpoint -q /mnt/nasus/media` succeeds, wrapped in `timeout 20` so a hung
  hard mount cannot hang the unit. `nasus-media-apps.timer` runs it at boot plus
  every 2 minutes and retries the mount via `Wants=`, so NASUS returning later
  brings both back with no intervention. Cost: crash recovery is up to 2 minutes.
  Stop the timer before a deliberate `docker stop`.
- **NFS exports narrowed is NOT done.** NASUS serves all four exports to
  `192.168.0.0/24`, `192.168.1.0/24`, and `192.168.3.0/24` with
  `no_root_squash,async`, but only `192.168.0.12` mounts them. The export file is
  ADM-managed (`/etc/exports` → `/volume0/etc/exports`), so the change belongs in
  the ADM UI — which the owner deliberately does not open, because each visit
  queues a stuck job. Left as a documented recommendation:
  narrow each export to `192.168.0.12(...)`. `no_root_squash` must stay until the
  backup script adds `--no-owner --no-group`, or `rsync -a` fails on ownership.
  `sync` instead of `async` is unmeasured and would mainly slow the nightly
  appdata copy.
- Confirmed Pangolin targets without sudo: `db.sqlite` is mode 0644, so
  `sqlite3 -readonly 'file:...db.sqlite?mode=ro'` works. `request` →
  `192.168.0.12:443` and `plex` → `192.168.0.12:32400`, both enabled.

### [2026-11-21] verification | Pangolin target audit

Checked every Pangolin resource against the live database and against the real
public path (resolved through Cloudflare's DoH, bypassing the CloudNode's
`/etc/hosts`, which pins four app names at `192.168.0.12` and silently turns a
"public" test into a LAN test).

- **Correct:** `plex` → `192.168.0.12:32400` and `request` → `192.168.0.12:443`
  both work end to end — public `plex.example.com` returns Plex's own `401`
  (reached, needs a token) and `/web/index.html` returns `200`. Zero `.10`
  targets remain. The other seven resources still point at CloudNode container
  names and are unaffected.
- **`request` is genuinely scryer, not a leftover seerr name.** The compose file
  sets `SCRYER_WEBAUTHN_RP_ID=request.example.com`, so scryer's passkeys are
  bound to that hostname. Renaming it would invalidate every registered
  authenticator.
- **`torrent`, `prowlarr`, `scryer`, `nasus`, `adguard` do not answer publicly —
  correct.** They are LAN-only, reached via AdGuard rewrites plus rammus Traefik.
- **`dash` is split-brained.** The Pangolin resource `dash` targets the
  CloudNode's `dashdot:3001`; the AdGuard rewrite sends LAN clients to
  `192.168.0.12:3003` on rammus. One hostname, two different dashboards. Fix is
  to retarget the Pangolin resource at `192.168.0.12:3003`.
- Corrected the `AGENTS.md` claim that the CloudNode host file pins six names:
  `/etc/hosts` has four (`nasus`, `prowlarr`, `torrent`, `adguard`); the six live
  in Homarr's `extra_hosts`, which adds `request` and `plex`.

### [2026-11-21] verification | Hermes knowledge base audited and corrected

A Sonnet agent updated Hermes's own wiki, skills, cron prompts and
`memory_store.db` on the CloudNode (119 files backed up to
`/home/jesus/.hermes/backups/homelab-rammus-sync-20261121/`).

- **Found: Hermes's monitoring is now lying.** `service-watchdog.py` runs every
  5 minutes and still probes NASUS. `.watchdog-state.json` at 22:05 reported 11
  services down with 15 consecutive failures each — `Newt`, `NAS Traefik`,
  `Hawser`, `Plex`, `Prowlarr`, `Scryer`, `qBit`, `arr-mcp`, `arr-mcp tunnel`,
  `Olm data path`, `Dashdot NAS application`. All of them are healthy on rammus.
  An alert was sent at 21:30:37 claiming a full outage.
- `qb-reaper.py` and `tl-force-seed-guard.py` still SSH to `.10`, and
  `update-home-crowdsec-whitelist.sh`, `ensure-arr-mcp-tunnel.sh` and
  `migration-infra-watch.py` (`*/15`, enabled) do too. None of them can work.
- The `dash-nas` watchdog check targets a hostname that no longer resolves.
- **Corrected a doc error:** `/etc/fstab` does **not** contain
  `timeo=600,retrans=2`. Those are the kernel defaults for a `hard` NFSv3 mount;
  `findmnt` shows them on the live mount. The table in `hosts/rammus.md` now
  shows the real fstab string and explains the defaults.
- **Corrected the Plex GPU-group story.** The container runs as **root**
  (`Config.User` empty, `GroupAdd=[]`) and opens `/dev/dri/renderD128` as root,
  so no supplementary group is involved today. Host `render` is GID **993**;
  the container's own `/etc/group` says `render:x:994:`, which is a red herring
  that nearly produced a wrong doc edit. `group_add: ["993"]` only matters if
  Plex is ever moved off root.
- **Not yet done:** repointing the Hermes scripts at rammus. This is a change to
  alerting behaviour, so the exact patches are being produced separately and
  reviewed before applying. Until then the watchdog keeps reporting a false
  outage.
- Note: the repo checkout on the CloudNode (`/home/jesus/pangolin-stack`) does
  **not** contain these corrections. They are uncommitted on the Mac only, so
  Hermes's repo-derived answers stay stale until the branch is committed and
  pushed.

### [2026-11-21] fixes | everything outstanding closed

- **Pangolin `dash` retargeted** (was split-brained). Pangolin stopped, DB
  backed up to `db.sqlite.bak-pre-dash-retarget`, `targets` row 7 changed from
  site `ThePangoli` / `dashdot:3001` (internalPort 60215) to site `homelab` /
  `192.168.0.12:3003`, Pangolin restarted. Verified the backend answers `200`
  with `Ubuntu 24.04.5` from the CloudNode, and all nine public resources still
  respond. Note: changing only the IP would have failed — a local-site target
  carries a Docker-mapped `internalPort` that is meaningless once the target
  moves to a newt site.
- **All 14 NASUS containers now `restart=no`.** `sonarr`, `radarr`, `bazarr`,
  `recyclarr` and `profilarr` were still `unless-stopped`, so a NASUS reboot
  could have revived services that now live on rammus. Manual `docker start`
  still works, so the rollback path is intact.
- **OPNsense `.10:2375` rules are blocks, not permits.** Verified with
  `pfctl -sr | grep 2375`: `block drop in quick` on `igc1` and `igc3`. An earlier
  audit misread the direction; they are protective and were left alone. The
  host page was corrected.
- **Hermes monitoring repointed at rammus.** `service-watchdog.py` now probes
  rammus (`RAMMUS_SSH`, `RAMMUS = 192.168.0.12`), NASUS is reported as its own
  storage check and gates nothing, and the retired `dash-nas` and CloudNode
  `127.0.0.1:3001` checks are gone. Dry run: **34 checks, all true, zero
  failures**. `qb-reaper.py`, `tl-force-seed-guard.py`,
  `update-home-crowdsec-whitelist.sh` and `migration-infra-watch.py` all
  retargeted; `ensure-arr-mcp-tunnel.sh` and `nasus-watchdog-setup.sh` archived
  as dead code.
- **`arr-mcp-tunnel.service`** forwarded to `NASUS:6060`, where nothing listens.
  Repointed to `jesus@192.168.0.12`; `http://127.0.0.1:16060/healthz` now returns
  `{"status":"ok","name":"arr-mcp","version":"1.70.0"}`.
- **Watchdog unit tests fixed** (`NASUS_SSH` → `RAMMUS_SSH`, retired `dash-nas`
  assertions removed, SSH host `.12`). 19 tests pass. The stale
  `.watchdog-state.json` was deleted so the next run does not send a false
  "all recovered" message.
- **Backups now take consistent SQLite copies.** `sqlite3` installed on rammus;
  after the rsync every `*.db` over 10 kB is rewritten with
  `sqlite3 <live> ".backup <dest>"`. Verified `scryer.db` and `prowlarr.db`
  report `integrity_check = ok`; the Plex library copy is readable with the same
  258 tables. Plex's own DB cannot be `integrity_check`ed by stock sqlite (custom
  tokenizer) and is not corrupt.
- The authoritative host pages were copied into the CloudNode repo clone
  (`/home/jesus/pangolin-stack`) so Hermes's repo-derived answers are correct.
  The branch itself is still uncommitted on the workstation.

### [2026-11-21] fixes | backup integrity and monitoring truth

Independent production review found two high-severity defect classes that the
migration itself did not cause but did expose. Both are fixed and regression
tested.

- **The SQLite snapshot step was overwriting backup history.** `cp -al` gives a
  dated snapshot the *same inode* as `opt-docker-latest`, and `rsync` leaves that
  link in place when it sees no change (Plex's library DB measured link count 2).
  `sqlite3 .backup $dest` then rewrote the file inside the kept snapshot, so
  "yesterday" silently became tonight's copy. Now writes `$dest.tmp` and
  `mv -f`s. Verified: a 2-link test pair split into two inodes with the old rows
  intact, and after a full backup run no `*.db` in `opt-docker-latest` shares an
  inode with any kept snapshot.
- **`migration-infra-watch` watched paths nothing writes to.** It read
  `/volume2/backups/configs/configs-*.tgz` (producer `config-backup` is stopped)
  and `/volume2/backups/scryer/*.enc` (that volume is not exported to rammus).
  It would have alerted at ~15:30 on 2026-11-22 and again the next morning.
  Now checks `/volume1/backups/rammus/rammus-etc-*.tar.gz`,
  `/volume1/backups/scryer/*.enc`, and the freshness/size of
  `opt-docker-latest`. The `find -printf` used for that age check is unsupported
  by ADM's `find` and reported a 56-year-old copy; replaced with
  `find -exec stat -c %Y`.
- **scryer's backup destination moved with the app.** `/backups` inside scryer is
  now `/volume1/backups/scryer`, which was empty while all history sat in the
  unexported `/volume2/backups/scryer`. History was copied across with `cp -p`,
  and write access from inside the container was proven by a probe file.
- **`olm-watchdog.sh` probed `.10`**, so any NASUS maintenance window looked like
  an Olm tunnel failure and would have restarted Olm, taking every home route
  down. Now `TARGET_IP=192.168.0.12` / `/_ping`. That endpoint answers `401`,
  which the script already accepts as reachable.
- **The qBittorrent API probe timeout was raised 15 s → 30 s.** A single SSH
  round trip under load produced a false `qBittorrent API unavailable`; the
  direct check returned `v5.3.0` both times it fired.
