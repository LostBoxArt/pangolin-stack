---
title: "0002 VPS Traefik shares Gerbil network namespace"
slug: decision-0002-vps-traefik-gerbil-namespace
type: decision
status: accepted
tags: ["homelab", "decision", "traefik", "gerbil", "networking"]
aliases: ["gerbil traefik shared namespace"]
entities:
  primary: decision-0002-vps-traefik-gerbil-namespace
  mentions: []
related: ["../services/gerbil.md", "../services/traefik.md", "../runbooks/recreate-traefik-after-gerbil.md"]
sources: ["AGENTS.md", "docs/wiki/services/traefik.md", "docs/wiki/services/gerbil.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# 0002 VPS Traefik shares Gerbil network namespace

## Status
Accepted

## Context
On the VPS, Traefik runs with `network_mode: service:gerbil`. This means Gerbil owns the public network namespace and Traefik rides inside it. The arrangement is operationally important enough that `AGENTS.md` calls out a dedicated recovery rule: if Gerbil is recreated, Traefik must also be recreated.

## Decision
Keep the VPS-side Traefik attached to Gerbil's network namespace and treat Gerbil recreation as a mandatory Traefik recreation event.

## Consequences
### Positive
- Preserves the current public ingress architecture.
- Keeps the documented Pangolin/Gerbil/Traefik flow aligned with the running stack.

### Negative
- Silent breakage is possible if Gerbil is recreated without Traefik following it.
- Network troubleshooting is less intuitive because Traefik does not appear like a regular container on the external network.

### Neutral
- This is a VPS-only behavior. NASUS Traefik is standalone and does not share this constraint.

## Alternatives considered
- Run Traefik independently with its own namespace.
- Move public ingress responsibilities away from Gerbil entirely.

## References
- [[../services/gerbil.md]]
- [[../services/traefik.md]]
- [[../runbooks/recreate-traefik-after-gerbil.md]]
