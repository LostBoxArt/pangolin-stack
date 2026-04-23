---
title: "Pangolin Stack — Internal Wiki"
slug: wiki-readme
type: index
status: active
tags: ["homelab", "wiki", "index"]
aliases: ["wiki", "pangolin stack wiki"]
entities:
  primary: wiki-readme
  mentions: []
related: ["./system-overview.md", "./maintenance-workflow.md", "./index.md"]
sources: ["AGENTS.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-21
---
# Pangolin Stack — Internal Wiki

Living knowledge base captured while reviewing each compose file in this repo
against upstream documentation and reference compose files.

The goal of this wiki is to be **one click away from the right upstream
source** for every service we run, and to record any deviation we've made so
future agents (or future-you) don't have to rediscover the reasoning.

Coverage spans **two hosts**:

- **CloudNode** (`203.0.113.1`) — public edge: Pangolin, Traefik, CrowdSec, etc.
  Compose files live in this repo under `stacks/`.
- **HomeNode** (`192.168.1.10`) — home lab: *arr stack, Plex, torrent client,
  etc. Compose files live on HomeNode at `/volume1/docker/config/*/` and
  `/volume1/docker/{traefik,hawser}/`. Source-controlled copies live in
  `host-configs/homenode/` (currently incomplete — see the HomeNode audit).

---

## Start Here

- [System Overview](./system-overview.md) — high-level architecture, startup
  order, public endpoints, critical operational rules, and repo layout.
- [Maintenance Workflow](./maintenance-workflow.md) — how agents should ingest,
  answer from, lint, and update this wiki.
- [LLM Wiki Pattern](./llm-wiki-pattern.md) — design notes for how this wiki
  adopts current LLM-wiki and `llms.txt` best practices.
- [Compose Review 2026-04-17](./compose-review-2026-04-17.md) — current latest
  CloudNode audit; if a newer `compose-review-*.md` exists, use that instead.
- [HomeNode Review 2026-04-17](./homenode-review-2026-04-17.md) — current latest
  HomeNode audit; if a newer `homenode-review-*.md` exists, use that instead.
- [Index](./index.md) — flat content catalog of the current wiki.
- [Glossary](./glossary.md) — compact definitions for recurring homelab terms.
- [Wiki Log](./log.md) — append-only maintenance log for wiki updates, audits,
  and structural changes.
- [llms.txt](./llms.txt) — machine-oriented manifest for agents.
- [llms-full.txt](./llms-full.txt) — compact compiled context file for agents
  that need the wiki map and top operational rules in one read.


## Per-Service Pages

Each page follows the same structure:

- **Role** — what this service does in the stack
- **Upstream source** — link(s) to official docs / reference compose
- **Our compose** — file + service name in this repo
- **Deviations from upstream** — what we changed and why
- **Findings** — optimization opportunities, bugs, drift risks
- **Remediation** — concrete diff-level fixes

## Supporting Pages

- [Index](./index.md) — flat catalog of all current wiki pages.
- [Glossary](./glossary.md) — recurring homelab terms and shorthand.
- [Hosts](./hosts/cloudnode.md) / [HomeNode host](./hosts/homenode.md) — host-level summaries.
- [Networks](./networks/pangolin.md) and [traefik_traefik](./networks/traefik-traefik.md) — current network model.
- [Runbooks](./runbooks/recreate-traefik-after-gerbil.md) and peers — operator procedures grounded in existing wiki facts.

## CloudNode — `stacks/`

### Core (`stacks/core/docker-compose.yml`)

- [pangolin](./services/pangolin.md)
- [gerbil](./services/gerbil.md)
- [traefik](./services/traefik.md)
- [badger](./services/badger.md)
- [olm](./services/olm.md)

### Security (`stacks/security/docker-compose.yml`)

- [crowdsec](./services/crowdsec.md)
- [crowdsec-web-ui](./services/crowdsec-web-ui.md)
- [pocket-id](./services/pocket-id.md)

### Observability (`stacks/observability/docker-compose.yml`)

- [traefik-log-dashboard](./services/traefik-log-dashboard.md) (agent + UI)
- [dashdot](./services/dashdot.md)

### Management (`stacks/management/docker-compose.yml`)

- [dockhand](./services/dockhand.md)

### Dashboard (`stacks/dashboard/docker-compose.yml`)

- [homarr](./services/homarr.md)
- [qbit-proxy](./services/qbit-proxy.md)

### Apps (`stacks/apps/docker-compose.yml`)

- [landing](./services/landing.md)
- [termix](./services/termix.md)

> Historical: [linkstack](./services/linkstack.md) was replaced by `landing` on 2026-04-21.

## HomeNode — `/volume1/docker/`

Live compose files on HomeNode are under `/volume1/docker/config/<service>/`,
`/volume1/docker/traefik/`, and `/volume1/docker/hawser/`. Source-controlled
copies live under `host-configs/homenode/`, but coverage is still incomplete. See
`docs/wiki/homenode-review-2026-04-17.md` finding `NM1`.

### Edge / Tunnel
- [traefik (HomeNode)](./services-homenode/traefik.md)
- [hawser](./services-homenode/hawser.md)
- [newt](./services-homenode/newt.md)

### *arr suite
- [sonarr](./services-homenode/sonarr.md)
- [radarr](./services-homenode/radarr.md)
- [bazarr](./services-homenode/bazarr.md)
- [prowlarr](./services-homenode/prowlarr.md)
- [profilarr](./services-homenode/profilarr.md)
- [recyclarr](./services-homenode/recyclarr.md)

### Torrent
- [qbittorrent](./services-homenode/qbittorrent.md)
- [qui](./services-homenode/qui.md)
- [flaresolverr](./services-homenode/flaresolverr.md)
- [cleanuparr](./services-homenode/cleanuparr.md)

### Media
- [plex](./services-homenode/plex.md)
- [seerr](./services-homenode/seerr.md)

### Observability
- [dashdot (HomeNode)](./services-homenode/dashdot.md)

### HomeNode-specific operating notes
- HomeNode services all share one external Docker network: `traefik_traefik`.
- Sync direction is **HomeNode -> repo**, never repo -> HomeNode.
- When touching a HomeNode service, update the live HomeNode file,
  `host-configs/homenode/<service>/docker-compose.yml`, and the matching
  `docs/wiki/services-homenode/<service>.md` together.

---

## Conventions Used in This Wiki

- **Severity legend**:
  - `critical` — data-loss, security, or outage risk.
  - `high` — functional drift from upstream that can break on next release.
  - `medium` — hardening / best-practice deviations.
  - `low` — cosmetic or nice-to-have.
- **Upstream pin policy** (from `AGENTS.md`): services with release cadence
  that matters for us (Pangolin, Gerbil, Newt, Olm, Badger, CrowdSec Web UI)
  are pinned to exact versions. Everything else historically uses `:latest`,
  which this review flags as drift risk.
- All file paths are relative to repo root unless otherwise noted.

## When to Update This Wiki

- After any compose-file change, update the matching service page.
- After a review session like 2026-04-17, add a dated review document rather
  than editing the old one in place — keeps an audit trail.
- Service added / removed → add or archive its page and update the TOC above.


## Wiki Tooling

- Mechanical lint script: `scripts/wiki_lint.py`
- Current job: check frontmatter, broken links, duplicate slugs, missing service entries in `index.md`, and required top-level entry points.
- Semantic health checks should additionally look for stale upstream references,
  conceptual gaps, contradictions, and missing source-page coverage for new
  external material.


## Knowledge Layers

- Concepts: `docs/wiki/concepts/*.md`
- Decisions: `docs/wiki/decisions/*.md`
- Hosts: `docs/wiki/hosts/*.md`
- Networks: `docs/wiki/networks/*.md`
- Runbooks: `docs/wiki/runbooks/*.md`
