---
title: "NASUS Host"
slug: host-nasus
type: host
status: active
tags: ["homelab", "nasus", "host"]
aliases: ["NASUS", "192.168.0.10"]
entities:
  primary: host-nasus
  mentions: []
related: ["../system-overview.md", "../nasus-review-2026-04-17.md", "../networks/traefik-traefik.md", "../services-nasus/traefik.md", "../services-nasus/hawser.md", "../services-nasus/newt.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md", "docs/wiki/nasus-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# NASUS Host

Home server that runs the media, torrent, and *arr workloads.

## Identity
- Hostname: NASUS
- LAN IP: `192.168.0.10`
- Role: home-lab applications, media services, torrent stack, and NASUS-side tunnel components

## Compose layout
- Live compose files: `/volume1/docker/config/<service>/docker-compose.yml`
- Traefik compose: `/volume1/docker/traefik/docker-compose.yml`
- Hawser compose: `/volume1/docker/hawser/docker-compose.yml`
- Source-controlled copies: `host-configs/nasus/` (currently incomplete coverage per `NM1`)

## Services hosted
- [[../services-nasus/traefik.md]]
- [[../services-nasus/hawser.md]]
- [[../services-nasus/newt.md]]
- [[../services-nasus/sonarr.md]]
- [[../services-nasus/radarr.md]]
- [[../services-nasus/bazarr.md]]
- [[../services-nasus/prowlarr.md]]
- [[../services-nasus/profilarr.md]]
- [[../services-nasus/recyclarr.md]]
- [[../services-nasus/qbittorrent.md]]
- [[../services-nasus/qui.md]]
- [[../services-nasus/flaresolverr.md]]
- [[../services-nasus/cleanuparr.md]]
- [[../services-nasus/plex.md]]
- [[../services-nasus/seerr.md]]
- [[../services-nasus/dashdot.md]]

## Networks
- Shared external Docker network: [[../networks/traefik-traefik.md]]
- Home LAN reachable from the VPS through Olm/Newt

## Access
- SSH: `ssh jesus@192.168.0.10`
- Docker API via Hawser on TCP 2375 requires token auth
- Plain docker socket access generally requires `sudo`

## Known operational notes
- NASUS changes flow live host first, then repo sync, then wiki update.
- `NC1` and `NC2` remain open compromise-risk surfaces on NASUS as of the current audit.
