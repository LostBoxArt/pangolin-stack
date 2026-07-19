---
title: "Tunnel down + all HomeNode services unreachable"
slug: runbook-tunnel-down-all-homenode-down
type: runbook
status: active
tags: ["homelab", "runbook", "troubleshooting", "newt", "gerbil", "pangolin", "tunnel", "dns", "docker", "homenode"]
aliases: ["tunnel down", "all homenode services down", "newt cannot reconnect", "docker dns 127.0.0.11 broken", "502 all homenode sites"]
entities:
  primary: runbook-tunnel-down-all-homenode-down
  mentions: ["newt", "gerbil", "pangolin", "traefik", "dockerd"]
related:
  - "../services-homenode/newt.md"
  - "../services/gerbil.md"
  - "../services/pangolin.md"
  - "../services/traefik.md"
  - "../hosts/homenode.md"
  - "../hosts/cloudnode.md"
  - "./403-all-sites.md"
  - "../log.md"
sources: ["incident 2026-07-18"]
confidence: high
audience_level: operator
last_ingested: 2026-07-18
last_lint: 2026-07-18
---

# Tunnel Down + All HomeNode Services Unreachable

When every `*.example.com` site that routes to HomeNode returns 502, 000
(timeout), or Pangolin's "site offline" page simultaneously, the cause is
either the **Pangolin tunnel (newt/gerbil)** or the **Docker embedded DNS
proxy on HomeNode**. Both produce the same user-visible symptom: HomeNode
services are unreachable from the public internet.

This runbook covers the full diagnostic path from "everything pointing at
HomeNode is down" to "root cause identified and fixed." It is deliberately
detailed because the failure mode has multiple layers and the obvious
debugging steps lead to the wrong fix.

## Architecture: How HomeNode services are reached

```
Client → Cloudflare → CloudNode Traefik (TLS termination)
       → CloudNode Traefik routes HomeNode-backed domains to
         https://<tunnel-ip>:<port> (the Pangolin tunnel IP for the homelab site)
       → Gerbil (WireGuard relay on CloudNode) forwards TCP/UDP over the
         tunnel to HomeNode
       → Newt (Pangolin site connector on HomeNode) receives tunnel traffic
         and forwards to the target IP:port (e.g. 192.168.1.10:443)
       → HomeNode Traefik (port 443 on the NAS) routes by Host header to
         the final container (e.g. seerr:5055, plex:32400)
```

There are **two Traefik instances** in this stack:

| Traefik | Location | Role |
|---|---|---|
| CloudNode Traefik | CloudNode (VPS) | Public edge, TLS termination for `*.example.com`, routes HomeNode-backed domains through the tunnel |
| HomeNode Traefik | HomeNode (NAS), port 443 | LAN reverse proxy, routes by Host header to HomeNode containers (seerr, plex, sonarr, etc.) |

Both must be healthy for HomeNode-backed public URLs to work. The CloudNode
Traefik routes to the tunnel IP; the HomeNode Traefik receives the tunneled
request and forwards to the container.

## Quick Triage (do these in order)

### 0. Check the Pangolin site status first

```bash
sqlite3 ~/pangolin-stack/config/db/db.sqlite \
  "SELECT siteId, name, online, lastPing, subnet, endpoint FROM sites WHERE name='homelab';"
```

- `online=1` → tunnel control channel is up. The issue is either the data
  path (Gerbil/WireGuard forwarding) or the HomeNode Traefik/container
  layer. Skip to step 2.
- `online=0` → tunnel control channel is down. Newt is not connected to
  Pangolin. Go to step 1.

Convert `lastPing` from Unix timestamp to UTC to see when the tunnel last
checked in:

```bash
python3 -c "from datetime import datetime; print(datetime.utcfromtimestamp(<lastPing>).strftime('%Y-%m-%d %H:%M:%S UTC'))"
```

### 1. If `online=0`: Newt cannot connect to Pangolin

Check newt logs on HomeNode:

```bash
ssh jesus@192.168.1.10 "docker logs newt --tail=20 2>&1"
```

Common failure patterns and their root causes:

