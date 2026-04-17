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
sources: ["AGENTS.md", "docs/wiki/services/traefik.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# Recreate CloudNode Traefik after recreating Gerbil

## When to use this
Use this whenever `gerbil` has been recreated, replaced, or force-recreated on the CloudNode.

## Prerequisites
- Repo path: `/opt/homelab`
- Docker available on the CloudNode
- `.env` present in the repo root

## Procedure
1. Change to the repo root:
   ```bash
   cd /opt/homelab
   ```
2. Force-recreate Traefik in the core stack:
   ```bash
   docker compose -f stacks/core/docker-compose.yml --env-file .env up -d --force-recreate traefik
   ```

## Verification
- Check that public `80/443` routing works again.
- Confirm Traefik is running and attached to Gerbil's current namespace.

## Rollback
- If the recreate fails, inspect the core stack logs and container status.
- Re-run the command after fixing the underlying compose or image problem.

## Escalation
- Review [[../services/traefik.md]] and [[../services/gerbil.md]] for current findings and dependencies.

## Last tested
Not recorded in the wiki yet.
