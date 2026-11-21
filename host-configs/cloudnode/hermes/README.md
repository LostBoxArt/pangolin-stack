These are sanitized source copies of the CloudNode's Hermes monitoring scripts.
Production copies live in `$HOME/.hermes/scripts/`; their state and credentials
remain outside Git.

- `service-watchdog.py` runs every five minutes in Hermes **no-agent** mode.
  Healthy runs are silent. Two consecutive failures produce an alert; repeated
  failures alert again after two hours. Recovery is reported once.
- `check-diagnostic-trigger.py` runs one minute after each watchdog interval.
  At three consecutive failures it saves a read-only diagnostic snapshot under
  `$HOME/.hermes/diagnostics/watchdog/`. It never restarts services. Its scheduled
  delivery and failure delivery are local only.
- `hermes-agent-release-check.py` checks public release metadata daily at 06:00
  in the configured Hermes timezone. It runs without an LLM and saves results
  locally. It does not upgrade Hermes or send messages.

The NAS user, example domains, NAS address, and example Tailscale router address
must match the deployment before copying these templates. Retain the deployed
origin delivery target for the existing watchdog job. Manage job definitions
through `hermes cron`; do not overwrite `jobs.json` while the gateway is running.

Run the isolated tests from the repository root:

```bash
python3 host-configs/cloudnode/hermes/scripts/test_watchdog.py
```

Successful verification reports 15 passing tests. The tests make no network
requests and deliver no notifications.

See [the monitoring and tunnel runbook](../../../docs/wiki/runbooks/monitoring-and-arr-mcp.md)
for live checks and recovery. The sibling
[arr-mcp unit template](../systemd/arr-mcp-tunnel.service) is supervised separately
from the watchdog and keeps both tunnel endpoints on loopback.
