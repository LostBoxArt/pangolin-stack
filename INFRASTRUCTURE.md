# Pangolin Stack Infrastructure

This document provides detailed infrastructure documentation for AI agents and developers working with this stack.

## Network Architecture

```
                                    ┌─────────────────────────────────────┐
                                    │            INTERNET                  │
                                    └──────────────────┬──────────────────┘
                                                       │
                                                       ▼
                                    ┌─────────────────────────────────────┐
                                    │           CLOUDFLARE                 │
                                    │    DNS: *.dennisb.xyz → VPS IP       │
                                    │    Proxy: Orange cloud enabled       │
                                    └──────────────────┬──────────────────┘
                                                       │
                                                       ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                                   VPS (51.195.100.11)                                 │
│                                                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │   Traefik   │◄───│  Pangolin   │    │   Gerbil    │    │  CrowdSec   │            │
│  │  :80, :443  │    │   :3001     │    │  :51820/udp │    │   :8080     │            │
│  └──────┬──────┘    └─────────────┘    └──────┬──────┘    └─────────────┘            │
│         │                                      │                                      │
│         │ Routes requests                      │ WireGuard                            │
│         ▼                                      │ tunnel                               │
│  ┌─────────────┐    ┌─────────────┐            │                                      │
│  │  Homepage   │    │     Olm     │────────────┘                                      │
│  │   :3000     │    │ host network│                                                   │
│  └─────────────┘    └──────┬──────┘                                                   │
│                            │                                                          │
└────────────────────────────┼──────────────────────────────────────────────────────────┘
                             │
                             │ WireGuard tunnel via
                             │ Pangolin/Gerbil relay
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                              HOME NETWORK (192.168.0.0/24)                            │
│                                                                                       │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐            │
│  │    Newt     │    │   Traefik   │    │   Sonarr    │    │   Radarr    │            │
│  │  (tunnel)   │    │  :80, :443  │    │   :8989     │    │   :7878     │            │
│  └─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘            │
│                                                                                       │
│                     └─── nasus (192.168.0.10) ───┘                                   │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

## Service Dependencies

```mermaid
graph TD
    subgraph "Core Services"
        Traefik --> Pangolin
        Traefik --> CrowdSec
        Gerbil --> Pangolin
    end
    
    subgraph "Add-ons"
        Homepage --> Olm
        Homepage --> Docker[Docker Socket]
        TraefikDashboard --> TraefikAgent
    end
    
    subgraph "Remote"
        Olm --> Gerbil
        Gerbil --> Newt
        Newt --> HomeServices[Home Services]
    end
```

## Docker Compose Files

| File | Purpose | Services |
|------|---------|----------|
| `docker-compose.yml` | Core infrastructure | traefik, pangolin, gerbil, crowdsec, portainer |
| `docker-compose.addons.yml` | Dashboard & tools | homepage, olm, middleware-manager, traefik-dashboard, crowdsec-web-ui, dashdot, linkstack |
| `docker-compose.tools.yml` | Utilities | maxmind-updater |

## Olm Tunnel Configuration

Olm creates a WireGuard tunnel from the VPS to the home network, enabling Homepage to access internal services.

### How It Works

1. **Olm** connects to Pangolin/Gerbil endpoint
2. **WireGuard tunnel** established to home Newt instance
3. **Route** to `192.168.0.0/24` added via `olm` interface
4. **Homepage** uses `extra_hosts` to override DNS for service domains
5. **Requests** to `*.dennisb.xyz` resolve to `192.168.0.10` inside container
6. **Traffic** flows through Olm tunnel to home Traefik

### Configuration in docker-compose.addons.yml

```yaml
olm:
  image: ghcr.io/fosrl/olm:1.3.0
  network_mode: host
  cap_add:
    - NET_ADMIN
  devices:
    - /dev/net/tun:/dev/net/tun
  command:
    - "--id"
    - "<OLM_ID>"
    - "--secret"
    - "<OLM_SECRET>"
    - "--endpoint"
    - "https://pangolin.dennisb.xyz"
```

### DNS Overrides in Homepage

```yaml
homepage:
  extra_hosts:
    - "sonarr.dennisb.xyz:192.168.0.10"
    - "radarr.dennisb.xyz:192.168.0.10"
    - "request.dennisb.xyz:192.168.0.10"
```

## Homepage Configuration

### Files

| File | Purpose |
|------|---------|
| `config/homepage/services.yaml` | Service cards and widgets |
| `config/homepage/settings.yaml` | Layout, theme, columns |
| `config/homepage/docker.yaml` | Docker server connections |
| `config/homepage/widgets.yaml` | Top bar widgets |

### Docker Integration

- Local Docker: `/var/run/docker.sock` (mounted read-only)
- Container runs as root with docker group (986) for socket access
- Do NOT use PUID/PGID - breaks socket permissions

### Widget Access Pattern

```
Widget URL: https://sonarr.dennisb.xyz
    ↓ extra_hosts override
Resolved: 192.168.0.10:443
    ↓ Olm tunnel
Home Traefik (SNI routing)
    ↓
Sonarr container
```

## Troubleshooting Commands

### Olm Tunnel

```bash
# Check tunnel status
docker logs olm --tail 20

# Verify interface exists
ip addr show olm

# Test connectivity
ping 192.168.0.10

# Check routes
ip route | grep 192.168.0

# Restart tunnel
docker restart olm
```

### Homepage

```bash
# Check logs
docker logs homepage --tail 50

# Verify DNS override works inside container
docker exec homepage getent hosts sonarr.dennisb.xyz

# Check process permissions
docker exec homepage cat /proc/1/status | grep -E "Uid|Gid|Groups"
```

### CrowdSec

```bash
# Check decisions
docker exec crowdsec cscli decisions list

# Check bouncers
docker exec crowdsec cscli bouncers list

# View alerts
docker exec crowdsec cscli alerts list
```

## Environment Variables

Key variables in `.env`:

| Variable | Purpose |
|----------|---------|
| `TRAEFIK_DASHBOARD_TOKEN` | Auth token for traefik-dashboard |
| `CROWDSEC_AGENT_KEY` | CrowdSec agent registration key |

## Permissions Notes

| Path | Required Owner | Why |
|------|----------------|-----|
| `config/homepage/` | Container writable | Live config reload |
| `config/crowdsec-web-ui/` | Container writable | SQLite database |
| `/var/run/docker.sock` | root:docker (986) | Docker API access |

If permissions break, fix with:
```bash
sudo chmod 666 config/crowdsec-web-ui/crowdsec.db*
sudo chown -R jesus:jesus config/homepage/
```
