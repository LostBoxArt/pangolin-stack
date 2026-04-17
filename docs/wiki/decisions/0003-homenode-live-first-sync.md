---
title: "0003 HomeNode live-first sync workflow"
slug: decision-0003-homenode-live-first-sync
type: decision
status: accepted
tags: ["homelab", "decision", "homenode", "workflow"]
aliases: ["homenode sync workflow"]
entities:
  primary: decision-0003-homenode-live-first-sync
  mentions: []
related: ["../hosts/homenode.md", "../homenode-review-2026-04-17.md", "../services-homenode/traefik.md"]
sources: ["docs/wiki/README.md", "docs/wiki/homenode-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# 0003 HomeNode live-first sync workflow

## Status
Accepted

## Context
HomeNode compose files live on the HomeNode host under `/volume1/docker/...`, while `host-configs/homenode/` is only a source-controlled copy and is currently incomplete. The audit explicitly states that changes flow `HomeNode -> repo`, not the other way around, until a stronger sync system exists.

## Decision
Treat the live HomeNode host as the operational source of truth for HomeNode compose edits. After changing the live file and applying it on HomeNode, sync the sanitized repo copy and then update the matching wiki page.

## Consequences
### Positive
- Matches current operational reality.
- Avoids pretending the repo copy is deployable when coverage is incomplete.
- Keeps wiki and tracked compose copies tied to real live changes.

### Negative
- HomeNode drift can still occur outside git until sync happens.
- Editing HomeNode services is inherently more manual than the CloudNode side.

### Neutral
- This is a temporary but explicit operating model, not an ideal GitOps end-state.

## Alternatives considered
- Treat `host-configs/homenode/` as the deployment source immediately.
- Delay all HomeNode wiki maintenance until repo-sync coverage is complete.

## References
- [[../hosts/homenode.md]]
- [[../homenode-review-2026-04-17.md]]
- [[../README.md]]
