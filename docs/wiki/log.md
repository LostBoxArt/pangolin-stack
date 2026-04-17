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
sources: ["docs/wiki/README.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# Wiki Log

Append-only record of structural wiki changes, maintenance passes, and review
artifacts.

## [2026-04-17] bootstrap | initial service audit
- Added the first dated compose review at
  `docs/wiki/compose-review-2026-04-17.md`.
- Added VPS service pages under `docs/wiki/services/`.
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
  to NASUS pages that are not yet present in the repo.

## [2026-04-17] structure | NASUS namespace ingestion and machine entry-point refresh
- Updated `docs/wiki/README.md` to include the NASUS service TOC and NASUS review link.
- Updated `docs/wiki/system-overview.md` to reflect current dual-host coverage and NASUS operational rules.
- Refreshed `docs/wiki/maintenance-workflow.md` for `services-nasus/` pages and NASUS live-host sync rules.
- Refreshed `docs/wiki/llms.txt` and `docs/wiki/llms-full.txt` so machine entry points cover both VPS and NASUS.
- Added namespace guidance to `docs/wiki/llm-wiki-pattern.md` for duplicate service names across hosts.

## [2026-04-17] structure | phase-1 schema groundwork
- Added `docs/wiki/index.md` as a flat content catalog for agents and humans.
- Added `docs/wiki/glossary.md` for repeated homelab term disambiguation.
- Added frontmatter to existing wiki pages so typed metadata is now available across the current corpus.
- Refreshed top-level entry points so `README.md`, `llms.txt`, `llms-full.txt`, and `system-overview.md` reference the new index/glossary layer.

## [2026-04-17] structure | hosts networks runbooks and lint foundation
- Added host pages for the VPS and NASUS under `docs/wiki/hosts/`.
- Added network pages for `pangolin` and `traefik_traefik` under `docs/wiki/networks/`.
- Added foundational runbooks for Gerbil/Traefik recreation, Pocket-ID data migration, and Olm reachability checks under `docs/wiki/runbooks/`.
- Added `scripts/wiki_lint.py` for mechanical wiki checks and refreshed entry-point pages to reference the new structure.

## [2026-04-17] maintenance | lint-safe research note and NASUS cross-link cleanup
- Added complete frontmatter metadata to `docs/wiki/llm-wiki-research-and-best-practices.md` and converted raw placeholder wikilink examples to lint-safe placeholder syntax.
- Fixed the `services-nasus/recyclarr.md` cross-link so it points cleanly to `profilarr.md` without a broken anchor.
- Re-ran `scripts/wiki_lint.py` and cleared all reported issues.

## [2026-04-17] structure | concept and decision layer seed
- Added `docs/wiki/concepts/port-matrix.md` as the first cross-cutting topology concept page.
- Added initial decision records for version pinning, VPS Traefik/Gerbil namespace sharing, and NASUS live-first sync workflow.
- Refreshed `index.md`, `README.md`, `llms.txt`, `llms-full.txt`, and `system-overview.md` to expose the new knowledge-layer pages.

