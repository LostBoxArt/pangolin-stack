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
| **dns** | adguard-home | DNS-over-HTTPS \u0026 filtering |
| **observability** | traefik-agent, traefik-dashboard, dashdot | Monitoring & logs |
| **management** | dockhand | Container management |
| **dashboard** | homarr, qbit-proxy | User dashboards |
| **apps** | linkstack, termix | User applications |

## Version Pins

- Pangolin: `fosrl/pangolin:1.17.0`
- Gerbil: `fosrl/gerbil:1.3.1`
- Traefik Badger plugin: `v1.4.0`
- CrowdSec Web UI: `ghcr.io/theduffman85/crowdsec-web-ui:2026.3.1`
- Newt (HomeNode): `fosrl/newt:1.11.0`
- Olm (CloudNode systemd binary): `1.4.4` with `--override-dns=false`

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
  "http://${DOCKHAND_IP}:3000/api/stacks?env=2"
'
```

Environment IDs:
- `1` = CloudNode
- `2` = HomeNode

## HomeNode Healthchecks

The repo now keeps source-controlled copies of the current HomeNode host-side compose files under `host-configs/homenode/`. Current live Docker healthchecks exist for:

- `sonarr`
- `radarr`
- `prowlarr`
- `bazarr`
- `qbittorrent`
- `flaresolverr`
- `plex`
- `traefik`
- `qui`
- `seerr`
- `hawser`

Live host paths:

- `/volume1/docker/config/<service>/docker-compose.yml`
- `/volume1/docker/traefik/docker-compose.yml`

Repo backup paths:

- `host-configs/homenode/<service>/docker-compose.yml`
- `host-configs/homenode/traefik/docker-compose.yml`

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
ping 192.168.1.10               # Test connectivity
sudo systemctl restart olm      # Restart tunnel
sudo systemctl status olm-watchdog.timer  # Watchdog timer status
```

`olm` is pinned to run with `--override-dns=false` to prevent DNS lockout during tunnel flaps.

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
| AdGuard Home | https://dns.example.com |
| LinkStack | https://example.com |
| Termix | https://termix.example.com |
| CrowdSec Web UI | http://<cloudnode-ip>:3458 |

## DNS-over-HTTPS (DoH)

AdGuard Home runs independently on the CloudNode with its own blocklists and configuration.

**DoH URL:** `https://dns.example.com/dns-query`  
**DoT URL:** `dns.example.com:853`

### Device Setup

| Device | Instructions |
|--------|--------------|
| **iPhone/iOS** | Visit dns.example.com → Setup Guide → Download iOS profile |
| **Android 9+** | Settings → Network → Private DNS → `dns.example.com` |
| **Firefox** | Settings → Privacy → Enable DoH → Custom: `https://dns.example.com/dns-query` |
| **Chrome** | Settings → Privacy → Use secure DNS → Custom: `https://dns.example.com/dns-query` |

### Configuration
Manage blocklists and upstream DNS at `https://dns.example.com`

## Troubleshooting

### qBittorrent Authorization Errors
Use the **qbit-proxy** sidecar in the dashboard stack. Set widget URL to `http://qbit-proxy:8081`.

## Security Features

### Geo-Blocking

The stack blocks traffic from **13 high-risk countries** (CN, RU, KP, IR, VN, IN, PK, BD, NG, BR, ID, UA, KZ) while whitelisting Israel and EU.

- **CrowdSec**: GeoIP enrichment with 24h bans for blocked countries
- **Traefik**: Immediate edge blocking using GeoBlock middleware

View geo-blocked IPs: `docker exec crowdsec cscli alerts list --origin custom/country-block`

## Documentation

See [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for detailed architecture documentation.
See [AGENTS.md](AGENTS.md) for agent briefing and operational details.
