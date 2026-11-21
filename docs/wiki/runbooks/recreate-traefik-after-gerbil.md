---
title: "Recreate CloudNode Traefik after recreating Gerbil"
slug: runbook-recreate-traefik-after-gerbil
type: runbook
status: active
tags: ["homelab", "runbook", "cloudnode", "traefik", "gerbil"]
aliases: ["traefik gerbil recreate"]
entities:
  primary: runbook-recreate-traefik-after-gerbil
  mentions: []
related: ["../services/gerbil.md", "../services/traefik.md", "../hosts/cloudnode.md"]
sources: ["AGENTS.md", "docs/wiki/services/traefik.md", "scripts/ensure-traefik-netns.sh", "tests/test_core_netns.py"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-04-17
---
# Recreate CloudNode Traefik after recreating Gerbil

## When to use this
Use this after replacing Gerbil outside the normal startup scripts, or when public routing fails after a core deployment. `startup.sh`, `stackctl.sh start core`, and `stackctl.sh restart core` now run this check automatically.

## Prerequisites
- Run from the deployed repository root (`/home/jesus/pangolin-stack` on the current CloudNode).
- Docker available on the CloudNode
- `.env` present in the repo root

## Procedure
1. Change to the repo root:
   ```bash
   cd /home/jesus/pangolin-stack
   ```
2. Check the running containers' actual network namespaces:
   ```bash
   ./scripts/ensure-traefik-netns.sh
   ```

The check leaves healthy containers unchanged. When the namespaces differ, it recreates only Traefik, uses the cached image, and verifies the result. Missing or stopped core containers produce an error instead of being silently started.

## Verification
- Check that public `80/443` routing works again.
- Confirm Traefik is running and attached to Gerbil's current namespace.
- A second check should report a shared namespace without changing either container ID.

## Rollback
- If the recreate fails, inspect the core stack logs and container status.
- Re-run the command after fixing the underlying compose or image problem.

## Escalation
- Review [[../services/traefik.md]] and [[../services/gerbil.md]] for current findings and dependencies.

## Last tested
2026-10-27: `python3 tests/test_core_netns.py` passed with Docker 29.6.1 / Compose 5.3.0. The isolated fixture covers healthy no-op, Gerbil replacement, Gerbil restart, repeat no-op, and rejection of a stopped Traefik. Production verification was a no-op; Gerbil was not replaced for testing.
