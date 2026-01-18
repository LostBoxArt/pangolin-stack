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

## Core Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Pangolin** | Control plane, user/resource management | 3001 |
| **Gerbil** | WireGuard relay for remote sites | 51820/udp |
| **Traefik** | Reverse proxy with auto-HTTPS | 80, 443 |
| **CrowdSec** | Threat detection & blocking | 6060, 8080 |
| **Traefik Agent** | Log dashboard agent for Traefik | 5000 |
| **Dockhand** | Container management & auto-update | 3000 |

## Add-on Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Olm** | WireGuard client to home network | host network |
| **Traefik Dashboard** | Traefik log analytics UI | 3457 |
| **CrowdSec Web UI** | Security dashboard | 3458 |
| **Pocket ID** | Self-hosted auth provider | 1411 |
| **Homarr** | Dashboard | 7575 |
| **Dashdot** | System dashboard | 3001 |
| **LinkStack** | Link-in-bio landing page | 80 |
| **qbit-proxy** | qBittorrent API proxy | 8081 |
| **Termix** | Web-based SSH terminal | 8080 |


## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/LostBoxArt/pangolin-stack.git
cd pangolin-stack
cp .env.example .env && nano .env

# 2. Start core services
docker compose up -d

# 3. Start add-ons
docker compose -f docker-compose.yml -f docker-compose.addons.yml up -d
```
You can also use `./startup.sh` to pull images and start both core services and add-ons.

## File Structure

```
pangolin-stack/
├── docker-compose.yml          # Core (Pangolin, Gerbil, Traefik, CrowdSec, Traefik Agent, Dockhand) + add-ons (Traefik Dashboard, CrowdSec Web UI, Pocket ID)
├── docker-compose.addons.yml   # Add-ons: Homarr, LinkStack, Dashdot, Termix, qbit-proxy
├── config/
│   ├── pangolin/               # Pangolin config
│   ├── traefik/                # Traefik rules and certs (overrides backed up in rules/resource-overrides.yml.back)
│   └── crowdsec/               # CrowdSec configuration
├── qbit-proxy/                 # qBittorrent proxy (local build)
└── data/                       # Runtime data (gitignored)
```

## Olm Tunnel (Home Network Access)

Widgets access home services (*arr stack) via Olm tunnel:

```
Dashboard → qbit-proxy (optional) → Olm tunnel → Pangolin/Gerbil → Newt → Home Traefik → Services
```

**Configuration:**
- Olm runs as a **systemd service** on the host.
- DNS overrides via `extra_hosts` in dashboard containers.
- Home subnet route: `192.168.0.0/24`

**Troubleshooting:**
```bash
sudo journalctl -u olm -f       # Check systemd tunnel logs
ip addr show olm                # Verify interface exists
ping 192.168.0.10               # Test connectivity to NASUS
sudo systemctl restart olm      # Restart tunnel
```

## Widgets & Integrations (Troubleshooting)

### qBittorrent Authorization Errors
If Homarr shows "Authorization error" for qBittorrent v5.1.4+:
1. Use the **qbit-proxy** sidecar: Set URL to `http://qbit-proxy:8081`.
2. Disable **CSRF** and **Host Validation** in qBittorrent Web UI.
3. Disable **Secure Cookie** in qBittorrent (Web UI).
4. Add `100.90.128.0/24` to the **Waitlist/Bypass Auth** in qBittorrent.

## Common Commands

```bash
# View all containers
docker ps

# Check logs
docker logs <container> --tail 50

# Restart service
docker restart <container>

# Update all images
docker compose pull && docker compose up -d

# Full restart with add-ons
docker compose -f docker-compose.yml -f docker-compose.addons.yml up -d
```

## Access Points

| Service | URL |
|---------|-----|
| Pangolin | https://pangolin.dennisb.xyz |
| CrowdSec | https://crowdsec.dennisb.xyz |
| Traefik Logs | https://traefik-logs.dennisb.xyz |
| Termix | https://termix.dennisb.xyz |
| Pocket ID | https://auth.dennisb.xyz |
| Homarr | https://home.dennisb.xyz |
| Dashdot | https://dash.dennisb.xyz |
| LinkStack | https://dennisb.xyz |
| CrowdSec Web UI | http://<vps-ip>:3458 |
| Dockhand | https://dockhand.dennisb.xyz |


## Documentation

See [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for detailed architecture documentation.
