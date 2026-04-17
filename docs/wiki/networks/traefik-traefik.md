---
title: "traefik_traefik Docker Network"
slug: network-traefik-traefik
type: network
status: active
tags: ["homelab", "network", "nasus", "traefik"]
aliases: ["traefik_traefik"]
entities:
  primary: network-traefik-traefik
  mentions: []
related: ["../hosts/nasus.md", "../services-nasus/traefik.md", "../services-nasus/hawser.md", "../services-nasus/qbittorrent.md"]
sources: ["docs/wiki/system-overview.md", "docs/wiki/nasus-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# traefik_traefik Docker Network

Single shared external Docker network for NASUS services.

## Purpose
Gives the NASUS Traefik instance reachability to the service backends it proxies.

## Design consequence
All NASUS services share one flat network with no segmentation by function.

## Risk and findings
- The NASUS audit flags this design under `NM3` as a security and blast-radius concern.
- Hawser, torrent workloads, media services, and Traefik all sit on the same shared network.

## Operational notes
- This is a major architectural difference from the VPS side.
- Any future segmentation work should likely create purpose-specific networks and update Traefik routing accordingly.
