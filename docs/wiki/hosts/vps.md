---
title: "VPS Host"
slug: host-vps
type: host
status: active
tags: ["homelab", "vps", "host"]
aliases: ["vps", "51.195.100.11"]
entities:
  primary: host-vps
  mentions: []
related: ["../system-overview.md", "../services/pangolin.md", "../services/gerbil.md", "../services/traefik.md", "../networks/pangolin.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md", "docs/wiki/compose-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# VPS Host

Primary public edge and control-plane server.

## Identity
- Host role: public edge and homelab control plane
- Public IP: `51.195.100.11`
- Key responsibilities: Pangolin control plane, Gerbil relay, VPS Traefik, CrowdSec, Dockhand, dashboards

## Services hosted
- [[../services/pangolin.md]]
- [[../services/gerbil.md]]
- [[../services/traefik.md]]
- [[../services/crowdsec.md]]
- [[../services/crowdsec-web-ui.md]]
- [[../services/pocket-id.md]]
- [[../services/adguard-home.md]]
- [[../services/traefik-log-dashboard.md]]
- [[../services/dashdot.md]]
- [[../services/dockhand.md]]
- [[../services/homarr.md]]
- [[../services/qbit-proxy.md]]
- [[../services/linkstack.md]]
- [[../services/termix.md]]

## Networks
- Docker external network: [[../networks/pangolin.md]]
- Tunnel route to NASUS LAN: `192.168.0.0/24 dev olm`

## Access
- Tunnel component: `olm` systemd service
- Safe service helper: `/usr/local/sbin/hermes-safe-service`
- Safe logs helper: `/usr/local/sbin/hermes-safe-logs`

## Backup and restore context
- Repo contains compose, config, and operational docs.
- `backup.sh` is the documented backup/restore helper for the Pangolin stack.

## Known operational notes
- If Gerbil is recreated, Traefik must be recreated afterward because Traefik shares Gerbil's network namespace.
- VPS is the place where Dockhand reaches NASUS Hawser and where `olm` route health matters.
