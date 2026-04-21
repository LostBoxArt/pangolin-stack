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
last_ingested: 2026-04-17
last_lint: 2026-04-18
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
- Complete visual redesign of `dennisb.xyz` landing page following Anthropic's
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
  (`dennisb.xyz` → `example.com`, `192.168.0.x` → `192.168.1.x`, `NASUS` → `HomeNode`,
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

