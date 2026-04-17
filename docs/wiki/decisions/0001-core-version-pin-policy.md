---
title: "0001 Core version pin policy"
slug: decision-0001-core-version-pin-policy
type: decision
status: accepted
tags: ["homelab", "decision", "versions", "pinning"]
aliases: ["version pin policy"]
entities:
  primary: decision-0001-core-version-pin-policy
  mentions: []
related: ["../system-overview.md", "../services/traefik.md", "../services-homenode/traefik.md"]
sources: ["AGENTS.md", "docs/wiki/compose-review-2026-04-17.md", "docs/wiki/homenode-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# 0001 Core version pin policy

## Status
Accepted

## Context
The homelab depends on a small set of components where upstream image drift can break routing, tunneling, or control-plane behavior. `AGENTS.md` already states that Pangolin, Gerbil, Newt, Olm, Badger, and CrowdSec Web UI should remain pinned. Both CloudNode and HomeNode audits also flag `:latest` usage as a recurring risk.

## Decision
Keep the core control-plane and tunnel-related components version-pinned rather than following moving tags.

## Consequences
### Positive
- Reduces surprise breakage during pulls or restarts.
- Keeps tunnel and proxy compatibility easier to reason about.
- Makes upgrades explicit and auditable.

### Negative
- Requires manual review and deliberate upgrade work.
- Pin drift has to be maintained in the wiki and compose files.

### Neutral
- Non-core services may still be unpinned today, but those are treated as drift to review rather than an intentional best practice.

## Alternatives considered
- Follow `:latest` everywhere and accept operational drift.
- Pin only the CloudNode side and let HomeNode float independently.

## References
- [[../system-overview.md]]
- [[../services/traefik.md]]
- [[../services-homenode/traefik.md]]
