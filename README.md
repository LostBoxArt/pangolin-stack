# Pangolin Stack

A self-hosted reverse proxy, tunneling, and dashboard solution with enterprise-grade security.

## Architecture

```
Internet → Cloudflare → CloudNode (203.0.113.1) → Traefik → Services
                                    ↓
                              Gerbil (WireGuard)
                                    ↓
                          Home Network (via Newt)
```

## Stacks Overview

| Stack | Services | Purpose |
|-------|----------|---------|
| **core** | pangolin, gerbil, traefik | Core infrastructure (starts first) |
| **security** | crowdsec, crowdsec-web-ui, pocket-id | Security & authentication |
| **observability** | traefik-agent, traefik-dashboard, dashdot | Monitoring & logs |
| **management** | dockhand | Container management |
| **dashboard** | homarr, qbit-proxy | User dashboards |
| **apps** | landing, termix | Landing page; Termix is an older template |

## Repository Template Pins

These older template values are not the current deployment inventory. The
2026-10-27 live audit found Pangolin `1.25.3`, Gerbil `1.5.2`, Traefik
`v3.7.16`, CrowdSec Web UI `2026.10.10`, Newt `1.19.0`, and Olm `1.9.1`.
Do not deploy an older template over that running installation. See the
[maintenance record](docs/wiki/maintenance-2026-10-27.md) and synchronized
host snapshots before a planned upgrade or recovery.

- Pangolin: `fosrl/pangolin:1.17.0`
- Gerbil: `fosrl/gerbil:1.3.1`
- Traefik Badger plugin: `v1.4.0`
- CrowdSec Web UI: `ghcr.io/theduffman85/crowdsec-web-ui:2026.3.1`
- Newt (HomeNode): `fosrl/newt:1.11.0`
- Olm (CloudNode systemd binary): verified `1.9.1` with `--override-dns=false` on 2026-10-27

Newt `1.11.x` aligns with Pangolin `1.17.x` for private resource connection logging, site provisioning keys, and the newer site provisioning flow.
CrowdSec Web UI is pinned to `2026.3.1` because the moving `latest` tag pulled a broken image on March 30, 2026.
Traefik shares Gerbil's network namespace. If `gerbil` is recreated during an upgrade, recreate `traefik` immediately afterward:

```bash
docker compose -f stacks/core/docker-compose.yml --env-file .env up -d --force-recreate traefik
```

When upgrading, check the official update guide and release notes first:
- https://docs.pangolin.net/self-host/how-to-update
- https://github.com/fosrl/pangolin/releases
- https://github.com/fosrl/gerbil/releases
- https://github.com/fosrl/newt/releases
- https://github.com/fosrl/olm/releases
- https://github.com/fosrl/badger/releases

## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/exampleuser/pangolin-stack.git
cd pangolin-stack
cp .env.example .env && nano .env

# 2. Start all stacks (phased startup)
./startup.sh

# 3. Or start individual stacks
./stackctl.sh start core
./stackctl.sh start security
```

## Stack Management

```bash
# View all stack status
./stackctl.sh status

# Start/stop/restart a stack
./stackctl.sh start <stack>
./stackctl.sh stop <stack>
./stackctl.sh restart <stack>

# View stack logs
./stackctl.sh logs <stack>

# Pull latest images
./stackctl.sh pull [stack]

# Stop everything
./stackctl.sh down
```

## Dockhand API

For scripted Dockhand API use, call the Dockhand container on the CloudNode over SSH instead of the public `https://dockhand.example.com` URL. The public URL is fronted by Pangolin auth and redirects browser flows.

Verified flow:

```bash
ssh user@example.com '
DOCKHAND_IP=$(docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}" dockhand | awk "{print \$1}")
curl -sk -c /tmp/dockhand.cookie \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"admin\",\"password\":\"<dockhand-local-password>\"}" \
  "http://${DOCKHAND_IP}:3000/api/auth/login"

TOKEN=$(awk "/dockhand_session/ {print \$7}" /tmp/dockhand.cookie)
curl -sk -H "Cookie: dockhand_session=${TOKEN}" \
  "http://${DOCKHAND_IP}:3000/api/stacks?env=3"
'
```

Environment IDs:
- `1` = CloudNode
- `2` = Nasus (`192.168.0.10`) — stale, no Hawser there since 2026-11-21
- `3` = Rammus (`192.168.0.12`) — the live home environment

## Application Healthchecks (rammus)

Since 2026-11-21 every application runs on **rammus** (`192.168.0.12`). NASUS
(`192.168.0.10`) is pure NFS storage and runs zero containers.

Live healthchecks exist for:

- `traefik`
- `plex`
- `prowlarr`
- `scryer`
- `arr-mcp`
- `hawser`

