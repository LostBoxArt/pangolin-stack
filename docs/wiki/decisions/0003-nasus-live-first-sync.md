---
title: "0003 NASUS live-first sync workflow"
slug: decision-0003-nasus-live-first-sync
type: decision
status: accepted
tags: ["homelab", "decision", "nasus", "workflow"]
aliases: ["nasus sync workflow"]
entities:
  primary: decision-0003-nasus-live-first-sync
  mentions: []
related: ["../hosts/nasus.md", "../nasus-review-2026-04-17.md", "../services-nasus/traefik.md"]
sources: ["docs/wiki/README.md", "docs/wiki/nasus-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# 0003 NASUS live-first sync workflow

## Status
Accepted

## Context
NASUS compose files live on the NASUS host under `/volume1/docker/...`, while `host-configs/nasus/` is only a source-controlled copy and is currently incomplete. The audit explicitly states that changes flow `NASUS -> repo`, not the other way around, until a stronger sync system exists.

## Decision
Treat the live NASUS host as the operational source of truth for NASUS compose edits. After changing the live file and applying it on NASUS, sync the sanitized repo copy and then update the matching wiki page.

## Consequences
### Positive
- Matches current operational reality.
- Avoids pretending the repo copy is deployable when coverage is incomplete.
- Keeps wiki and tracked compose copies tied to real live changes.

### Negative
- NASUS drift can still occur outside git until sync happens.
- Editing NASUS services is inherently more manual than the VPS side.

### Neutral
- This is a temporary but explicit operating model, not an ideal GitOps end-state.

## Alternatives considered
- Treat `host-configs/nasus/` as the deployment source immediately.
- Delay all NASUS wiki maintenance until repo-sync coverage is complete.

## References
- [[../hosts/nasus.md]]
- [[../nasus-review-2026-04-17.md]]
- [[../README.md]]
