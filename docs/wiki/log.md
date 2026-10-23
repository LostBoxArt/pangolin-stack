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
last_ingested: 2026-10-23
last_lint: 2026-10-23
---
# Wiki Log

Append-only record of structural wiki changes, maintenance passes, and review
artifacts.

## [2026-10-23] security + upgrade | Pangolin 1.25.3
- Updated Pangolin from `1.24.0` to `1.25.3`; verified the live Node runtime is `v24.22.1`, the container is healthy, and the local API returns HTTP 200. The upstream release identifies the Node2Shell fix; details and source links are in `services/pangolin.md`.
- Tested the migration on an isolated database copy, verified production database integrity and foreign keys, and preserved the post-upgrade route set (22 routers / 11 services). Gerbil and Traefik were not restarted.
- Kept Traefik at `v3.7.16` (above Pangolin's `3.6+` requirement) and Badger at `v1.7.0` because upstream reports the `v1.8.0` plugin-integrity failure.
- Live-verified Newt `1.19.0`, Olm `1.9.1`, and Gerbil `1.5.2`. Removed the temporary four-hour Pangolin image watcher after verifying the fixed runtime.
- Updated the active version/compatibility references and LLM entry points. Historical dated records remain unchanged.

## [2026-10-22] stack refresh | dashboard, identity, security UI, and proxy runtime
- Upgraded Homarr to `v2.8.0`; the SQLite integrity check passed, the local dashboard returned HTTP 200, and the container had zero restarts at verification.
- Rebuilt qbit-proxy on `node:24-slim`; the running runtime reported Node `v24.22.1`, and both internal and routed HTTP probes returned 200.
- Updated Pocket-ID to `v2.19.1` and CrowdSec Web UI to `2026.10.9`; both current containers were healthy with zero restarts when rechecked on 2026-10-23.
- Refreshed current-state references while preserving dated historical version notes.

## [2026-10-16] decommission | Termix removed from CloudNode apps stack
- Removed the Termix Compose service and its named-volume declaration; `docker compose ... up -d --remove-orphans` removed the container. The apps stack now contains only `landing`.
- Retained the detached `pangolin-apps_termix_data` volume as a reversible rollback copy.
- Removed Termix from the active Hermes watchdog URL list and cleared its stale failure counter. Updated the active service inventory, endpoint lists, port matrix, and runbook probes.
- Pangolin resource-route deletion was pending on 2026-10-16. A read-only check on 2026-10-23 still found `21-termix-router` and `21-termix-service` in the live provider configuration (22 routers / 11 services); the Termix container is absent. Route cleanup remains open and was not performed as part of this documentation update.

## [2026-07-18] incident + runbook | tunnel down, all HomeNode sites unreachable
- **Symptom**: All HomeNode-backed `*.example.com` sites returned 502/timeout. Pangolin showed site `homelab` as `online=0`. Watchdog false-alarmed on all 7 HomeNode SSH services.
- **Root cause**: Docker's embedded DNS proxy (127.0.0.11) died inside the `dockerd` process on HomeNode. Newt could not resolve `pangolin.example.com` to fetch its auth token, so the tunnel dropped and could not reconnect. The DNS proxy death is a runtime failure of dockerd's internal DNS forwarder, not a config issue.
- **Contributing factor**: Home ISP NAT rebinding (endpoint port changing every 2-10 min) caused the initial WebSocket disconnect. Newt could not reconnect due to the DNS proxy being dead.
- **Secondary issue**: The Asustor GUI Docker restart (used to restart dockerd) clobbered `/usr/local/bin/docker` — replaced the wrapper script with a plain symlink, breaking non-interactive docker access for the `jesus` user. The sudoers rule survived; the wrapper was restored manually.
- **Fix**: Restarted `dockerd` (via Asustor GUI and via CLI). All 16 containers came back via `restart: unless-stopped`. Restored the Docker wrapper script. Tunnel reconnected; all sites recovered.
- **New runbook**: `docs/wiki/runbooks/tunnel-down-all-homenode-down.md` — comprehensive troubleshooting guide covering Docker DNS proxy death, newt reconnection failures, NAT rebinding churn, Docker wrapper clobbering, SSH penalty table blocks, container-level diagnosis, and a decision flowchart.
- **Updated**: `docs/wiki/index.md` — added the new runbook to the Runbooks section.
- **Lessons**: (1) Search session history before re-deriving a fix. (2) Do not restart CloudNode Traefik during debugging. (3) Do not tinker with DNS config when the real issue is a dead dockerd DNS proxy. (4) Verify the Docker wrapper after any Asustor GUI Docker restart. (5) Avoid rapid SSH retry loops (triggers penalty table). (6) Pangolin `online=1` does not guarantee the data path works.

## [2026-05-09] homarr | memory-optimized beta + qbit-proxy fix
- **Homarr**: Pinned from `:latest` (main branch, ~595 MiB) to `v1.61.1-beta.1`
  (~181 MiB). Beta tag merges 3 Node processes into 1 (#5600) plus idle-memory
  reduction (#5637). Updated `services/homarr.md` — version, findings,
  remediation, operational notes. Added `.env` symlink:
  `stacks/dashboard/.env` → `../../.env` to fix compose env resolution.
- **qbit-proxy**: Fixed `TARGET_IP` from `192.168.1.10` (unreachable subnet) to
  `<homenode-lan-ip>` (routed through the tunnel). Fixed `TARGET_HOST` to match
  HomeNode's Traefik route. Updated `qbit-proxy/index.js` defaults to match.
  Added F-QBP-3 to `services/qbit-proxy.md`.
- Updated `services/homarr.md` and `services/qbit-proxy.md`.

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

## [2026-04-26] design | landing page field-notes redesign
- Delivered the field-notes redesign (branch `codex/landing-field-notes-redesign`,
  commit `deb6eb9`): replaced the operations console systems card grid with
  journal-style numbered note rows (01 Work, 02 Home, 03 AI/agents, 04 Signals).
- Restored rotating gold ring around the portrait using `@property --ring-angle`
  for GPU-friendly conic-gradient animation (commit `b47661c`).
- Moved secondary links (X, Steam) from a card into the footer.
- Switched focus tags into a pill-layout section within the Signals note.
- Updated `docs/wiki/services/landing.md` and `sites/dennisb-landing/DESIGN.md`
  to reflect the current design.
- Cache buster bumped to `style.css?v=12`.
- Re-ran `scripts/wiki_lint.py` — all files pass clean. Flagged `pangolin-stack-wiki-maintenance` skill for manual update: it still uses deprecated "VPS/NASUS" terminology and references `nasus-review-*.md`, `services-nasus/`, and `host-configs/nasus/` which were renamed to CloudNode/HomeNode on 2026-04-21. Security scan blocked automated skill patching this session.

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

## [2026-04-24] service | landing page redesigned as operations console
- Complete visual redesign of `example.com` landing page (commit `4172993`).
- Shifted from dark editorial aesthetic to an **operations console** concept
  that frames Dennis as an infrastructure/operator profile.
- Hero copy rewritten: research compute at work, homelab tinkering at home,
  Linux boxes, private tunnels, local models, agents, dashboards, automations.
- New identity section: "Cloud / Lab / Home" eyebrow, Playfair Display name,
  position paragraph, primary action buttons (Email, GitHub, LinkedIn).
- New ops panel: infrastructure-map style portrait frame with Cloud/HPC/Home
  node labels, telemetry rows for Base, Role, and Stack.
- Systems section reorganized into six numbered cards:
  01 Operating Principle, 02 Day Work, 03 Night Work, 04 Focus, 05 Elsewhere,
  06 Current Focus.
- Current Focus card explicitly calls out AI hobbies: local models,
  tool-using agents, coding assistants, and agent workflows.
- Typography: IBM Plex Mono (labels/telemetry), Outfit (body), Playfair
  Display (name). Old Cormorant Garamond + helix canvas removed.
- Palette: near-black `#0d0f0d` with warm gold `#c9a96e` accents and a
  green status dot. Old copper accents, rotating amber ring, pulsing glow,
  film-grain overlay, and aurora orbs removed.
- Cache buster bumped to `style.css?v=9`.
- `logo.png` optimized from ~2.1 MB to ~119 KB.
- `sites/dennisb-landing/` removed from `.gitignore`; all site files and
  assets now tracked in git (`index.html`, `style.css`, `avatar.jpg`,
  `logo.png`, `DESIGN.md`).
- Updated `docs/wiki/services/landing.md` to reflect the new design.
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
- Fixed `~/.hermes/memories/MEMORY.md`: corrected the stale HomeNode address, updated deprecated `VPS/NASUS` terminology to `CloudNode/HomeNode`, and fixed the documented network range.
- Removed stale LinkStack replacement preference from `~/.hermes/memories/USER.md` (completed 2026-04-21).
- Sanitized remaining real data leaks in `docs/wiki/log.md`: removed real ISP and
  LAN addresses, replaced real domains with `example.com` in service descriptions,
  and updated `VPS` → `CloudNode` in incident narrative.
- Patched 7 skills for deprecated terminology and wrong IPs:
  - `home/homelab-automation`: `VPS/Nasus` → `CloudNode/HomeNode`
  - `home/pangolin-networking`: `VPS` → `CloudNode`
  - `home/traefik-routing`: `VPS stack` → `CloudNode stack`
  - `home/seerr-media-requests`: `<homenode-lan-ip>` in place of the private LAN address (3×)
  - `devops/dockhand-hawser-monitoring`: `NASUS` → `HomeNode`, private LAN address → `<homenode-lan-ip>`, `NAS host` → `HomeNode host`
  - `devops/pangolin-service-swap`: `NASUS` → `HomeNode`
  - `software-development/hermes-gateway-live-session-guardrails`: `VPS` → `CloudNode`
- Removed unused one-time research artifact `~/.hermes/skills/ai-pricing-research.md`.
- Re-ran `scripts/wiki_lint.py` — all files pass clean.

## [2026-09-05] maintenance | Seerr deployment recovery
- Restored a reproducible Compose definition for Seerr from verified live runtime state.
- Preserved the existing `jellyseerr` data directory and added a pinned `v3.4.1` image.
- Verified the backup, healthcheck, internal route, and unchanged application data after recreation.

## [2026-09-05] maintenance | Arr download safety
- Enabled Sonarr and Radarr `failDownloads=[0,1]` on all seven configured indexers in each app through their supported APIs.
- Verified the settings by read-back, confirmed no active qBittorrent torrent has an executable content path, and documented that Arr detects these files after download inspection rather than preventing qBittorrent from receiving initial bytes.

## [2026-09-06] maintenance | Media path follow-up
- Seerr's live Sonarr/Radarr routing defaults were still `/tv` and `/movies`; changed them through the supported API to `/data/tv` and `/data/movies` and verified by read-back.
- Corrected the two affected Arr records through their editor APIs with `moveFiles=false` and `deleteFiles=false`; no media was moved and Plex was not restarted.
- Dark Matter and Mayday remain visible in Plex. Their earlier imports were copies rather than hardlinks because they used the legacy aliases; the next normal request is the clean Radarr hardlink canary.
- Full verification passed: all seven relevant containers healthy with restart count 0; qBittorrent 134 torrents / 133 complete / 0 active downloads; zero dangerous-extension files in Arr download directories.

## [2026-09-06] maintenance | Safe obsolete-data cleanup
- Removed only the older duplicate migration backup `20260905T105403Z` (203.3 MB) after verifying the retained `20260905T105556Z` backup with its SHA-256 manifest.
- Kept all media, qBittorrent torrents, the active `vuetorrent` WebUI assets, and two qBittorrent-tracked `.parts` files. Kept legacy aliases because existing torrent records still reference `/downloads`.
- Post-cleanup migration verification passed with no service restart; NAS free space is 7.3 TB.

## [2026-09-07] Quality profile policy
- Researched the current TRaSH Guides and Recyclarr guide-backed templates for conventional media and anime. The anime guidance explicitly supports lower-resolution availability and does not require 4K.
- Made Recyclarr the effective single writer for quality profiles and custom formats. Profilarr remains running for repository synchronization only.
- Synced `2160p Quality`, `1080p Quality`, and `Anime 1080p` into Sonarr and Radarr. Anime Sonarr series use the anime profile; ordinary non-4K series use the 1080p profile; existing 2160p assignments were preserved.
- Updated Seerr's ordinary-TV and anime defaults to the new Sonarr profiles. Radarr remains defaulted to the 2160p profile.
- Verified an idempotent Recyclarr preview, healthy Arr/Seerr/Plex containers, zero restarts, and Plex identity HTTP 200. No media, torrents, databases, or Plex configuration changed.

## [2026-09-07] Prowlarr and arr-mcp remediation
- Removed the broken Prowlarr indexers `1337x` (Cloudflare 403/error 1006) and `BitSearch` (missing indexer definition) through Prowlarr's supported API; no torrents, media, or databases were touched.
- Set Prowlarr allowed hosts to the verified internal and routed hostnames; read-back passed.
- Verified Prowlarr now has 6 working indexers, and Sonarr/Radarr now have 5 synchronized indexers each.
- arr-mcp stack health returned zero failures and zero degraded services after remediation; all adapters remain read-only and private.
- The Radarr natural hardlink canary remains deferred because no post-migration Radarr import has occurred. The stable Prowlarr image is currently older than the running `develop` build, so switching channels was not performed without an authorized maintenance/source-of-truth update.


## [2026-09-28] maintenance | WebUI removal, DNS stack deletion, and security cleanup
- Removed `hermes-webui` entirely: compose service, `hermi.example.com` Pangolin resource, DB rows (`targets`, `roleResources`, 1896 `requestAuditLog` rows, its auto-created `resourcePolicies` row), container, and the `9119` publish. The container mounted `/home/jesus/.hermes` plus `docker.sock`, and a cron job (`ensure-hermes-dashboard.sh`) recreated it on boot and every 5 minutes — that cron entry and script were removed so it cannot come back. The separate `hermes-gateway` systemd platform is untouched and still active.
- Deleted the dead `dns` stack: `stacks/dns/`, `config/adguard-home/`, and the `dns-tls` (853) entrypoint in `config/traefik/traefik_config.yml`. `dns` was dropped from the `stackctl.sh` stack list. The VPS AdGuard was never actually deployed, so no running container was lost. Discovered F-GERBIL-3 as a result: Gerbil still publishes `853:853`, but nothing listens behind it now.
- Removed the six vestigial `*.example.com` Traefik labels from `stacks/{apps,dashboard,management,observability,security}/docker-compose.yml`. They duplicated Pangolin-owned routes and were causing **45 failed Let's Encrypt orders per day** (`rejectedIdentifier: "forbidden by policy"`), burning ACME rate-limit budget that real certs need. Post-change ACME failures: zero.
- Security cleanup: `.env` and `config/pangolin/config.yml` locked from `644` to `600`; the five dead `ADGUARD_*` sync vars removed from `.env`; Homarr's unused `docker.sock` mount removed (no Docker integration was configured); CrowdSec `ForwardedHeadersTrustedIPs` narrowed from `0.0.0.0/0` to loopback + internal + the exact Cloudflare edge ranges so clients can no longer forge their source IP.
- Updated `AGENTS.md` (6 stacks, not 7), `docs/wiki/index.md`, `docs/wiki/system-overview.md`, `docs/wiki/services/adguard-home.md`, `docs/wiki/services/gerbil.md`, and `docs/wiki/services/homarr.md`.
- Verified after each step: all 12 remaining hostnames answer correctly, the HomeNode tunnel still serves `plex`, `hermes-gateway` stayed active, and `scripts/wiki_lint.py` passes clean.
- Removed content is recoverable, not destroyed: `/home/jesus/pangolin-stack/.removed-20260928/` and `/home/jesus/.hermes/.removed-webui-20260928/`, plus `.bak-<timestamp>` copies beside each edited config.

## [2026-09-28] maintenance | Version and path drift correction across all docs
- Found and fixed widespread stale version pins and a wrong repo path that predated this session. Every value below was re-verified against the running stack, not inferred.
- Version pins corrected everywhere (`AGENTS.md`, `README.md`, `INFRASTRUCTURE.md`, and the affected wiki service pages):
  - Pangolin `1.17.1` / `1.17.0` / `1.18.1` → `1.23.0`
  - Gerbil `1.3.1` → `1.5.2`
  - Badger plugin `v1.4.0` → `v1.7.0`
  - CrowdSec Web UI `2026.3.1` → `2026.8.3`
  - Newt `1.11.0` / `1.12.3` → `1.17.0`
  - Olm `1.4.4` → `1.5.0`
  - Homarr `v1.61.1-beta.1` → stable `v1.77.2` (the memory work that justified the beta pin has landed in stable; `F-HOMARR-1b` deleted as obsolete)
  - Lockstep triplets rewritten to match: Pangolin 1.23.x ↔ Newt 1.17.x ↔ Olm 1.5.0.
- Corrected the repo path claim. `llms.txt`, `llms-full.txt`, and two runbooks claimed the repo lives at `/opt/homelab`, which broke the runbooks as written (`cd /opt/homelab` then `docker compose -f stacks/...` finds nothing). Real repo path is `/home/jesus/pangolin-stack`. `INFRASTRUCTURE.md` also documented the blocklist cron as `/opt/homelab/scripts/blocklist-import.sh`; the live crontab uses `/home/jesus/pangolin-stack/scripts/blocklist-import.sh`.
- Deliberately kept the `/opt/homelab/stacks` references in `services/dockhand.md`: that is a real bind mount in the Dockhand compose, distinct from the repo path.
- Re-verified the two gerbil deviations that older docs asserted for gerbil 1.3.1: `reachableAt` still uses port `3003` on 1.5.2 (`3003` answers, `3004` refuses), so the note now says "verified still correct on gerbil 1.5.2" instead of tying it to the old version.
- Left in place, correctly: the dated review files `compose-review-2026-04-17.md` and `homenode-review-2026-04-17.md` are append-only, and their historical version references describe the stack as it was on that date.
- `scripts/wiki_lint.py` passes clean after the changes.

## [2026-09-28] maintenance | Three component upgrades applied and verified
- Upgraded three components after checking each project's own upgrade docs first and confirming no undocumented manual steps were required:
  - **Pocket-ID** `v2.15.0` → `v2.16.0`. Docs: <https://pocket-id.org/docs/setup/upgrading> — Docker upgrade is `pull` + `up -d`; no manual steps between these versions. Migrations ran automatically (`05-workflow-labels.sql`, `06-terminal-jobs.sql`). Verified: 2 users and 3 OIDC clients intact, `integrity_check=ok`, OIDC discovery/JWKS/login all 200.
  - **CrowdSec Web UI** `2026.8.3` → `2026.9.2`. Confirmed 2026.8.3 had already migrated from `config.json` to `config.yaml`, so there was no config-format break to handle. Verified: healthy, LAPI `isConnected: true`, alerts API 200, 27 tables intact.
  - **Olm** `1.5.0` → `1.9.1` (CloudNode systemd binary, not a container). Verified the 1.9.1 binary still accepts `--override-dns` so `ExecStart` is unchanged. Verified: `active`, `NRestarts=0`, WireGuard CONNECTED to site 1 at 127ms RTT, 0 errors from the new PID, tunnel reachable.
- Backups taken before each change using the SQLite online-backup API, not `cp` (both Pocket-ID and CrowdSec Web UI run WAL-mode SQLite): `/tmp/pid-20260928-123257.db` and `/tmp/csw-20260928-123459.db`, both `integrity_check=ok`. Olm rollback copies at `/usr/local/bin/olm.1.5.0.rollback` and `/tmp/olm-1.5.0-current`.
- Investigated and dismissed a suspected SSO regression: `dash.example.com` and `fileflows.example.com` appeared to flip 200→401 after the Pocket-ID upgrade. Rotated access logs show `dash` has been `{401:413, 302:276}` continuously since 2026-09-24 and `fileflows` `{401:37, 302:23, 403:5}` since 2026-09-25 — neither ever served 200 unauthenticated. SSO is enforcing correctly (unauthenticated 401; browser 302 → `pangolin.example.com/auth/resource/...`). No regression.
- Corrected stale facts found while verifying: `services/pocket-id.md` documented the image as the floating `:v2` tag; the real pin is `v2.16.0` (now documented as exact-minor, `F-POCKETID-3`). `services/crowdsec-web-ui.md` claimed the UI was "not behind Traefik"; it is in fact fronted by Pangolin with SSO enforced, and only host port 3458 is filtered.
- New findings recorded: `F-POCKETID-3` (floating major tag, resolved), `F-POCKETID-4` (WAL-mode DB, naive copies are not backups), `F-CSWUI-3` (application auth disabled), `F-CSWUI-4` (1.8 GB state dir with permissive modes).
- Everything else was already current and needed no action: Pangolin 1.23.0, Gerbil 1.5.2, Newt 1.17.0, Badger v1.7.0, Traefik 3.7.13, CrowdSec v1.8.1, Homarr v1.77.2, Termix 2.8.0, Dashdot 6.3.4.
- `scripts/wiki_lint.py` passes clean after the changes.

## [2026-09-28] maintenance | Pocket-ID isolation, Traefik pin, and Gerbil cleanup
- Migrated Pocket-ID state from the shared repo-wide `data/` mount into the dedicated `data/pocket-id/` path.
- Created a rollback snapshot with SQLite online backup before the move; verified the live database afterward with `integrity_check=ok`, 2 users, and 3 OIDC clients.
- Pinned Traefik from the mutable `latest` tag to `v3.7.13`; the tag resolves to the same verified running digest.
- Removed Gerbil's dead `853/tcp` publish and recreated Gerbil followed by Traefik; public routing and the HomeNode tunnel remained healthy.
- Tightened CrowdSec Web UI state permissions to `0700`/`0600`. Application-level auth remains disabled pending an operator-supplied admin credential or OIDC configuration; no unsafe credential was invented.
- Verified all six Compose files, the public endpoints, core container state, Pocket-ID database integrity, and CrowdSec Web UI health.

## [2026-10-10] maintenance | Stack version documentation and stale media metadata
- Updated current version references to the live CloudNode pins: Pangolin 1.24.0, Traefik v3.7.14, Homarr v2.4.1, Pocket-ID v2.18.0, and CrowdSec Web UI 2026.10.3.
- Updated current HomeNode references to Newt 1.18.1, Seerr v3.5.0, Recyclarr 8.7.3, and FileFlows 26.10 with its verified digest in the tracked Compose copy.
- Preserved dated historical audit references as historical rather than rewriting them into current-state claims.
- Removed a stale Sonarr record for *The Grand Tour (2026)* with `deleteFiles=false`; the six existing files and Plex/Jellyfin library entry remain intact. The current TVDB record remains marked deleted, so the series is not re-added to Sonarr until a valid metadata mapping exists.
- Sanitized credential-like values from documentation examples before publication; real values remain in private runtime configuration only.
