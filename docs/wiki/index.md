---
title: "Wiki Index"
slug: wiki-index
type: index
status: active
tags: ["homelab", "wiki", "index"]
aliases: ["content index"]
entities:
  primary: wiki-index
  mentions: []
related: ["./README.md", "./log.md", "./glossary.md"]
sources: ["docs/wiki/README.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-21
---

# Wiki Index

Flat catalog of the current wiki contents. This is the fastest content map for both humans and agents.

## Entry Points
- [`Pangolin Stack — Internal Wiki`](./README.md) — Living knowledge base captured while reviewing each compose file in this repo against upstream documentation and reference compose files.
- [`System Overview`](./system-overview.md) — High-level map of the Pangolin homelab as documented in this repo.
- [`Maintenance Workflow`](./maintenance-workflow.md) — How agents should maintain and use this wiki.
- [`LLM Wiki Pattern for This Homelab`](./llm-wiki-pattern.md) — This page records the design principles adopted from current LLM-wiki and LLM-friendly documentation patterns, then maps them onto this homelab wiki.
- [`0. How to read this document`](./llm-wiki-research-and-best-practices.md) — This is a **research + design note**, not an implementation. It distills ~20 primary and secondary sources on the LLM-Wiki pattern, agent-friendly documentation, context engineering, hybrid retrieval, agent memory architectures, homelab runbook hygiene, and secrets handling. The goal is to describe the **utopia end-state** for an LLM-Wiki serving an AI coding/operations agent that helps you run this Pangolin homelab stack, then to justify every design choice against the literature so future changes can be made on evidence rather than vibes.
- [`Wiki Index`](./index.md) — Flat catalog of the current wiki contents. This is the fastest content map for both humans and agents.
- [`Glossary`](./glossary.md) — Short definitions for recurring Pangolin homelab terms.
- [`Wiki Log`](./log.md) — Append-only record of structural wiki changes, maintenance passes, and review artifacts.

## Reviews
- [`Compose-File Review — 2026-04-17`](./compose-review-2026-04-17.md) — Full audit of every `docker-compose.yml` under `stacks/` against upstream documentation and reference compose files. Findings, severities, and remediation steps are collected there, with per-service detail in `docs/wiki/services/`.
- [`HomeNode Compose-File Review — 2026-04-17`](./homenode-review-2026-04-17.md) — Full audit of every `docker-compose.yml` under `/volume1/docker/` on HomeNode (`192.168.1.10`) against upstream references. Findings, severities, and remediation follow the same conventions as the CloudNode review.

## Concepts
- [`Port Matrix`](./concepts/port-matrix.md) — This page is the quickest view of which host or service owns which important port, whether it is public, tunneled, LAN-only, or considered a risk surface.

## Decisions
- [`0001 Core version pin policy`](./decisions/0001-core-version-pin-policy.md) — Accepted
- [`0002 CloudNode Traefik shares Gerbil network namespace`](./decisions/0002-cloudnode-traefik-shares-gerbil-namespace.md) — Accepted
- [`0003 HomeNode live-first sync workflow`](./decisions/0003-homenode-live-first-sync.md) — Accepted

## Hosts
- [`HomeNode Host`](./hosts/homenode.md) — Home server that runs the media, torrent, and *arr workloads.
- [`CloudNode Host`](./hosts/cloudnode.md) — Primary public edge and control-plane server.

## Networks
- [`pangolin Docker Network`](./networks/pangolin.md) — Shared external Docker network used by the CloudNode stacks outside the core namespace-sharing rule.
- [`traefik_traefik Docker Network`](./networks/traefik-traefik.md) — Single shared external Docker network for HomeNode services.

## Runbooks
- [`All sites return 403`](./runbooks/403-all-sites.md) — When every Cloudflare-fronted site returns 403 simultaneously. Covers CrowdSec container exit, Cloudflare false leads, and origin health checks.
- [`Check HomeNode reachability via Olm`](./runbooks/check-homenode-reachability-via-olm.md) — Use this when the CloudNode cannot reach HomeNode services, especially when Dockhand on the CloudNode cannot talk to HomeNode Docker at `192.168.1.10:2375`.
- [`Fix Pocket-ID shared data path`](./runbooks/fix-pocket-id-shared-data.md) — Use this to remediate `F-POCKETID-1 / C1`, where Pocket-ID mounts the shared repo `data/` directory instead of a dedicated path.
- [`Recreate CloudNode Traefik after recreating Gerbil`](./runbooks/recreate-traefik-after-gerbil.md) — Use this whenever `gerbil` has been recreated, replaced, or force-recreated on the CloudNode.

## CloudNode Services (Active)
- [`crowdsec-web-ui`](./services/crowdsec-web-ui.md) — Web admin UI for CrowdSec decisions / alerts / bouncers. Third-party image (not shipped by CrowdSec team).
- [`crowdsec`](./services/crowdsec.md) — IDS/IPS that reads Traefik's access log (and host `auth.log`/`syslog`), classifies suspicious behavior, and pushes decisions to bouncers (Traefik Badger plugin + host firewall).
- [`dashdot`](./services/dashdot.md) — Lightweight CloudNode system dashboard (CPU, RAM, storage, network). Runs behind Traefik at `dash.example.com`.
- [`dockhand`](./services/dockhand.md) — Modern replacement for Portainer — container + compose-stack management, both for the CloudNode (local docker.sock) and HomeNode (remote Hawser agent over TCP). Fronted at `dockhand.example.com`.
- [`gerbil`](./services/gerbil.md) — Fossorial Gerbil — WireGuard relay between the CloudNode and remote sites. Also owns the public HTTP/HTTPS ports (80/443); Traefik shares its network namespace via `network_mode: service:gerbil`.
- [`homarr`](./services/homarr.md) — Personal landing / dashboard page at `home.example.com`. Embeds widgets for media services, torrents, system status, etc.
- [`landing`](./services/landing.md) — Custom-built static landing page at the apex `example.com`. Replaced LinkStack with a single HTML+CSS page served by nginx.
- [`pangolin`](./services/pangolin.md) — Fossorial Pangolin — control plane, dashboard, API, and database for the whole stack. All other Fossorial components (Gerbil, Newt, Olm, Badger) read config from it.
- [`pocket-id`](./services/pocket-id.md) — OIDC / passkey-first identity provider. Used as the SSO gateway behind Traefik for admin UIs (`auth.example.com`).
- [`qbit-proxy`](./services/qbit-proxy.md) — Local reverse-proxy sidecar for Homarr's qBittorrent widget. Built from in-repo Dockerfile.
- [`termix`](./services/termix.md) — Web-based SSH terminal / tunneling / file editor at `termix.example.com`.
- [`traefik-log-dashboard (agent + UI)`](./services/traefik-log-dashboard.md) — Two services, one codebase: the **agent** tails Traefik's JSON access/error logs and exposes a parsed stream; the **dashboard** renders that stream in a React SPA with geolocation, status-code breakdowns, and service metrics.
- [`traefik`](./services/traefik.md) — Edge reverse-proxy and TLS terminator for everything exposed behind `*.example.com`. Shares Gerbil's network namespace.
- [`badger`](./services/badger.md) — Traefik CrowdSec bouncer plugin (`v1.4.0`). Not a container; runs inside Traefik.
- [`olm`](./services/olm.md) — WireGuard endpoint for LAN reachability. CloudNode systemd service (`1.4.4`), not a container.

## CloudNode Services (Archived)
- [`linkstack`](./services/linkstack.md) — Self-hosted Linktree replacement (archived — replaced by `landing` on 2026-04-21).

## CloudNode Services (Removed)
- [`adguard-home`](./services/adguard-home.md) — ~~Network-wide DNS filtering~~ **REMOVED 2026-04-21**. iPhone now uses `1.1.1.1` directly. Config preserved at `./config/adguard-home/`.

## HomeNode Services
- [`bazarr`](./services-homenode/bazarr.md) — Subtitle manager for Sonarr + Radarr. LinuxServer.io image.
- [`cleanuparr`](./services-homenode/cleanuparr.md) — Automated cleanup for qBit / Sonarr / Radarr — removes failed / stalled / redundant downloads so they stop taking up disk and swarm slots.
- [`dashdot (HomeNode)`](./services-homenode/dashdot.md) — Lightweight system dashboard for HomeNode. Separate instance from the CloudNode dashdot (which lives at [services/dashdot](./services/dashdot.md)).
- [`flaresolverr`](./services-homenode/flaresolverr.md) — Cloudflare anti-bot challenge solver. Runs a headless browser; Prowlarr and the *arr apps proxy indexer requests through it when hitting sites protected by Cloudflare's Under-Attack Mode / Turnstile.
- [`hawser`](./services-homenode/hawser.md) — Dockhand's remote agent. The CloudNode Dockhand connects to this agent over TCP to manage HomeNode containers in the same UI as CloudNode containers.
- [`newt`](./services-homenode/newt.md) — Fossorial Newt, the Pangolin site connector that establishes the outbound tunnel from HomeNode to the CloudNode so home services are reachable without opening inbound ports on the router.
- [`plex`](./services-homenode/plex.md) — Plex Media Server. Serves `plex.example.com` (Traefik-routed) and direct LAN clients. Hardware transcoding enabled via `/dev/dri`.
- [`profilarr`](./services-homenode/profilarr.md) — Quality-profile manager for Sonarr / Radarr — keeps custom formats, quality definitions, and naming schemes in sync across the *arr apps from a central spec.
- [`prowlarr`](./services-homenode/prowlarr.md) — Indexer manager for the *arr suite — federates torrent/usenet indexers into one API that Sonarr/Radarr query.
- [`qbittorrent`](./services-homenode/qbittorrent.md) — Torrent client. LinuxServer.io image. Serves web UI at `torrent.example.com` (Traefik-routed). **Runs with no VPN sidecar** — outbound swarm traffic exits on the ISP IP.
- [`qui`](./services-homenode/qui.md) — autobrr's "qui" — modern web UI for managing qBittorrent torrents (sort, bulk re-category, cross-seed workflows, etc.).
- [`radarr`](./services-homenode/radarr.md) — Movie manager. LinuxServer.io image. Twin of Sonarr, with `/movies` instead of `/tv`.
- [`recyclarr`](./services-homenode/recyclarr.md) — CLI + cron job that applies TRaSH-Guides recommended quality profiles and custom formats to Sonarr / Radarr. Runs on a schedule, not a long-lived server.
- [`seerr`](./services-homenode/seerr.md) — Media request front-end for end users — they ask for a movie / show, it hands the request to Sonarr / Radarr for fulfilment.
- [`sonarr`](./services-homenode/sonarr.md) — TV series manager. LinuxServer.io image.
- [`traefik (HomeNode)`](./services-homenode/traefik.md) — Home-LAN reverse proxy for all HomeNode services. Terminates TLS for `*.example.com` via Cloudflare DNS challenge. Distinct from the CloudNode Traefik.
