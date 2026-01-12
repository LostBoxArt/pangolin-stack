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

## Core Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Pangolin** | Control plane, user/resource management | 3001 |
| **Gerbil** | WireGuard relay for remote sites | 51820/udp |
| **Traefik** | Reverse proxy with auto-HTTPS | 80, 443 |
| **CrowdSec** | Threat detection & blocking | 6060, 8080 |
| **Traefik Agent** | Log dashboard agent for Traefik | 5000 |

## Add-on Components

| Component | Purpose | Port |
|-----------|---------|------|
| **Olm** | WireGuard client to home network | host network |
| **Traefik Dashboard** | Traefik log analytics UI | 3457 |
| **CrowdSec Web UI** | Security dashboard | 3458 |
| **Pocket ID** | Self-hosted auth provider | 1411 |
| **Portainer** | Docker management | 9000, 9443 |
| **Homarr** | Dashboard | 7575 |
| **Dashdot** | System dashboard | 3001 |
| **LinkStack** | Link-in-bio landing page | 80 |
| **qbit-proxy** | qBittorrent API proxy | 8081 |
| **Termix** | Web-based SSH terminal | 8080 |


## Quick Start

```bash
# 1. Clone and configure
git clone https://github.com/exampleuser/pangolin-stack.git
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
├── docker-compose.yml          # Core (Pangolin, Gerbil, Traefik, CrowdSec, Traefik Agent) + add-ons (Traefik Dashboard, CrowdSec Web UI, Pocket ID, Portainer)
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
- Home subnet route: `192.168.1.0/24`

**Troubleshooting:**
```bash
sudo journalctl -u olm -f       # Check systemd tunnel logs
ip addr show olm                # Verify interface exists
ping 192.168.1.10               # Test connectivity to HomeNode
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
| Pangolin | https://pangolin.example.com |
| CrowdSec | https://crowdsec.example.com |
| Traefik Logs | https://traefik-logs.example.com |
| Termix | https://termix.example.com |
| Pocket ID | https://auth.example.com |
| Homarr | https://home.example.com |
| Dashdot | https://dash.example.com |
| LinkStack | https://example.com |
| CrowdSec Web UI | http://<cloudnode-ip>:3458 |
| Portainer | https://<cloudnode-ip>:9443 |


## Documentation

See [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for detailed architecture documentation.