`newt`, `qbittorrent`, and `dashdot` have no native Docker healthcheck; process
availability is a weaker signal (for `newt`, the watchdog is the real check).
`sonarr`, `radarr`, `bazarr`, `profilarr`, `recyclarr`, `seerr`, `flaresolverr`,
`qui`, and `cleanuparr` were stopped before the migration and are not running.

FileFlows and its Dolby Vision watcher were decommissioned on 2026-10-27. Their containers, deployment files, dedicated data and active integrations have been removed; historical backups are not deployment sources.

Live host paths (rammus):

- `/opt/docker/stacks/<service>/docker-compose.yml`
- `/opt/docker/config/<service>` (appdata, always local SSD)

Repo backup paths (stale, do not deploy):

- `host-configs/homenode/<service>/docker-compose.yml`

## File Structure

```
pangolin-stack/
├── stacks/
│   ├── core/docker-compose.yml         # pangolin, gerbil, traefik
│   ├── security/docker-compose.yml     # crowdsec, crowdsec-web-ui, pocket-id
│   ├── observability/docker-compose.yml # traefik-agent, traefik-dashboard, dashdot
│   ├── management/docker-compose.yml   # dockhand
│   ├── dashboard/docker-compose.yml    # homarr, qbit-proxy
│   └── apps/docker-compose.yml         # linkstack, termix
├── config/                             # Service configs (traefik, crowdsec, pangolin)
├── data/                               # Runtime data (gitignored)
├── .env                                # Shared environment variables
├── startup.sh                          # Start all stacks in order
├── stackctl.sh                         # Stack management utility
└── backup.sh                           # Backup and restore
```

## Olm Tunnel (Home Network Access)

Olm runs as a **systemd service** on the host (not Docker):

```bash
sudo journalctl -u olm -f       # Check logs
ip addr show olm                # Verify interface
ping 192.168.0.12               # Test connectivity to rammus
sudo systemctl restart olm      # Restart tunnel
sudo systemctl status olm-watchdog.timer  # Watchdog timer status
```

`olm` is pinned to run with `--override-dns=false` to prevent DNS lockout during tunnel flaps.

Credentials load from root-only `/root/.config/olm-client/config.json` (`0600`,
parent `0700`) through `CONFIG_FILE`; the unit uses `UMask=0077` and contains no
secret in its command. See [Olm operations](docs/wiki/services/olm.md) and the
sanitized unit in `host-configs/cloudnode/systemd/olm.service`.

## Access Points

| Service | URL |
|---------|-----|
| Pangolin | https://pangolin.example.com |
| CrowdSec | https://crowdsec.example.com |
| Traefik Logs | https://traefik-logs.example.com |
| Pocket ID | https://auth.example.com |
| Homarr | https://home.example.com |
| Dashdot | https://dash.example.com |
| Dockhand | https://dockhand.example.com |
| Landing | https://example.com |
| CrowdSec Web UI | Protected CrowdSec endpoint; host port 3458 is loopback-only |

## Troubleshooting

### qBittorrent Authorization Errors
Use the **qbit-proxy** sidecar in the dashboard stack. Set widget URL to `http://qbit-proxy:8081`.

The proxy uses Node 24, verifies the upstream TLS certificate and aborts requests after 10 seconds. Its Docker healthcheck requires a successful qBittorrent version response through the proxy; an upstream or tunnel failure can make it unhealthy.

### Backup Validation

`backup.sh` creates private archives with validated online SQLite snapshots of
Pangolin, CrowdSec, CrowdSec Web UI, Pocket ID, Dockhand and Homarr. It includes
landing sites, the proxy build context, full CrowdSec configuration, and private
runtime/host recovery metadata. Database consistency is independent per database.
The live script targets the verified deployed layout; reconcile older templates
before deploying or restoring them. See the
[maintenance record](docs/wiki/maintenance-2026-10-27.md) for restore and off-host
verification evidence.

Run the isolated regression checks without contacting production:

```bash
bash -n backup.sh
python3 tests/test_backup.py
node --test qbit-proxy/index.test.js
```

## Security Features

### Geo-Blocking

The stack blocks traffic from **13 high-risk countries** (CN, RU, KP, IR, VN, IN, PK, BD, NG, BR, ID, UA, KZ) while whitelisting Israel and EU.

- **CrowdSec**: GeoIP enrichment with 24h bans for blocked countries
- **Traefik**: Immediate edge blocking using GeoBlock middleware

View geo-blocked IPs: `docker exec crowdsec cscli alerts list --origin custom/country-block`

## Documentation

See [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for detailed architecture documentation.
See [AGENTS.md](AGENTS.md) for agent briefing and operational details.
