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
last_ingested: 2026-11-21
last_lint: 2026-11-21
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

### Rammus
- LAN IP: `192.168.0.12`
- Role: **every** application workload (media, torrent, *arr, tunnel, edge proxy)
- Live compose files: `/opt/docker/stacks/<service>/docker-compose.yml`
- Appdata: `/opt/docker/config/<service>`, always on local SSD
- Dedicated page: `docs/wiki/hosts/rammus.md`
- This host is a single point of failure: one SSD, no RAID.

### HomeNode (NASUS)
- LAN IP: `192.168.0.10`
- Role: NFS storage only — **zero Docker containers** since 2026-11-21
- Exports `/volume1/{media,storage,backups}` and `/volume2/fast` over NFSv3
- Dedicated page: `docs/wiki/hosts/homenode.md`
- Service pages under `docs/wiki/services-homenode/` now describe the layout as
  it ran before the move; treat them as history.

## Architecture

Traffic flow:

`Internet -> Cloudflare -> CloudNode -> Traefik -> services`

Control and tunnel flow:
- Pangolin is the control plane.
- Gerbil is the WireGuard relay on the CloudNode.
- Olm on the CloudNode and Newt on rammus provide reachability to `192.168.0.0/24`.
- Traefik runs with `network_mode: service:gerbil`, so 80/443 live in the
  Gerbil container namespace.

## Stack Layout on the CloudNode

### Core
- `pangolin` — control plane
- `gerbil` — relay and edge port owner
- `olm` — WireGuard endpoint for LAN reachability
- `badger` — Traefik CrowdSec bouncer plugin
- `traefik` — reverse proxy

### Security
- `crowdsec`
- `crowdsec-web-ui`
- `pocket-id`

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

### Historical note
- `adguard-home` was removed from the CloudNode on 2026-04-21 and is not part
  of the active stack layout.

## Rammus Service Layout

All rammus services share one external Docker network: `traefik_traefik`
(subnet `172.19.0.0/16`). There is no stack separation like on the CloudNode.

### Edge / Tunnel
- `traefik` — public 80/443, `traefik:3.7.17` pinned
- `newt` — the only tunnel for `192.168.0.0/24`
- `hawser` — Dockhand agent, token required

### *arr / acquisition
- `prowlarr`
- `scryer`
- `arr-mcp`

### Torrent
- `qbittorrent`

### Media
- `plex`

### Observability
- `dashdot` (`dash.example.com`, port 3003)

### DNS
LAN name resolution is not on rammus. AdGuard Home runs as a plugin on the
OPNsense router and holds explicit rewrites for each service name, all pointing
at `192.168.0.12`. There is no wildcard, so a new service needs both a Traefik
route and an AdGuard rewrite.

## Startup Order

1. `core`
2. `security`, `management`
3. `observability`, `dashboard`, `apps`

All non-core stacks use the external `pangolin` Docker network.

## Public Endpoints

- `https://pangolin.example.com`
- `https://crowdsec.example.com`
- `https://auth.example.com`
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

5. **Live host first, then repo.**
   Application changes go to rammus (`/opt/docker/stacks/`) first, then the repo
   copy, then the matching wiki page. NASUS changes should be avoided entirely
   unless they concern NFS exports or ADM itself.

6. **Two-host rules that must not be broken.**
   `newt` may run on only one host: a duplicate client on the same site
   credentials flaps the tunnel and causes intermittent 502s. `plex` may run on
   only one host, because both instances would share `MachineIdentifier` and
   corrupt library state. Both are enforced today by `restart=no` on the stopped
   NASUS copies.

7. **Keep an audit trail.**
   New review sessions should create a new dated review file instead of editing
   prior audits in place.

## Current High-Priority Findings

### CloudNode
- `C1` / `F-POCKETID-1`: Pocket-ID mounts the shared repo `data/` directory.
- `H1` / `F-TRAEFIK-1`: Traefik image is still `:latest` instead of pinned.
- `H2`: CrowdSec Traefik log mount should be read-only.

### HomeNode (historical, mostly resolved by the 2026-11-21 migration)
- `NC1` / `F-N-TRAEFIK-1`: the old NASUS Traefik exposed its dashboard on
  `:9080` with `--api.insecure=true`. That Traefik is stopped; rammus publishes
  only 80/443.
- `NC2` / `F-N-HAWSER-1`: Hawser could fall back to an empty token while
  publishing its Docker API proxy. On rammus the token is set, the port is bound
  to `192.168.0.12` only, and unauthenticated requests return `401`.
- `NH2` / `F-N-TRAEFIK-2`: Traefik was `:latest`. It is now pinned to
  `traefik:3.7.17`.
- `NM1`: `host-configs/homenode/` tracks only a subset of the live compose
  files. The authoritative copies are now `/opt/docker/stacks/*` on rammus.
- **New gap:** no availability or certificate-expiry alerting exists. Nothing
  notifies anyone if rammus goes down, a disk fills, the NFS mount disappears, or
  ACME renewal starts failing.

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
