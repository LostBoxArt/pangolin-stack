---
title: "HomeNode Host"
slug: host-homenode
type: host
status: active
tags: ["homelab", "homenode", "host"]
aliases: ["HomeNode", "192.168.1.10"]
entities:
  primary: host-homenode
  mentions: []
related: ["../system-overview.md", "../homenode-review-2026-04-17.md", "../networks/traefik-traefik.md", "../services-homenode/traefik.md", "../services-homenode/hawser.md", "../services-homenode/newt.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md", "docs/wiki/homenode-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# HomeNode Host

Home server that runs the media, torrent, and *arr workloads.

## Identity
- Hostname: HomeNode
- LAN IP: `192.168.1.10`
- Role: home-lab applications, media services, torrent stack, and HomeNode-side tunnel components

## Compose layout
- Live compose files: `/volume1/docker/config/<service>/docker-compose.yml`
- Traefik compose: `/volume1/docker/traefik/docker-compose.yml`
- Hawser compose: `/volume1/docker/hawser/docker-compose.yml`
- Source-controlled copies: `host-configs/homenode/` (currently incomplete coverage per `NM1`)

## Services hosted
- [[../services-homenode/traefik.md]]
- [[../services-homenode/hawser.md]]
- [[../services-homenode/newt.md]]
- [[../services-homenode/sonarr.md]]
- [[../services-homenode/radarr.md]]
- [[../services-homenode/bazarr.md]]
- [[../services-homenode/prowlarr.md]]
- [[../services-homenode/profilarr.md]]
- [[../services-homenode/recyclarr.md]]
- [[../services-homenode/qbittorrent.md]]
- [[../services-homenode/qui.md]]
- [[../services-homenode/flaresolverr.md]]
- [[../services-homenode/cleanuparr.md]]
- [[../services-homenode/plex.md]]
- [[../services-homenode/seerr.md]]
- [[../services-homenode/dashdot.md]]

## Networks
- Shared external Docker network: [[../networks/traefik-traefik.md]]
- Home LAN reachable from the CloudNode through Olm/Newt

## Access
- SSH: `ssh admin@192.168.1.10`
- Docker API via Hawser on TCP 2375 requires token auth
- Plain docker socket access generally requires `sudo`

## Known operational notes
- HomeNode changes flow live host first, then repo sync, then wiki update.
- `NC1` and `NC2` remain open compromise-risk surfaces on HomeNode as of the current audit.
