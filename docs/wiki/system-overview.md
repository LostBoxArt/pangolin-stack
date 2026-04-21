---
title: "System Overview"
slug: system-overview
type: concept
status: active
tags: ["homelab", "overview", "topology"]
aliases: ["overview"]
entities:
  primary: system-overview
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./homenode-review-2026-04-17.md"]
sources: ["AGENTS.md", "docs/wiki/compose-review-2026-04-17.md", "docs/wiki/homenode-review-2026-04-17.md"]
confidence: medium
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# System Overview

High-level map of the Pangolin homelab as documented in this repo.

This page is the fastest way to understand the topology before drilling into
service pages under `docs/wiki/services/`.

## Hosts

### CloudNode
- Public IP: `203.0.113.1`
- Role: public edge and control plane
- Source of truth in this repo: compose files under `stacks/`

### HomeNode
- LAN IP: `192.168.1.10`
- Role: home-lab applications and media stack
- Live compose files: `/volume1/docker/config/*/docker-compose.yml` plus
  `/volume1/docker/traefik/docker-compose.yml`
- Source-controlled backup copies: `host-configs/homenode/`
- This wiki now has dedicated HomeNode service pages under
  `docs/wiki/services-homenode/`.

## Architecture

Traffic flow:

`Internet -> Cloudflare -> CloudNode -> Traefik -> services`

Control and tunnel flow:
- Pangolin is the control plane.
- Gerbil is the WireGuard relay on the CloudNode.
- Olm on the CloudNode and Newt at home provide reachability to `192.168.1.0/24`.
- Traefik runs with `network_mode: service:gerbil`, so 80/443 live in the
  Gerbil container namespace.

## Stack Layout on the CloudNode

### Core
- `pangolin` — control plane
- `gerbil` — relay and edge port owner
- `olm` — WireGuard endpoint for LAN reachability
- `traefik` — reverse proxy

### Security
- `crowdsec`
- `crowdsec-web-ui`
- `pocket-id`

### DNS
- ~~`adguard-home`~~ — **Removed 2026-04-21**. iPhone uses `1.1.1.1` directly. Config preserved at `./config/adguard-home/`.

### Observability
- `traefik-log-dashboard`
- `dashdot`

### Management
- `dockhand`

### Dashboard
- `homarr`
- `qbit-proxy`

### Apps
- `landing`
- `termix`

## HomeNode Service Layout

All HomeNode services share one external Docker network: `traefik_traefik`.
There is no stack separation like on the CloudNode.

### Edge / Tunnel
- `traefik`
- `hawser`
- `newt`

### *arr suite
- `sonarr`
- `radarr`
- `bazarr`
- `prowlarr`
- `profilarr`
- `recyclarr`

### Torrent
- `qbittorrent`
- `qui`
- `flaresolverr`
- `cleanuparr`

### Media
- `plex`
- `seerr`

### Observability
- `dashdot`

## Startup Order

1. `core`
2. `security`, `management`, `dns`
3. `observability`, `dashboard`, `apps`

All non-core stacks use the external `pangolin` Docker network.

## Public Endpoints

- `https://pangolin.example.com`
- `https://crowdsec.example.com`
- `https://auth.example.com`
- `https://dns.example.com`
- `https://dockhand.example.com`
- `https://home.example.com`
- `https://dash.example.com`
- `https://traefik-logs.example.com`
- `https://termix.example.com`
- `https://example.com`

## Critical Operational Rules

1. **Pinned components stay pinned.**
   Pangolin, Gerbil, Newt, Olm, Badger, and CrowdSec Web UI must remain
   version-pinned. See `AGENTS.md` and the relevant service pages.

2. **If Gerbil is recreated, Traefik must be recreated afterward.**
   Traefik shares Gerbil's network namespace. If Gerbil changes container ID,
   Traefik can stay attached to the dead namespace and silently break 80/443.
   See `docs/wiki/services/traefik.md`.

3. **Pocket-ID data must not share the repo-wide `data/` directory.**
   This is the current critical data-layout bug. See
   `docs/wiki/services/pocket-id.md` and
   `docs/wiki/compose-review-2026-04-17.md`.

4. **Answer from the wiki first.**
   For covered services, use the relevant service page before re-researching.
   The deviations table explains why the compose differs from upstream.

5. **HomeNode changes flow live host first.**
   For HomeNode, update the live file on HomeNode first, then sync the repo copy under
   `host-configs/homenode/`, then update the matching `services-homenode` wiki page.

6. **Known HomeNode compromise-risk surfaces stay visible until fixed.**
   `NC1` is the open Traefik dashboard on `:9080`. `NC2` is Hawser's empty-token
   fallback. See `docs/wiki/homenode-review-2026-04-17.md`.

7. **Keep an audit trail.**
   New review sessions should create a new dated review file instead of editing
   prior audits in place.

## Current High-Priority Findings

### CloudNode
- `C1` / `F-POCKETID-1`: Pocket-ID mounts the shared repo `data/` directory.
- `H1` / `F-TRAEFIK-1`: Traefik image is still `:latest` instead of pinned.
- `H2`: CrowdSec Traefik log mount should be read-only.

### HomeNode
- `NC1` / `F-N-TRAEFIK-1`: HomeNode Traefik dashboard is exposed on `:9080` with `--api.insecure=true`.
- `NC2` / `F-N-HAWSER-1`: Hawser can fall back to an empty token while publishing its Docker API proxy.
- `NH2` / `F-N-TRAEFIK-2`: HomeNode Traefik is still `:latest` instead of pinned.
- `NM1`: `host-configs/homenode/` tracks only 8 of 16 live HomeNode compose files.

See `docs/wiki/compose-review-2026-04-17.md` and `docs/wiki/homenode-review-2026-04-17.md` for remediation order.

## Where To Go Next

- Repo-wide usage and structure: `docs/wiki/README.md` and `docs/wiki/index.md`
- Agent maintenance rules: `docs/wiki/maintenance-workflow.md`
- LLM-oriented design rationale: `docs/wiki/llm-wiki-pattern.md`
- Audit findings: `docs/wiki/compose-review-2026-04-17.md` and `docs/wiki/homenode-review-2026-04-17.md`
- Host details: `docs/wiki/hosts/*.md`
- Network details: `docs/wiki/networks/*.md`
- Concepts: `docs/wiki/concepts/*.md`
- Decisions: `docs/wiki/decisions/*.md`
- Runbooks: `docs/wiki/runbooks/*.md`
- CloudNode service details: `docs/wiki/services/<service>.md`
- HomeNode service details: `docs/wiki/services-homenode/<service>.md`
