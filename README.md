# Pangolin Stack

A self-hosted reverse proxy, tunneling, and dashboard solution with enterprise-grade security.

## Architecture

```
Internet → Cloudflare → VPS (51.195.100.11) → Traefik → Services
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
git clone https://github.com/LostBoxArt/pangolin-stack.git
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
ping 192.168.0.10               # Test connectivity
sudo systemctl restart olm      # Restart tunnel
```

## Access Points

| Service | URL |
|---------|-----|
| Pangolin | https://pangolin.dennisb.xyz |
| CrowdSec | https://crowdsec.dennisb.xyz |
| Traefik Logs | https://traefik-logs.dennisb.xyz |
| Pocket ID | https://auth.dennisb.xyz |
| Homarr | https://home.dennisb.xyz |
| Dashdot | https://dash.dennisb.xyz |
| Dockhand | https://dockhand.dennisb.xyz |
| AdGuard Home | https://dns.dennisb.xyz |
| LinkStack | https://dennisb.xyz |
| Termix | https://termix.dennisb.xyz |
| CrowdSec Web UI | http://<vps-ip>:3458 |

## DNS-over-HTTPS (DoH)

AdGuard Home runs on the VPS and syncs blocklists from the home router every 12 hours.

**DoH URL:** `https://dns.dennisb.xyz/dns-query`

### Device Setup

| Device | Instructions |
|--------|--------------|
| **iPhone/iOS** | Visit dns.dennisb.xyz → Setup Guide → Download iOS profile |
| **Android 9+** | Settings → Network → Private DNS → `dns.dennisb.xyz` |
| **Firefox** | Settings → Privacy → Enable DoH → Custom: `https://dns.dennisb.xyz/dns-query` |
| **Chrome** | Settings → Privacy → Use secure DNS → Custom: `https://dns.dennisb.xyz/dns-query` |

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
