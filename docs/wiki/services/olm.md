---
title: "olm"
slug: cloudnode-olm
type: service
status: active
tags: ["homelab", "cloudnode", "service", "olm"]
aliases: ["olm"]
entities:
  primary: cloudnode-olm
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md", "../runbooks/check-homenode-reachability-via-olm.md"]
sources: ["AGENTS.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-21
last_lint: 2026-04-21
---

# olm

Fossorial Olm — WireGuard endpoint on the CloudNode that provides reachability
to the HomeNode LAN (`192.168.1.0/24`). This is a **systemd service**, not a
Docker container.

- **Type**: systemd service (not a container)
- **Binary**: `/usr/local/sbin/olm`
- **Version**: `1.4.4`
- **Runtime flag**: `--override-dns=false`

## Upstream Sources

- Releases: <https://github.com/fosrl/olm/releases>

## Operational Commands

Use the safe-wrapper helpers instead of raw `sudo systemctl`:

```bash
/usr/local/sbin/hermes-safe-service status olm
/usr/local/sbin/hermes-safe-logs olm --since 30m
/usr/local/sbin/hermes-safe-service restart olm
/usr/local/sbin/hermes-safe-service status olm-watchdog.timer
```

## Tunnel Verification

Expected route on the CloudNode:

```bash
ip route | grep '192.168.1.0/24 dev olm'
```

If the route is missing, inspect Olm service state and logs, then restart if
needed. See `docs/wiki/runbooks/check-homenode-reachability-via-olm.md`.

## Watchdogs

- **CloudNode**: `/usr/local/sbin/olm-watchdog.sh` + `olm-watchdog.timer`
  (systemd, every minute)
- **HomeNode**: `/usr/local/bin/newt-watchdog.sh` (root crontab every minute)

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Version | latest | pinned `1.4.4` | aligned with Pangolin 1.17.x — ✓ |
| DNS override | default | `--override-dns=false` | prevents resolver drift inside Olm |

## Findings

None currently documented.

## Operational Notes

- Pin `pangolin.example.com` to `203.0.113.1` in `/etc/hosts` on the CloudNode.
  This avoids resolver drift inside Olm and keeps the UDP hole-punch path stable.
- If Dockhand on the CloudNode cannot reach HomeNode at `192.168.1.10:2375`,
  first check for `192.168.1.0/24 dev olm`. If it is missing, inspect Olm logs
  and restart the service.
