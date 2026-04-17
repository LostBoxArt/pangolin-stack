---
title: "Check HomeNode reachability via Olm"
slug: runbook-check-homenode-reachability-via-olm
type: runbook
status: active
tags: ["homelab", "runbook", "olm", "homenode", "cloudnode"]
aliases: ["check HomeNode route", "olm reachability"]
entities:
  primary: runbook-check-homenode-reachability-via-olm
  mentions: []
related: ["../hosts/cloudnode.md", "../hosts/homenode.md", "../services-homenode/newt.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# Check HomeNode reachability via Olm

## When to use this
Use this when the CloudNode cannot reach HomeNode services, especially when Dockhand on the CloudNode cannot talk to HomeNode Docker at `192.168.1.10:2375`.

## Prerequisites
- CloudNode shell access
- `olm` installed as a systemd service on the CloudNode

## Procedure
1. Check that the HomeNode LAN route exists:
   ```bash
   ip route | grep '192.168.1.0/24 dev olm'
   ```
2. If the route is missing, inspect the `olm` service state:
   ```bash
   /usr/local/sbin/hermes-safe-service status olm
   ```
3. Review recent logs:
   ```bash
   /usr/local/sbin/hermes-safe-logs olm --since 30m
   ```
4. If needed, restart `olm`:
   ```bash
   /usr/local/sbin/hermes-safe-service restart olm
   ```
5. Re-check the route and then retry the failing HomeNode access path.

## Verification
- Expected route: `192.168.1.0/24 dev olm`
- CloudNode can reach `192.168.1.10`
- Dockhand or other CloudNode-side HomeNode checks recover

## Rollback
- If restarting `olm` makes things worse, inspect logs and compare against the last known-good tunnel state.

## Escalation
- If the CloudNode route looks healthy, inspect the HomeNode-side Newt watchdog and service state next.

## Last tested
Not recorded in the wiki yet.