| Log pattern | Root cause | Fix |
|---|---|---|
| `lookup pangolin.example.com on 127.0.0.11:53: connection refused` | Docker embedded DNS proxy is dead | See **Docker DNS proxy dead** section below |
| `failed to get token: failed to request new token` (repeating every 3s) | Newt cannot reach Pangolin API — usually DNS or network | Check DNS proxy first, then network reachability |
| `Public key mismatch` / endpoint churn every ~2 min | Home ISP NAT rebinding — new endpoint port each time | Usually self-heals; if persistent, see **NAT rebinding churn** below |
| No logs at all / container exited | Newt crashed or was recreated | `docker compose up -d` in `/volume1/docker/config/newt/` |
| `i/o timeout` dialing Pangolin | CloudNode unreachable from HomeNode | Check HomeNode → CloudNode network path (NAT, firewall, ISP) |

### 2. If `online=1` but sites still 502/timeout: check the data path

The control channel (WebSocket) can be up while the WireGuard data path is
broken. This happens when Gerbil's peer churn has desynced the session.

```bash
# Check Gerbil logs for peer churn
docker logs gerbil --tail=30 2>&1 | grep -E "Peer|proxy mappings|Rebuilt"
```

If you see repeated `Peer <key> removed` / `Peer <key> added` cycles every
2-3 minutes, the home ISP is doing NAT rebinding and the tunnel data path
is unstable. See **NAT rebinding churn** below.

```bash
# Test the tunnel data path directly from CloudNode
curl -sk -o /dev/null -w "HTTP %{http_code} time=%{time_total}s\n" \
  --max-time 10 -H "Host: plex.example.com" \
  https://<tunnel-ip>:443/
```

- Timeout (HTTP 000) → Gerbil is not forwarding to HomeNode. Check Gerbil
  peer state and HomeNode newt.
- 502 → Gerbil forwarded but HomeNode Traefik/backend is down. Check
  HomeNode Traefik and the target container.
- 200/302/401 → tunnel works; the issue is a specific route or container.

### 3. Check HomeNode Traefik and containers

```bash
# From CloudNode, via SSH to HomeNode
ssh jesus@192.168.1.10 "docker ps --format '{{.Names}} {{.Status}}' | head -20"
ssh jesus@192.168.1.10 "docker logs traefik --tail=20 2>&1"
```

If `docker ps` fails with "permission denied while trying to connect to
the Docker daemon socket", the Docker wrapper on HomeNode is broken. See
**Docker wrapper broken** below.

### 4. Check CloudNode Traefik routes

```bash
# List routers matching HomeNode-backed domains
docker exec traefik wget -qO- --timeout=3 http://localhost:8080/api/http/routers 2>&1 | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data:
    name = r.get('name', '?')
    rule = r.get('rule', '?')
    status = r.get('status', '?')
    service = r.get('service', '?')
    print(f'{status:8s} {name:40s} svc={service:30s} {rule}')
"
```

```bash
# List service backends and their status
docker exec traefik wget -qO- --timeout=3 http://localhost:8080/api/http/services 2>&1 | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for s in data:
    name = s.get('name', '?')
    status = s.get('status', '?')
    servers = s.get('serverStatus', {})
    server_info = ' '.join([f'{url}={st}' for url, st in servers.items()])
    print(f'{status:8s} {name:40s} {server_info}')
"
```

HomeNode-backed services will show backends like `https://<tunnel-ip>:443`
(the tunnel IP) or `http://<tunnel-ip>:32400`. The `=UP` status only means
Traefik's last health check passed — it does NOT mean the tunnel is
currently forwarding.

### 5. Check the Pangolin target mapping

The Pangolin database stores which IP:port each domain maps to. Traefik
reads these via Pangolin's HTTP provider.

```bash
sqlite3 ~/pangolin-stack/config/db/db.sqlite \
  "SELECT t.targetId, r.subdomain, t.ip, t.port, t.internalPort, t.method, t.enabled
   FROM targets t JOIN resources r ON t.resourceId = r.resourceId
   ORDER BY r.subdomain;"
```

Typical HomeNode-backed targets:

| subdomain | ip | port | method | meaning |
|---|---|---|---|---|
| plex | 192.168.1.10 | 32400 | http | direct to HomeNode Plex port |
| request | 192.168.1.10 | 443 | https | to HomeNode Traefik, which routes to seerr |

The `ip` here is the HomeNode LAN IP as seen by newt. Traefik sees the
tunnel IP (`<tunnel-ip>`) because Pangolin translates the target IP
to the tunnel subnet when serving the config to Traefik.

