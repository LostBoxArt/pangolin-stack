---
title: "Check NASUS reachability via Olm"
slug: runbook-check-nasus-reachability-via-olm
type: runbook
status: active
tags: ["homelab", "runbook", "olm", "nasus", "vps"]
aliases: ["check NASUS route", "olm reachability"]
entities:
  primary: runbook-check-nasus-reachability-via-olm
  mentions: []
related: ["../hosts/vps.md", "../hosts/nasus.md", "../services-nasus/newt.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# Check NASUS reachability via Olm

## When to use this
Use this when the VPS cannot reach NASUS services, especially when Dockhand on the VPS cannot talk to NASUS Docker at `192.168.0.10:2375`.

## Prerequisites
- VPS shell access
- `olm` installed as a systemd service on the VPS

## Procedure
1. Check that the NASUS LAN route exists:
   ```bash
   ip route | grep '192.168.0.0/24 dev olm'
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
5. Re-check the route and then retry the failing NASUS access path.

## Verification
- Expected route: `192.168.0.0/24 dev olm`
- VPS can reach `192.168.0.10`
- Dockhand or other VPS-side NASUS checks recover

## Rollback
- If restarting `olm` makes things worse, inspect logs and compare against the last known-good tunnel state.

## Escalation
- If the VPS route looks healthy, inspect the NASUS-side Newt watchdog and service state next.

## Last tested
Not recorded in the wiki yet.
