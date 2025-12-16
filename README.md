# Pangolin Stack

A self-hosted reverse proxy and tunneling solution with enterprise-grade security features.

## Overview

This stack provides:

- **Pangolin** - Dashboard and management interface for resources, users, and access control
- **Gerbil** - WireGuard-based tunneling for secure access to remote resources
- **Traefik** - Modern reverse proxy with automatic HTTPS via Let's Encrypt
- **CrowdSec** - Collaborative security engine with real-time threat detection

### Optional Add-ons

- **Middleware Manager** - Web UI for managing Traefik middlewares
- **Traefik Log Dashboard** - Real-time traffic analytics and GeoIP visualization

## Prerequisites

- Docker Engine 24.0+
- Docker Compose v2.20+
- A domain with DNS pointed to your server
- Ports 80, 443, and 51820/udp available

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/pangolin-stack.git
cd pangolin-stack
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit with your values
nano .env
```

### 3. Configure Pangolin

```bash
# Copy the example config
cp config/pangolin/config.yml.example config/pangolin/config.yml

# Edit with your domain and credentials
nano config/pangolin/config.yml
```

### 4. Configure Traefik Dynamic Rules

```bash
# Copy the example config
cp config/traefik/rules/dynamic_config.yml.example config/traefik/rules/dynamic_config.yml

# Edit with your domain
nano config/traefik/rules/dynamic_config.yml
```

### 5. Start Core Services

```bash
docker compose up -d
```

### 6. Get CrowdSec Bouncer Key

```bash
# Wait for CrowdSec to be healthy, then:
docker exec crowdsec cscli bouncers add traefik-bouncer

# Copy the key to your dynamic_config.yml (CrowdsecLapiKey field)
```

### 7. Restart Traefik

```bash
docker compose restart traefik
```

### 8. Access Pangolin

Open `https://pangolin.YOUR_DOMAIN` in your browser.

## Optional: Enable Add-ons

### Middleware Manager + Traefik Dashboard

```bash
# Download GeoIP databases first (requires MaxMind account)
docker compose -f docker-compose.yml -f docker-compose.tools.yml run --rm maxmind-updater

# Start with add-ons
docker compose -f docker-compose.yml -f docker-compose.addons.yml up -d
```

Access points:
- Middleware Manager: `http://YOUR_SERVER:3456` (or configure via Pangolin)
- Traefik Dashboard: `http://YOUR_SERVER:3457` (or configure via Pangolin)

## Directory Structure

```
pangolin-stack/
├── docker-compose.yml          # Core services
├── docker-compose.addons.yml   # Optional add-ons
├── docker-compose.tools.yml    # Utility tools
├── .env                        # Your secrets (gitignored)
├── .env.example                # Template for .env
│
├── config/
│   ├── pangolin/
│   │   └── config.yml          # Pangolin configuration
│   ├── traefik/
│   │   ├── traefik_config.yml  # Traefik static config
│   │   └── rules/
│   │       └── dynamic_config.yml  # Middlewares & routes
│   ├── crowdsec/               # CrowdSec configuration
│   ├── middleware-manager/     # Middleware Manager config
│   ├── maxmind/                # GeoIP databases
│   └── letsencrypt/            # SSL certificates
│
├── data/                       # Runtime data (gitignored)
└── logs/                       # Log files (gitignored)
```

## Services Reference

| Service | Port | Description |
|---------|------|-------------|
| Pangolin | 3001 (internal) | Management dashboard |
| Gerbil | 51820/udp, 80, 443 | WireGuard tunnel + web traffic |
| Traefik | (via Gerbil) | Reverse proxy |
| CrowdSec | 6060 | Security engine |
| Middleware Manager | 3456 | Middleware UI (addon) |
| Traefik Agent | 5000 | Log collector (addon) |
| Traefik Dashboard | 3457 | Analytics UI (addon) |

## Security Features

### CrowdSec Integration

CrowdSec provides:
- Real-time IP reputation checking
- Automatic blocking of malicious IPs
- Community-driven threat intelligence
- AppSec virtual patching

### Fail2ban Plugin

Built-in rate limiting:
- Ban time: 3 hours
- Find time: 10 minutes
- Max retries: 4

### Security Headers

All responses include:
- HSTS with 2-year max-age
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- Strict Referrer-Policy

## Configuration Reference

### Environment Variables

| Variable | Description |
|----------|-------------|
| `BASE_DOMAIN` | Your base domain |
| `PANGOLIN_SECRET` | Session encryption key |
| `PANGOLIN_ADMIN_EMAIL` | Initial admin email |
| `PANGOLIN_ADMIN_PASSWORD` | Initial admin password |
| `SMTP_*` | Email configuration |
| `CROWDSEC_LAPI_KEY` | CrowdSec bouncer API key |
| `TRAEFIK_DASHBOARD_TOKEN` | Dashboard auth token |
| `MAXMIND_*` | GeoIP database credentials |

### Generating Secrets

```bash
# Generate random secret
openssl rand -hex 32

# Generate CrowdSec bouncer key
docker exec crowdsec cscli bouncers add traefik-bouncer
```

## Backup & Restore

### Backup

```bash
# Stop services
docker compose down

# Backup configuration (excludes secrets if following .gitignore)
tar -czvf backup-$(date +%Y%m%d).tar.gz \
  config/pangolin/config.yml \
  config/traefik/ \
  config/letsencrypt/ \
  .env
```

### Restore

```bash
# Extract backup
tar -xzvf backup-YYYYMMDD.tar.gz

# Start services
docker compose up -d
```

## Updating

```bash
# Pull latest images
docker compose pull

# Restart services
docker compose up -d
```

## Troubleshooting

### Check Service Status

```bash
docker compose ps
docker compose logs -f SERVICE_NAME
```

### Common Issues

**CrowdSec middleware not working:**
- Ensure the LAPI key is correct in `dynamic_config.yml`
- Check CrowdSec is healthy: `docker exec crowdsec cscli capi status`

**SSL certificates not issued:**
- Ensure ports 80 and 443 are open
- Check DNS is pointing to your server
- View Traefik logs: `docker compose logs traefik`

**GeoIP not working:**
- Run the maxmind-updater tool
- Check MaxMind credentials are correct

## License

This stack configuration is provided as-is. Individual components have their own licenses:
- [Pangolin](https://github.com/fosrl/pangolin)
- [Traefik](https://github.com/traefik/traefik)
- [CrowdSec](https://github.com/crowdsecurity/crowdsec)
