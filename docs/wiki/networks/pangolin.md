---
title: "pangolin Docker Network"
slug: network-pangolin
type: network
status: active
tags: ["homelab", "network", "cloudnode", "pangolin"]
aliases: ["pangolin network"]
entities:
  primary: network-pangolin
  mentions: []
related: ["../hosts/cloudnode.md", "../services/pangolin.md", "../services/traefik.md", "../services/dockhand.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# pangolin Docker Network

Shared external Docker network used by the CloudNode stacks outside the core namespace-sharing rule.

## Purpose
Provides service-to-service connectivity across the CloudNode stack after the core stack creates the network.

## Members and usage
- Core stack creates it.
- Non-core CloudNode stacks attach to it as an external network.
- Used by services such as Dockhand, Homarr, Pocket-ID, and dashboard components.

## Operational notes
- Startup order matters because the core stack creates this network.
- CloudNode Traefik does not appear as a regular member because it runs in `network_mode: service:gerbil`.
