---
title: "Monitoring and arr-mcp tunnel operations"
slug: runbook-monitoring-and-arr-mcp
type: runbook
status: active
tags: ["homelab", "runbook", "monitoring", "hermes", "ssh"]
aliases: ["watchdog diagnostics", "arr-mcp tunnel"]
entities:
  primary: runbook-monitoring-and-arr-mcp
  mentions: []
related: ["check-homenode-reachability-via-olm.md", "../services/olm.md"]
sources: ["host-configs/cloudnode/hermes/README.md", "host-configs/cloudnode/systemd/arr-mcp-tunnel.service"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-10-27
---
# Monitoring and arr-mcp tunnel operations

## Monitoring contract

The service watchdog runs every five minutes. Its NAS container inspection uses
one SSH connection per run. Critical CloudNode and HomeNode containers are
included; containers without a Docker healthcheck are checked only for a running
process. This does not establish full application health.

HTTP probes have total deadlines, retain certificate verification, and do not
follow redirects. Public `403` responses are failures. The public landing page
must return `200`; Plex's expected `401` and a protected Home route's expected
`401` or Pangolin authentication redirect are availability/authentication checks.
They do not establish that the protected application's authenticated operations
work. Local HTTP and native Docker health checks cover those separate layers.
Olm is checked independently through Hawser's native health endpoint with curl
forced to the `olm` interface and proxy use disabled. A working Tailscale route
therefore cannot mask a failed Olm data path.

Two consecutive failures produce an alert. Healthy runs are silent; persistent
failures repeat after two hours, and recovery is reported once. At three failed
checks a local-only, no-agent diagnostic consumer records another bounded,
read-only availability snapshot. Neither script performs automatic restarts.
FileFlows and its retired watcher are excluded.

The release watcher is also a no-agent, local-only job. It checks release
metadata daily at 06:00 in Hermes' configured timezone. New releases do not
trigger an upgrade. Historical unknown execution records are retained for audit.

## Verify without delivering alerts

Run on the CloudNode as the account that owns Hermes:

```bash
python3 "$HOME/.hermes/scripts/service-watchdog.py" --dry-run
python3 "$HOME/.hermes/scripts/check-diagnostic-trigger.py" --dry-run
hermes cron list
hermes cron doctor
```

The watchdog dry run reports check results and runtime, without changing state or
triggers. Healthy checks return `ok: true`. The diagnostic dry run normally reports
`pending: false`; pending diagnostics can be inspected without consuming them.
Cron doctor should report no issues. Avoid triggering the watchdog through cron
for a test: its existing origin delivery target remains active.

The deployed five-minute job completed 38 availability, container-health, and
authentication checks in under three seconds on 2026-10-27. Isolated tests cover
the failure threshold, alert deduplication, recovery, diagnostic queue handling,
authentication denials, and HTTP deadlines.

## arr-mcp tunnel

The system service `arr-mcp-tunnel.service` runs SSH as the normal CloudNode user.
It preserves the existing key and strict host-key checking, forwards CloudNode
`127.0.0.1:16060` to HomeNode `127.0.0.1:6060`, and restarts SSH after an unexpected
exit. `After=olm.service` orders startup; it does not start or restart Olm.

Adapt the account and NAS address in the sanitized
[unit template](../../../host-configs/cloudnode/systemd/arr-mcp-tunnel.service)
before installation. The old cron entries and PID-file manager must not own the
same forwarding port while the service runs. Keep a private copy of their
configuration before a cutover.

```bash
systemctl status arr-mcp-tunnel.service --no-pager
systemctl is-enabled arr-mcp-tunnel.service
ss -lntp 'sport = :16060'
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:16060/healthz
"$HOME/.hermes/scripts/home-services.py" mcp-status
```

Expected results are an enabled, active service; a listener only on
`127.0.0.1:16060`; a health response with `status: ok`; and an authenticated MCP
tool listing. The deployment exposed 39 tools when tested. Check the expected
current tool count when arr-mcp is upgraded.

If it fails, inspect the tunnel's journal and the HomeNode reachability runbook:

```bash
sudo journalctl -u arr-mcp-tunnel.service --since '15 minutes ago' --no-pager
```

Do not restart Olm or Docker solely because this client is unavailable. The NAS
SSH service, route, arr-mcp container, and local forwarding listener are separate
failure points.

## Recovery

Keep the previous scripts and job settings privately. A watchdog rollback should
restore the source captured after FileFlows removal, edit the existing schedule
with `hermes cron`, and pause the new diagnostic job if needed. Do not restore an
old complete `jobs.json` over unrelated jobs.

For tunnel rollback, stop and disable the new unit before restoring the former
cron owner and starting the former manager. Verify the loopback health response
and authenticated MCP listing afterward. Keep only one owner of port 16060.

Pause the release watcher if its checks fail. Do not restore its retired automatic
upgrade prompt as a recovery step.

## Sources

- [Hermes cron lifecycle and script-only jobs](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron)
- [systemd 259 service supervision](https://www.freedesktop.org/software/systemd/man/259/systemd.service.html)
- [OpenSSH forwarding and keep-alive options](https://man.openbsd.org/ssh_config)
- [curl total deadlines and response headers](https://curl.se/docs/manpage.html)
