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
| **dns** | adguard-home, adguardhome-sync | DNS-over-HTTPS with sync |
| **observability** | traefik-agent, traefik-dashboard, dashdot | Monitoring & logs |
| **management** | dockhand | Container management |
| **dashboard** | homarr, qbit-proxy | User dashboards |
| **apps** | linkstack, termix | User applications |

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
```

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

AdGuard Home runs on the CloudNode and syncs blocklists from the home router every 12 hours.

**DoH URL:** `https://dns.example.com/dns-query`

### Device Setup

| Device | Instructions |
|--------|--------------|
| **iPhone/iOS** | Visit dns.example.com → Setup Guide → Download iOS profile |
| **Android 9+** | Settings → Network → Private DNS → `dns.example.com` |
| **Firefox** | Settings → Privacy → Enable DoH → Custom: `https://dns.example.com/dns-query` |
| **Chrome** | Settings → Privacy → Use secure DNS → Custom: `https://dns.example.com/dns-query` |

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
