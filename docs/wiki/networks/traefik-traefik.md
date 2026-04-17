---
title: "traefik_traefik Docker Network"
slug: network-traefik-traefik
type: network
status: active
tags: ["homelab", "network", "homenode", "traefik"]
aliases: ["traefik_traefik"]
entities:
  primary: network-traefik-traefik
  mentions: []
related: ["../hosts/homenode.md", "../services-homenode/traefik.md", "../services-homenode/hawser.md", "../services-homenode/qbittorrent.md"]
sources: ["docs/wiki/system-overview.md", "docs/wiki/homenode-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# traefik_traefik Docker Network

Single shared external Docker network for HomeNode services.

## Purpose
Gives the HomeNode Traefik instance reachability to the service backends it proxies.

## Design consequence
All HomeNode services share one flat network with no segmentation by function.

## Risk and findings
- The HomeNode audit flags this design under `NM3` as a security and blast-radius concern.
- Hawser, torrent workloads, media services, and Traefik all sit on the same shared network.

## Operational notes
- This is a major architectural difference from the CloudNode side.
- Any future segmentation work should likely create purpose-specific networks and update Traefik routing accordingly.
