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
last_ingested: 2026-10-27
last_lint: 2026-10-27
---

# olm

Fossorial Olm — WireGuard endpoint on the CloudNode that provides reachability
to the HomeNode LAN (`192.168.1.0/24`). This is a **systemd service**, not a
Docker container.

- **Type**: systemd service (not a container)
- **Binary**: `/usr/local/bin/olm`
- **Version**: `1.9.1` (live verification, 2026-10-27)
- **Runtime flag**: `--override-dns=false`
- **Credential file**: `/root/.config/olm-client/config.json`, root-owned `0600`
  inside a `0700` directory. The unit sets `CONFIG_FILE` and `UMask=0077`;
  credentials are absent from `ExecStart` and process arguments.
- **Unit source**: `host-configs/cloudnode/systemd/olm.service`

## Upstream Sources

- Releases: <https://github.com/fosrl/olm/releases>
- Config loading: <https://github.com/fosrl/olm/blob/1.9.1/config.go>
- Credential rotation: <https://docs.pangolin.net/manage/clients/machine-clients#rotating-and-regenerating-credentials>
- Deployed rotation handler: <https://github.com/fosrl/pangolin/blob/1.25.3/server/routers/re-key/reGenerateClientSecret.ts>

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
| Version | latest | installed `1.9.1` | preserve the tested live binary during this maintenance |
| DNS override | default | `--override-dns=false` | prevents resolver drift inside Olm |
| Credential loading | CLI/env/config supported | root-only config file | avoids a credential in argv or the unit |

## Findings

Olm 1.9.1 merges boolean config values such that a file value of `false` does
not reliably override the default. Keep the explicit `--override-dns=false`
argument; moving credentials to JSON does not justify removing this flag.

Do not run `olm --help` or `--show-config` against a populated config in a
shared transcript: flag defaults/config output can disclose its secret.

On 2026-10-27 the service was migrated to the private config and its credential
rotated through Pangolin's authenticated API. Native Argon2 verification proved
the previous secret invalid and the new secret valid. Client identity was
preserved, the service restarted successfully, the NAS route and Hawser health
recovered, and the Olm watchdog timer was resumed. Recent Olm journal output
and process arguments contained no new secret.

## Operational Notes

- Pin `pangolin.example.com` to `203.0.113.1` in `/etc/hosts` on the CloudNode.
  This avoids resolver drift inside Olm and keeps the UDP hole-punch path stable.
- If Dockhand on the CloudNode cannot reach HomeNode at `192.168.1.10:2375`,
  first check for `192.168.1.0/24 dev olm`. If it is missing, inspect Olm logs
  and restart the service.
- Addresses above are repository examples. The verified deployment uses
  `192.168.0.0/24` and NAS `192.168.0.10`; use the actual deployment values.
- A credential rotation invalidates the secret in older backups. Restoring an
  old config alone will not restore access; use the current encrypted backup
  or regenerate through independently reachable Pangolin administration.
- Keep the root config and any retained user CLI config synchronized after
  rotation, with mode `0600`. Never commit either populated config.

## Verify the actual data path

The 2026-10-27 deployment has both Olm and a Tailscale subnet route. Linux policy
routing currently prefers Tailscale for an ordinary NAS request. A main-table
Olm route plus a successful ordinary request does not prove Olm is working.
Use the actual NAS address for these checks (example address below):

```bash
ip route get 192.168.1.10
ip route get 192.168.1.10 oif olm
curl --noproxy '*' --interface olm --fail --silent --show-error --max-time 10 \
  -o /dev/null -w 'HTTP %{http_code} source=%{local_ip}\n' \
  http://192.168.1.10:2375/_hawser/health
```

The forced-interface probe returned HTTP `200` from the Olm source address after
credential rotation. This endpoint checks Hawser availability without exposing
Docker credentials; authenticated Docker access is a separate check. Routing
priorities were preserved.
