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
last_lint: 2026-04-17
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
- [`Compose-File Review — 2026-04-17`](./compose-review-2026-04-17.md) — Full audit of every `docker-compose.yml` under `stacks/` against upstream documentation and reference compose files. Findings, severities, and remediation steps are collected here. Per-service detail lives in the
- [`NASUS Compose-File Review — 2026-04-17`](./nasus-review-2026-04-17.md) — Full audit of every `docker-compose.yml` under `/volume1/docker/` on NASUS (`192.168.0.10`) against upstream references. Findings, severities, and remediation follow the same conventions as the

## Concepts
- [`Port Matrix`](./concepts/port-matrix.md) — This page is the quickest view of which host or service owns which important port, whether it is public, tunneled, LAN-only, or considered a risk surface.

## Decisions
- [`0001 Core version pin policy`](./decisions/0001-core-version-pin-policy.md) — Accepted
- [`0002 VPS Traefik shares Gerbil network namespace`](./decisions/0002-vps-traefik-shares-gerbil-namespace.md) — Accepted
- [`0003 NASUS live-first sync workflow`](./decisions/0003-nasus-live-first-sync.md) — Accepted

## Hosts
- [`NASUS Host`](./hosts/nasus.md) — Home server that runs the media, torrent, and *arr workloads.
- [`VPS Host`](./hosts/vps.md) — Primary public edge and control-plane server.

## Networks
- [`pangolin Docker Network`](./networks/pangolin.md) — Shared external Docker network used by the VPS stacks outside the core namespace-sharing rule.
- [`traefik_traefik Docker Network`](./networks/traefik-traefik.md) — Single shared external Docker network for NASUS services.

## Runbooks
- [`Check NASUS reachability via Olm`](./runbooks/check-nasus-reachability-via-olm.md) — Use this when the VPS cannot reach NASUS services, especially when Dockhand on the VPS cannot talk to NASUS Docker at `192.168.0.10:2375`.
- [`Fix Pocket-ID shared data path`](./runbooks/fix-pocket-id-shared-data.md) — Use this to remediate `F-POCKETID-1 / C1`, where Pocket-ID mounts the shared repo `data/` directory instead of a dedicated path.
- [`Recreate VPS Traefik after recreating Gerbil`](./runbooks/recreate-traefik-after-gerbil.md) — Use this whenever `gerbil` has been recreated, replaced, or force-recreated on the VPS.

## VPS Services
- [`adguard-home`](./services/adguard-home.md) — Network-wide DNS filtering. Exposed publicly as:
- [`crowdsec-web-ui`](./services/crowdsec-web-ui.md) — Web admin UI for CrowdSec decisions / alerts / bouncers. Third-party image (not shipped by CrowdSec team).
- [`crowdsec`](./services/crowdsec.md) — IDS/IPS that reads Traefik's access log (and host `auth.log`/`syslog`), classifies suspicious behavior, and pushes decisions to bouncers (Traefik Badger plugin + host firewall).
- [`dashdot`](./services/dashdot.md) — Lightweight VPS system dashboard (CPU, RAM, storage, network). Runs behind Traefik at `dash.dennisb.xyz`.
- [`dockhand`](./services/dockhand.md) — Modern replacement for Portainer — container + compose-stack management, both for the VPS (local docker.sock) and NASUS (remote Hawser agent over TCP). Fronted at `dockhand.dennisb.xyz`.
- [`gerbil`](./services/gerbil.md) — Fossorial Gerbil — WireGuard relay between the VPS and remote sites. Also owns the public HTTP/HTTPS ports (80/443); Traefik shares its network namespace via `network_mode: service:gerbil`.
- [`homarr`](./services/homarr.md) — Personal landing / dashboard page at `home.dennisb.xyz`. Embeds widgets for media services, torrents, system status, etc.
- [`linkstack`](./services/linkstack.md) — Self-hosted Linktree replacement — single-page "all my links" landing page at the apex `dennisb.xyz`.
- [`pangolin`](./services/pangolin.md) — Fossorial Pangolin — control plane, dashboard, API, and database for the whole stack. All other Fossorial components (Gerbil, Newt, Olm, Badger) read config from it.
- [`pocket-id`](./services/pocket-id.md) — OIDC / passkey-first identity provider. Used as the SSO gateway behind Traefik for admin UIs (`auth.dennisb.xyz`).
- [`qbit-proxy`](./services/qbit-proxy.md) — Local reverse-proxy sidecar for Homarr's qBittorrent widget. Built from in-repo Dockerfile.
- [`termix`](./services/termix.md) — Web-based SSH terminal / tunneling / file editor at `termix.dennisb.xyz`.
- [`traefik-log-dashboard (agent + UI)`](./services/traefik-log-dashboard.md) — Two services, one codebase: the **agent** tails Traefik's JSON access/error logs and exposes a parsed stream; the **dashboard** renders that stream in a React SPA with geolocation, status-code breakdowns, and service metrics.
- [`traefik`](./services/traefik.md) — Edge reverse-proxy and TLS terminator for everything exposed behind `*.dennisb.xyz`. Shares Gerbil's network namespace.

