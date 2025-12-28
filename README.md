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
│   ├── crowdsec-web-ui/        # CrowdSec Web UI data (gitignored)
│   ├── middleware-manager/     # Middleware Manager config
│   ├── maxmind/                # GeoIP databases
│   └── letsencrypt/            # SSL certificates
│
├── data/                       # Runtime data (gitignored)
└── logs/                       # Log files (gitignored)
```

## Maintenance

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

### Updating

```bash
# Pull latest images
docker compose pull

# Restart services
docker compose up -d
```