## Root Cause: Docker DNS proxy dead (most common)

**This is the single most likely root cause when newt cannot reconnect and
all HomeNode sites are down.**

### Symptoms

- Newt logs show: `lookup pangolin.example.com on 127.0.0.11:53: read udp
  127.0.0.1:xxxxx->127.0.0.11:53: read: connection refused` repeating
  every 3 seconds
- Any `docker exec <container> nslookup <hostname>` from HomeNode fails
  with the same `127.0.0.11:53: connection refused` error
- `docker exec <container> cat /etc/resolv.conf` shows `nameserver
  127.0.0.11` (Docker's embedded DNS proxy)
- Host DNS works fine: `nslookup google.com` from the HomeNode shell
  resolves normally via 192.168.1.1
- Containers on `--network host` still resolve (they bypass the proxy and
  use the host resolv.conf directly)
- Nothing is listening on 127.0.0.11:53 inside any container

### Root cause

The `dockerd` process's embedded DNS proxy has died while `dockerd` itself
keeps running. Docker injects `127.0.0.11` as the nameserver into every
container on a user-defined bridge network, and the dockerd process is
supposed to run a DNS forwarder on that address that resolves container
hostnames and forwards external queries to the host's configured
nameservers. When that forwarder dies, every container on a user-defined
bridge loses DNS entirely.

This is NOT a config issue — it's a runtime failure of dockerd's internal
DNS forwarder. No amount of `dns:` directives in compose files or
resolv.conf overrides inside containers will fix it, because Docker forces
`127.0.0.11` as the resolver regardless.

### Why this breaks the tunnel

Newt authenticates to Pangolin by POSTing to
`https://pangolin.example.com/api/v1/auth/newt/get-token`. If it cannot
resolve `pangolin.example.com`, it cannot get a token, and it cannot
establish the WebSocket control channel or the WireGuard tunnel. Newt
retries every 3 seconds, but every retry fails at DNS resolution.

### Fix: restart dockerd on HomeNode (Asustor AppCentral)

Asustor does NOT have `systemctl` or `synoservicectl`. The AppCentral
`start-stop.sh` `reload` action only restarts containers, not the daemon.
You must restart `dockerd` itself.

**Preferred method: Asustor GUI**

The cleanest way is to restart the Docker package from the Asustor ADM
GUI: App Central → Docker → disable, then enable. This cleanly stops and
starts `dockerd` and all containers come back via their restart policies.

**Alternative: CLI restart**

If the GUI is unavailable, restart dockerd from the command line:

```bash
# 1. Find dockerd PID
ssh jesus@192.168.1.10 "ps | grep dockerd | grep -v grep"
# Note the PID (e.g. 9506)

# 2. Kill dockerd (graceful TERM)
ssh jesus@192.168.1.10 "echo 'PASSWORD' > /tmp/.p && sudo -S < /tmp/.p kill -TERM <PID>; rm -f /tmp/.p"

# 3. Start dockerd with the original args (copy from the ps output above)
ssh jesus@192.168.1.10 "echo 'PASSWORD' > /tmp/.p && sudo -S < /tmp/.p sh -c 'export DOCKER_RAMDISK=true; /volume1/.@plugins/AppCentral/docker-ce/bin/dockerd --debug --log-level info --data-root /volume1/.@plugins/AppCentral/docker-ce/docker_lib/ --iptables=false >/tmp/dockerd-restart.log 2>&1 &'; rm -f /tmp/.p"

# 4. Wait ~8s for dockerd to come back and containers to restart
sleep 8
ssh jesus@192.168.1.10 "ps | grep dockerd | grep -v grep; docker ps --format '{{.Names}} {{.Status}}'"

# 5. Verify the DNS proxy is working again
ssh jesus@192.168.1.10 "docker exec newt nslookup pangolin.example.com 2>&1 | head -5"
# Should resolve via 192.168.1.1 (host's nameserver, forwarded by Docker's proxy)

# 6. Verify newt reconnected
ssh jesus@192.168.1.10 "docker logs newt --tail=15 2>&1"
# Should show "Server ready" and active UDP copyPacketData lines
```

All 16 HomeNode containers have `restart: unless-stopped` — they come
back automatically after a dockerd restart. No need to manually start
each one.

### What does NOT fix this

| Attempted fix | Why it doesn't work |
|---|---|
| `dns: [192.168.1.1]` in docker-compose.yml | Docker still forces `127.0.0.11` as the proxy; the directive only changes the upstream forwarder list, which is moot because the proxy itself is dead |
| Overriding `/etc/resolv.conf` inside the container | Newt (and most containers) are on user-defined bridge networks with no route to 192.168.1.1 — they only have routes to 172.x.0.0/16 subnets. Pointing at the LAN DNS doesn't help because the container can't reach it. |
| Restarting individual containers | The DNS proxy is a dockerd process, not per-container. Restarting containers just reconnects them to the same dead proxy. |
| Restarting newt alone | Newt will still fail to resolve Pangolin's hostname. |

### Post-fix verification

```bash
# 1. DNS works inside containers
ssh jesus@192.168.1.10 "docker exec newt nslookup pangolin.example.com 2>&1 | head -3"
# Should show: Server: 192.168.1.1, then the resolved address

# 2. Pangolin sees the site as online
sqlite3 ~/pangolin-stack/config/db/db.sqlite \
  "SELECT siteId, name, online, lastPing FROM sites WHERE name='homelab';"
# Should show online=1 and a recent lastPing

# 3. Newt is passing tunnel traffic
ssh jesus@192.168.1.10 "docker logs newt --tail=10 2>&1"
# Should show "UDP copyPacketData" lines (tunnel data flowing)

# 4. All public URLs respond
for url in plex.example.com request.example.com dash.example.com \
           dockhand.example.com termix.example.com hermi.example.com \
           home.example.com; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://$url/")
  echo "$url → $code"
done
# Expect: plex 401, request 307, dash 200, dockhand 302,
#         termix 200, hermi 302, home 302
```

## Root Cause: NAT rebinding churn (intermittent)

### Symptoms

- Pangolin `online=1` but sites intermittently 502/timeout
- Gerbil logs show repeated peer add/remove cycles every 2-3 minutes:
  ```
  Peer <key1> removed successfully
  Peer <key2> added successfully
  Updated proxy mappings from <tunnel-ip>:xxxxx to <tunnel-ip>:yyyyy
  ```
- Newt logs show `Public key mismatch` messages when it reconnects
- Each cycle has a different endpoint port for the same WireGuard peer

### Root cause

The home ISP assigns a new source port to outbound UDP traffic
periodically (every 2-10 minutes). Since newt's WireGuard traffic to
Gerbil is outbound UDP, the endpoint that Gerbil sees keeps changing.
Gerbil interprets each new source port as a new peer (with a new public
key from the rebinding), removes the old peer, and adds the new one. This
tears down and rebuilds the tunnel data path repeatedly.

This is a transient condition that usually self-heals — the tunnel works
between rebinding events. If the rebinding frequency is high enough (every
2 minutes), users see intermittent 502s and timeouts.

### Fix

There is no clean fix for ISP-side NAT rebinding. Options:

1. **Wait it out** — the ISP usually settles after a period. Most
   sessions work fine.
2. **Request a static IP from the ISP** — eliminates NAT rebinding
   entirely.
3. **Configure the home router for a persistent NAT mapping for UDP
   51820** (WireGuard port) — if the router supports it, pin the source
   port so it doesn't rebind.
4. **Reduce Gerbil's sensitivity to endpoint changes** — not currently
   exposed as a config option in Gerbil 1.3.x.

Do NOT restart Gerbil or newt to "fix" this — it will not help and may
make the churn worse by forcing a full re-handshake.

## Root Cause: Docker wrapper broken on HomeNode

### Symptoms

- `ssh jesus@192.168.1.10 "docker ps"` fails with:
  `permission denied while trying to connect to the Docker daemon socket
  at unix:///var/run/docker.sock`
- The watchdog reports all HomeNode SSH services as down simultaneously
- Direct `docker` commands work with `sudo` but not as the `jesus` user

### Root cause

The file `/usr/local/bin/docker` on HomeNode is supposed to be a wrapper
script that runs the real Docker binary via `sudo -n` (non-interactive,
passwordless):

```sh
#!/bin/sh
exec /usr/builtin/bin/sudo -n /usr/local/AppCentral/docker-ce/bin/docker "$@"
```

This wrapper can be clobbered by:

1. **Asustor GUI Docker restart** (App Central → Docker → disable/enable)
   — replaces the wrapper with a plain symlink to the real binary
2. **Asustor AppCentral Docker package update** — same as above
3. **Manual `docker-ce` package reinstall**

When the wrapper is replaced with a plain symlink, the `jesus` user runs
the raw Docker binary, which tries to connect to the Docker socket
directly. The socket is owned by `root:root` with mode `srw-rw----`, and
`jesus` is not in a Docker-capable group, so the connection is refused.

The sudoers rule at `/etc/sudoers.d/99-jesus-docker` typically survives
these events — only the wrapper file gets clobbered.

### Fix: restore the wrapper

```bash
ssh jesus@192.168.1.10 "echo 'PASSWORD' > /tmp/.p && sudo -S < /tmp/.p sh -c 'rm -f /usr/local/bin/docker && cat > /usr/local/bin/docker << \"EOF\"
#!/bin/sh
exec /usr/builtin/bin/sudo -n /usr/local/AppCentral/docker-ce/bin/docker \"\$@\"
EOF
chmod +x /usr/local/bin/docker'; rm -f /tmp/.p"

# Verify
ssh jesus@192.168.1.10 "head -3 /usr/local/bin/docker; docker ps --format '{{.Names}} {{.Status}}' | head -5"
```

The sudoers rule should already be intact. If it's also missing, recreate
it:

```bash
ssh jesus@192.168.1.10 "echo 'PASSWORD' > /tmp/.p && echo 'jesus ALL=(root) NOPASSWD: /usr/local/AppCentral/docker-ce/bin/docker' > /tmp/.s && sudo -S < /tmp/.p cp /tmp/.s /etc/sudoers.d/99-jesus-docker && sudo -S < /tmp/.p chmod 440 /etc/sudoers.d/99-jesus-docker && rm -f /tmp/.s /tmp/.p && echo DONE"
```

**Important**: The sudoers rule must match the target of the `exec` in the
wrapper (`/usr/local/AppCentral/docker-ce/bin/docker`), NOT the wrapper
path (`/usr/local/bin/docker`). `sudo -n` checks the path of the command
it's asked to execute, which is the real binary.

### Prevention

After any Asustor GUI Docker restart or Docker package update, verify the
wrapper is intact:

```bash
ssh jesus@192.168.1.10 "head -1 /usr/local/bin/docker"
# Should show: #!/bin/sh
# If it shows binary garbage or a symlink, restore the wrapper
```

## Root Cause: SSH blocked by Asustor penalty table / fail2ban

### Symptoms

- `ssh jesus@192.168.1.10` fails with `Connection closed by
  192.168.1.10 port 22` or `Not allowed at this time` during key exchange
- The watchdog cannot reach HomeNode via SSH
- Rapid SSH retry loops make the block worse

### Root cause

Asustor's SSH daemon has a penalty table that blocks source IPs after
repeated failed authentication attempts. This is separate from fail2ban
(though both may be present). The block can be triggered by:

1. Too many failed SSH key auth attempts in a short window
2. Incompatible SSH client versions causing `sshd-session` crashes (see
   the 2026-04-21 incident in `log.md`)
3. Rapid retry loops during debugging (an agent retrying SSH every few
   seconds will trip this)

### Fix

Wait 10-15 minutes for temporary bans to expire, or clear the penalty
table from an existing HomeNode session:

```bash
# Hard restart of sshd (session drops, so run from a different session)
sudo kill -9 $(cat /var/run/sshd.pid); sleep 3; sudo $(which sshd)
```

`SIGHUP` (reload) does NOT clear the penalty table — the PID stays the
same and the table persists. A hard restart (`kill -9`) or ADM GUI toggle
(Services → Terminal → SSH Off/On) is required.

If fail2ban is also present:

```bash
sudo fail2ban-client set sshd unbanip <cloudnode-ip>
```

### Prevention

- Avoid rapid SSH retry loops. Wait 30+ seconds between attempts when SSH
  is failing.
- Do not run SSH commands in tight loops from scripts or agents.
- If writing an agent that SSHes to HomeNode, add exponential backoff on
  connection failure.

## Root Cause: CloudNode Traefik restarted during debugging

### Symptoms

- All `*.example.com` sites return 502 or timeout immediately after a
  CloudNode Traefik restart
- HomeNode-backed sites may stay down for several minutes even after the
  tunnel is healthy
- Traefik may pick up stale backend IPs from the Pangolin HTTP provider

### Root cause

Restarting CloudNode Traefik during troubleshooting disrupts ALL public
routing. Even a brief restart causes public URLs to return 502/000 for
minutes afterward, and Traefik may serve stale Pangolin config until its
next poll cycle.

### Fix

Do not restart CloudNode Traefik during debugging unless it is genuinely
the problem. The watchdog checks `http://127.0.0.1:80/` for Traefik
health — if that returns 404, Traefik is fine.

If Traefik was restarted and sites are slow to recover:

```bash
# Wait for Traefik to re-poll Pangolin (usually 30-60s)
sleep 60

# Verify all public URLs
for url in plex.example.com request.example.com dash.example.com \
           dockhand.example.com termix.example.com hermi.example.com \
           home.example.com; do
  code=$(curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://$url/")
  echo "$url → $code"
done
```

## Container-level diagnosis: specific service 502

If the tunnel is up and most sites work but one specific site returns 502,
the issue is the route or the target container, not the tunnel.

### Check the Pangolin target mapping

```bash
sqlite3 ~/pangolin-stack/config/db/db.sqlite \
  "SELECT t.targetId, r.subdomain, t.ip, t.port, t.internalPort, t.method, t.enabled
   FROM targets t JOIN resources r ON t.resourceId = r.resourceId
   WHERE r.subdomain='<problematic-subdomain>';"
```

Verify the `ip` is the HomeNode LAN IP and `port` is correct for the
service.

### Check HomeNode Traefik routes

```bash
ssh jesus@192.168.1.10 "docker exec traefik wget -qO- --timeout=3 http://localhost:8080/api/http/routers 2>&1" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for r in data:
    if '<subdomain>' in r.get('rule', '').lower():
        print(json.dumps(r, indent=2))
"
```

There may be duplicate routers (one from file config, one from Docker
labels) for the same Host rule. Both should point to the same backend. If
they conflict, the file-based router typically wins.

### Check the target container directly

```bash
ssh jesus@192.168.1.10 "docker inspect <container> --format 'state={{.State.Status}} health={{.State.Health.Status}}'"
ssh jesus@192.168.1.10 "docker logs <container> --tail=30 2>&1"
ssh jesus@192.168.1.10 "curl -s -o /dev/null -w 'HTTP %{http_code}' --max-time 5 http://<container-ip>:<port>/"
```

### Expected HTTP codes (healthy services)

| URL | Expected code | Meaning |
|---|---|---|
| `plex.example.com` | 401 | Plex auth challenge (normal — the app loads) |
| `request.example.com` | 307 | Seerr redirect to login page |
| `dash.example.com` | 200 | Dashdot dashboard loads |
| `dockhand.example.com` | 302 | Dockhand redirect to login |
| `termix.example.com` | 200 | Termix web UI loads |
| `hermi.example.com` | 302 | Hermes redirect |
| `home.example.com` | 302 | Homarr redirect |

Codes other than these (especially 502, 000, 503) indicate a problem with
that specific route or container.

## HomeNode container inventory (July 2026)

16 containers running on HomeNode, all with `restart: unless-stopped`:

| Container | Purpose | Watchdog-monitored |
|---|---|---|
| `traefik` | HomeNode reverse proxy (port 443) | no (NAS Traefik) |
| `newt` | Pangolin tunnel connector | no (checked via Pangolin site status) |
| `sonarr` | TV series manager | yes |
| `radarr` | Movie manager | yes |
| `qbittorrent` | Torrent client | yes |
| `prowlarr` | Indexer manager | yes |
| `seerr` | Media request front-end | yes |
| `bazarr` | Subtitle manager | yes |
| `plex` | Media server | yes |
| `qui` | autobrr qBit UI | no |
| `cleanuparr` | Download cleanup automation | no |
| `hawser` | Dockhand remote agent | no |
| `profilarr` | Profile manager for *arr | no |
| `recyclarr` | TRaSH-Guides sync | no |
| `dash` | HomeNode dashdot | no |
| `flaresolverr` | Cloudflare challenge solver | no |

## Sudo password handling via SSH

The HomeNode sudo password contains shell-special characters. When sudo
requires a password (e.g., to recreate the sudoers file or restart
dockerd), the password cannot be piped via `echo 'pass' | sudo -S` if it
contains `!` (shell history expansion).

Use a file-based approach:

```bash
ssh jesus@192.168.1.10 "echo 'PASSWORD' > /tmp/.p && sudo -S < /tmp/.p <command>; rm -f /tmp/.p"
```

Or disable history expansion first: `set +H` in the shell before any
command containing `!`.

The sudo password is stored in the Hermes fact_store — query it or ask
the user. Do NOT guess or try variants blindly; failed attempts trigger
the Asustor penalty table block.

## Decision flowchart

```
All HomeNode-backed sites down?
│
├── Check Pangolin site status (sqlite3 query)
│   │
│   ├── online=0 (tunnel control down)
│   │   │
│   │   ├── Check newt logs on HomeNode
│   │   │   │
│   │   │   ├── "127.0.0.11:53 connection refused"
│   │   │   │   → Docker DNS proxy dead → restart dockerd
│   │   │   │
│   │   │   ├── "failed to get token" (without DNS error)
│   │   │   │   → Network issue HomeNode→CloudNode → check routing
│   │   │   │
│   │   │   └── Container exited/crashed
│   │   │       → docker compose up -d in /volume1/docker/config/newt/
│   │   │
│   │   └── Check SSH access to HomeNode
│   │       │
│   │       ├── "Connection closed" / "Not allowed at this time"
│   │       │   → SSH blocked by penalty table → wait or clear
│   │       │
│   │       └── "permission denied" on docker commands
│   │           → Docker wrapper broken → restore wrapper
│   │
│   └── online=1 (tunnel control up, data path down)
│       │
│       ├── Check Gerbil logs for peer churn
│       │   │
│       │   ├── Repeated peer add/remove every 2-3 min
│       │   │   → NAT rebinding → wait it out
│       │   │
│       │   └── No churn
│       │       → Check tunnel data path with curl to tunnel IP
│       │
│       └── Check HomeNode Traefik and containers
│           │
│           ├── Traefik down → docker start traefik
│           │
│           └── Target container down/unhealthy
│               → docker logs <container>, inspect health
│
└── Only one site down?
    → Container-level diagnosis (see that section)
```

## Lessons learned (2026-07-18 incident)

1. **Search session history first.** The Docker wrapper + sudoers fix was
   documented in a May 8, 2026 session. Re-deriving it from scratch wasted
   time and led to a wrong initial fix (creating a sudoers rule for the
   wrapper path instead of the real binary path).

2. **Do not restart CloudNode Traefik during debugging.** It disrupts all
   public routing and makes the diagnostic picture worse. The watchdog's
   Traefik check (`http://127.0.0.1:80/` → 404) is sufficient to confirm
   Traefik health.

3. **Do not tinker with DNS when the real issue is the tunnel.** The
   tunnel drop was caused by the Docker DNS proxy dying, not by a DNS
   config problem. Adding `dns:` directives or overriding resolv.conf
   inside containers does not fix a dead dockerd DNS proxy.

4. **The Docker DNS proxy dying is a runtime failure, not a config issue.**
   It cannot be fixed by config changes — only by restarting dockerd.
   Recognize the symptom (`127.0.0.11:53: connection refused` from inside
   any container) and go straight to the dockerd restart.

5. **The Asustor GUI Docker restart clobbers the wrapper.** After any
   GUI-level Docker restart, verify that `/usr/local/bin/docker` is still
   the wrapper script and not a plain symlink. The sudoers rule survives;
   the wrapper does not.

6. **Avoid rapid SSH retry loops.** They trigger the Asustor penalty
   table, which blocks the CloudNode IP and prevents further diagnosis.
   Wait 30+ seconds between SSH attempts when debugging connection
   issues.

7. **Pangolin `online=1` does not mean the data path works.** The
   WebSocket control channel can be up while WireGuard forwarding is
   broken (NAT rebinding, peer churn). Always test the data path with a
   direct curl to the tunnel IP.

8. **All 16 HomeNode containers have `restart: unless-stopped`.** A
   dockerd restart is safe — everything comes back automatically. Do not
   hesitate to restart dockerd when the DNS proxy is dead.