## NASUS Services
- [`bazarr`](./services-nasus/bazarr.md) — Subtitle manager for Sonarr + Radarr. LinuxServer.io image.
- [`cleanuparr`](./services-nasus/cleanuparr.md) — Automated cleanup for qBit / Sonarr / Radarr — removes failed / stalled / redundant downloads so they stop taking up disk and swarm slots.
- [`dashdot (NASUS)`](./services-nasus/dashdot.md) — Lightweight system dashboard for NASUS. Separate instance from the VPS dashdot (which lives at [services/dashdot](../services/dashdot.md)).
- [`flaresolverr`](./services-nasus/flaresolverr.md) — Cloudflare anti-bot challenge solver. Runs a headless browser; Prowlarr and the *arr apps proxy indexer requests through it when hitting sites protected by Cloudflare's Under-Attack Mode / Turnstile.
- [`hawser`](./services-nasus/hawser.md) — Dockhand's remote agent. The VPS Dockhand connects to this agent over TCP to manage NASUS containers in the same UI as VPS containers.
- [`newt`](./services-nasus/newt.md) — Fossorial Newt — Pangolin site connector. Establishes the outbound tunnel from NASUS to the VPS Pangolin so that LAN services can be reached from the public `*.dennisb.xyz` without opening inbound ports on the home
- [`plex`](./services-nasus/plex.md) — Plex Media Server. Serves `plex.dennisb.xyz` (Traefik-routed) and direct LAN clients. Hardware transcoding enabled via `/dev/dri`.
- [`profilarr`](./services-nasus/profilarr.md) — Quality-profile manager for Sonarr / Radarr — keeps custom formats, quality definitions, and naming schemes in sync across the *arr apps from a central spec.
- [`prowlarr`](./services-nasus/prowlarr.md) — Indexer manager for the *arr suite — federates torrent/usenet indexers into one API that Sonarr/Radarr query.
- [`qbittorrent`](./services-nasus/qbittorrent.md) — Torrent client. LinuxServer.io image. Serves web UI at `torrent.dennisb.xyz` (Traefik-routed). **Runs with no VPN sidecar** — outbound swarm traffic exits on the ISP IP.
- [`qui`](./services-nasus/qui.md) — autobrr's "qui" — modern web UI for managing qBittorrent torrents (sort, bulk re-category, cross-seed workflows, etc.).
- [`radarr`](./services-nasus/radarr.md) — Movie manager. LinuxServer.io image. Twin of Sonarr, with `/movies` instead of `/tv`.
- [`recyclarr`](./services-nasus/recyclarr.md) — CLI + cron job that applies TRaSH-Guides recommended quality profiles and custom formats to Sonarr / Radarr. Runs on a schedule, not a long-lived server.
- [`seerr`](./services-nasus/seerr.md) — Media request front-end for end users — they ask for a movie / show, it hands the request to Sonarr / Radarr for fulfilment.
- [`sonarr`](./services-nasus/sonarr.md) — TV series manager. LinuxServer.io image.
- [`traefik (NASUS)`](./services-nasus/traefik.md) — Home-LAN reverse proxy for all NASUS services. Terminates TLS for `*.dennisb.xyz` via Cloudflare DNS challenge. Distinct from the VPS Traefik.
