---
title: "All sites return 403"
slug: runbook-403-all-sites
type: runbook
status: active
tags: ["homelab", "runbook", "troubleshooting", "crowdsec", "traefik", "cloudflare"]
aliases: ["403 troubleshooting", "all sites down"]
entities:
  primary: runbook-403-all-sites
  mentions: []
related: ["../services/crowdsec.md", "../services/traefik.md", "../hosts/cloudnode.md", "../log.md"]
sources: ["incident 2026-04-21"]
confidence: high
audience_level: operator
last_ingested: 2026-04-21
last_lint: 2026-04-22
---

# All Sites Return 403

When **every** Cloudflare-fronted site returns 403 simultaneously, the cause
is almost always on the **CloudNode origin**, not Cloudflare itself.

## Quick Diagnosis (do these in order)

### 1. Check CrowdSec container status

```bash
docker ps -a | grep crowdsec
```

If the `crowdsec` container (not `crowdsec-web-ui`) is **Exited**, start it:

```bash
docker start crowdsec
```

**Why this matters**: Traefik's `websecure` entrypoint applies the
`crowdsec@file` middleware to **all** requests by default. The CrowdSec
bouncer plugin fails closed — if it cannot reach the CrowdSec LAPI on
`crowdsec:8080`, it returns 403 for every request.

This has happened before (2026-04-21) when CrowdSec exited after a CloudNode
reboot or resource pressure. The `crowdsec-web-ui` container may still be
running, which is misleading.

### 2. Verify origin health directly (bypass Cloudflare)

```bash
# Test the origin directly via the CloudNode public IP
curl -sI -H "Host: example.com" --resolve example.com:443:203.0.113.1 \
  https://example.com
```

- If this returns **200** but Cloudflare returns 403 → Cloudflare is
  serving a cached challenge or has a WAF rule active. Purge Cloudflare
  cache or check Security Events.
- If this returns **403** → the problem is on the origin. Go to step 3.

### 3. Check Traefik access logs for the real source IP

```bash
docker exec traefik sh -c "tail -50 /var/log/traefik/access.log" | \
  jq -r '[.ClientHost, .RequestHost, .DownstreamStatus, .RequestPath] | @tsv"
```

Look for patterns:
- `DownstreamStatus: 403` with `OriginStatus: 0` and tiny `Duration`
  → middleware blocked it before reaching the backend (likely CrowdSec).
- `DownstreamStatus: 403` with `OriginStatus: 403`
  → the backend service returned 403 (not a middleware issue).

### 4. Check CrowdSec decisions explicitly

```bash
docker exec crowdsec cscli decisions list --ip <your-ip>
```

If your IP is banned, the bouncer is working correctly — you just need to
remove the ban or wait it out.

### 5. Check Cloudflare Security Events (if origin is healthy)

Log into [dash.cloudflare.com](https://dash.cloudflare.com) → Security →
Events. Look for:
- **Managed challenges** or **Blocks** on your IP
- Security Level set to "High" or "I'm Under Attack"
- Super Bot Fight Mode being overly aggressive

If Cloudflare is challenging, purge cache (Caching → Purge Everything) and
add your IP to the Allowlist (Security → WAF → Tools).

## Common False Leads

| Symptom | What it looks like | Reality |
|---|---|---|
| `cf-mitigated: challenge` header | Cloudflare is blocking your IP | Cloudflare cached the challenge while the origin was broken. Fix origin first. |
| Both home ISP and cellular get 403 | Must be a Cloudflare-wide block | More likely CrowdSec down, which blocks ALL IPs. |
| `server: cloudflare` in response | Cloudflare is the problem | Cloudflare always adds this header. Check `server-timing` for `chlray` (challenge) vs nothing (pass-through). |

## HomeNode SSH Tunnel Issues (separate from 403s)

If Termix or other SSH-through-tunnel connections fail with "Connection lost
before handshake" while direct CloudNode SSH works:

### Diagnosis

```bash
# From CloudNode, test through tunnel
ssh -vvv -o ConnectTimeout=5 jesus@192.168.1.10 echo test 2>&1 | \
  grep -E "kex_exchange|banner|Connection closed"
```

- `kex_exchange_identification: banner line 0: Not allowed at this time`
  → Asustor penalty table is blocking the source IP.
- Check if the CloudNode OpenSSH client was recently updated:
  ```bash
  ssh -V  # e.g., OpenSSH_10.0p2 Ubuntu-5ubuntu5.1
  ```

### Important Finding (2026-04-21)

The penalty table was a **symptom**, not the root cause. The actual issue
was an OpenSSH client incompatibility that caused Asustor's custom
`sshd-session` binary to crash with a seccomp violation (SIGSYS, syscall
87). Every crash added the source IP to the penalty table.

**Fix**: Updating the CloudNode's OpenSSH client (`apt upgrade`) resolved
the incompatibility. After the update, tunnel SSH worked immediately.

**Clearing the penalty table** (when needed):

```bash
# Hard restart from an existing session (session drops)
sudo kill -9 $(cat /var/run/sshd.pid); sleep 3; sudo $(which sshd)

# Or via Asustor ADM GUI: Services → Terminal → toggle SSH Off/On
```

`SIGHUP` (reload) does **not** clear the penalty table — verify with
`pgrep sshd` that the PID changed.

## Prevention

1. **Monitor CrowdSec container health**: Add a Dockhand alert or healthcheck
   that fires if `crowdsec` exits.
2. **Keep OpenSSH updated**: The CloudNode's SSH client can trigger
   HomeNode-side bugs if outdated.
3. **Document changes**: When the origin is fixed, purge Cloudflare cache
   to avoid stale challenge pages.
