# Pangolin Stack - Agent Briefing

This file is the one-stop overview for agents working in this repo. It captures architecture, services, critical files, operational flows, and troubleshooting without requiring you to read the other docs first.

## High-Level Architecture
- Traffic flow: Internet -> Cloudflare -> VPS (51.195.100.11) -> Traefik -> Services.
- Pangolin is the control plane and issues configuration to Gerbil.
- Gerbil is the WireGuard relay between the VPS and remote sites.
- Home network (192.168.0.0/24) is reachable via Olm on the VPS and Newt at home.
- Traefik runs with `network_mode: service:gerbil`, so 80/443 are bound by Gerbil and shared.

## Stack Organization

Services are organized into 7 stacks under `stacks/`:

| Stack | Services | Purpose |
|-------|----------|---------|
| **core** | pangolin, gerbil, traefik | Infrastructure (starts first, creates `pangolin` network) |
| **security** | crowdsec, crowdsec-web-ui, pocket-id | Protection & auth |
| **dns** | adguard-home | DNS-over-HTTPS & filtering |
| **observability** | traefik-agent, traefik-dashboard, dashdot | Monitoring & logs |
| **management** | dockhand | Container management |
| **dashboard** | homarr, qbit-proxy | User dashboards |
| **apps** | linkstack, termix | User applications |

### Startup Order
1. **core** (creates network, must start first)
2. **security**, **management**, **dns** (can start in parallel)
3. **observability**, **dashboard**, **apps** (can start in parallel)

All stacks except core use `networks.pangolin: external: true`.

## Service Inventory (Ports and Roles)
Core:
- Pangolin: control plane, 3001 (internal).
- Gerbil: WireGuard relay, 51820/udp and 21820/udp; also binds 80/443 for Traefik.
- Traefik: reverse proxy, uses Gerbil network namespace, routes HTTPS via Let's Encrypt.

Security:
- CrowdSec: 6060/8080, LAPI and bouncers; ingests Traefik logs.
- CrowdSec Web UI: admin UI for CrowdSec, 3458 (mapped to 3000 in container).
- Pocket ID: auth provider, 1411 (behind Traefik).

DNS:
- AdGuard Home: DNS-over-HTTPS/DoT, 3000/53/853 (behind Traefik for UI).

Observability:
- Traefik Agent: log dashboard agent, 5000.
- Traefik Dashboard: UI for Traefik logs, 3457.
- Dashdot: system dashboard, 3001 (behind Traefik).

Management:
- Dockhand: container management & auto-update, 3000 (behind Traefik).

Dashboard:
- Homarr: dashboard, 7575 (behind Traefik).
- qbit-proxy: local proxy for qBittorrent widget, 8081 (internal).

Apps:
- LinkStack: landing page, 80 (behind Traefik).
- Termix: web SSH, 8080 (behind Traefik).

## Public Endpoints
- Pangolin: https://pangolin.dennisb.xyz
- CrowdSec: https://crowdsec.dennisb.xyz
- Traefik Logs UI: https://traefik-logs.dennisb.xyz
- Pocket ID: https://auth.dennisb.xyz
- Homarr: https://home.dennisb.xyz
- Dashdot: https://dash.dennisb.xyz
- Termix: https://termix.dennisb.xyz
- LinkStack: https://dennisb.xyz
- CrowdSec Web UI: http://<vps-ip>:3458
- Dockhand: https://dockhand.dennisb.xyz
- AdGuard Home: https://dns.dennisb.xyz

## Startup and Health
- Use `./startup.sh` to pull images and start all stacks in phased order.
- Use `./stackctl.sh` to manage individual stacks.
- Health waits for container status to be running and healthchecks to be healthy.

## Version and Upgrade Policy
- Core pins: Pangolin `1.17.1`, Gerbil `1.3.1`, Traefik Badger plugin `v1.4.0`.
- Security pin: CrowdSec Web UI `ghcr.io/theduffman85/crowdsec-web-ui:2026.3.1` because the moving `latest` tag pulled a broken image on 2026-03-30.
- NASUS Newt is pinned to `1.11.0`.
- VPS Olm runs as systemd binary `1.4.4` with `--override-dns=false`.
- Newt `1.11.x` aligns with Pangolin `1.17.x` for private resource connection logging and provisioning-key site creation.
- Before upgrades, read:
  - `https://docs.pangolin.net/self-host/how-to-update`
  - `https://github.com/fosrl/pangolin/releases`
  - `https://github.com/fosrl/gerbil/releases`
  - `https://github.com/fosrl/newt/releases`
  - `https://github.com/fosrl/olm/releases`
  - `https://github.com/fosrl/badger/releases`

## Home Network Tunnel (Olm)
- Olm is a systemd service on the VPS (not a container).
- Pin `pangolin.dennisb.xyz` to `51.195.100.11` in `/etc/hosts` on the VPS. This avoids resolver drift inside Olm and keeps the UDP hole-punch path stable.
- Commands:
  - `sudo systemctl status olm`
  - `sudo journalctl -u olm -f`
  - `sudo systemctl restart olm`
  - `sudo systemctl status olm-watchdog.timer`
- Tunnel route used: 192.168.0.0/24.

### Tunnel Watchdogs
- VPS: `/usr/local/sbin/olm-watchdog.sh` + `olm-watchdog.timer` (systemd, every minute).
- NASUS: `/usr/local/bin/newt-watchdog.sh` (root crontab every minute).
- If Dockhand on the VPS cannot reach NASUS at `192.168.0.10:2375`, first check for `192.168.0.0/24 dev olm`. If it is missing, inspect `journalctl -u olm` and restart `olm`.
- NASUS Docker healthchecks currently exist for `sonarr`, `radarr`, `prowlarr`, `bazarr`, `qbittorrent`, `flaresolverr`, `plex`, `traefik`, `qui`, `seerr`, and `hawser`.
- Those compose files are live on NASUS under `/volume1/docker/config/*/docker-compose.yml` plus `/volume1/docker/traefik/docker-compose.yml`.
- Source-controlled backup copies live in this repo under `host-configs/nasus/`.

## qBittorrent Widget Fix
Homarr v0.15+ has issues with qBittorrent v5.1.4+ HTTPS secure cookies.
- Use `qbit-proxy` for widgets:
  - Widget URL: `http://qbit-proxy:8081`
  - Target host: `torrent.dennisb.xyz`
  - Target IP: `192.168.0.10`
- The proxy strips the Secure cookie flag and sets the correct Host header.

## File Layout
```
pangolin-stack/
├── stacks/
│   ├── core/docker-compose.yml         # pangolin, gerbil, traefik
│   ├── security/docker-compose.yml     # crowdsec, crowdsec-web-ui, pocket-id
│   ├── observability/docker-compose.yml # traefik-agent, traefik-dashboard, dashdot
│   ├── management/docker-compose.yml   # dockhand
│   ├── dashboard/docker-compose.yml    # homarr, qbit-proxy
│   └── apps/docker-compose.yml         # linkstack, termix
├── config/                             # service configs (pangolin, crowdsec, traefik)
├── config/db/                          # Pangolin database
├── config/traefik/rules/               # Traefik dynamic rules
├── config/letsencrypt/                 # ACME certs (acme.json)
├── qbit-proxy/                         # proxy build context (Dockerfile, index.js)
├── data/                               # runtime data (Pocket ID, Dockhand)
├── logs/                               # stack logs
├── .env                                # shared environment variables
├── startup.sh                          # start all stacks in order
├── stackctl.sh                         # stack management utility
├── backup.sh                           # backup/restore script
├── README.md                           # quick start
├── INFRASTRUCTURE.md                   # detailed architecture
└── AGENTS.md                           # this file
```

## Key Environment Variables
From `.env` (all are referenced in compose):
- TRAEFIK_DASHBOARD_TOKEN
- CROWDSEC_AGENT_KEY
- CROWDSEC_WEB_UI_PASSWORD
- HOMARR_SECRET_KEY
- TELEGRAM_BOT_TOKEN
- TELEGRAM_CHAT_ID
- POCKET_ID_APP_URL
- POCKET_ID_ENCRYPTION_KEY
- POCKET_ID_TRUST_PROXY
- MAXMIND_ACCOUNT_ID
- MAXMIND_LICENSE_KEY
- DISABLE_ONLINE_API
- DISABLE_HUB_UPDATE

## Traefik Notes
- Traefik config lives in `config/traefik/traefik_config.yml`.
- Dynamic rules live in `config/traefik/rules/`.
- Access and error logs live in `config/traefik/logs/`.
- Traefik uses Docker socket for service discovery.
- Traefik shares Gerbil's network namespace via `network_mode: service:gerbil`.
- If `gerbil` is recreated or replaced, `traefik` must also be recreated afterward or public `80/443` can fail because Traefik remains attached to the old container namespace.
- Recovery command: `docker compose -f stacks/core/docker-compose.yml --env-file .env up -d --force-recreate traefik`

## CrowdSec Notes
- Configs under `config/crowdsec/`.
- Data DB under `config/crowdsec/db/`.
- Blocklist import: `./scripts/blocklist-import.sh` (or add to cron for daily updates)
- Common commands:
  - `docker exec crowdsec cscli decisions list`
  - `docker exec crowdsec cscli decisions list | grep external_blocklist | wc -l`
  - `docker exec crowdsec cscli bouncers list`
  - `docker exec crowdsec cscli alerts list`

## Backup and Restore
`./backup.sh` handles full backup/restore and daily timers.
- Backup includes compose files, `.env`, configs, db, certs, volumes, docs.
- Uses `/home/jesus/pangolin-stack/backups` and logs to `backups/backup.log`.
- Install daily timer: `sudo ./backup.sh install-timer` (runs at 03:00).
- Restore stops services, restores files, and re-imports volumes.

## Docker Volumes and External Data
- External volumes: `linkstack_linkstack_data`.
- Homarr data is in `/opt/homarr/appdata` on the host.
- Dockhand data is in `./data/dockhand`.
- Docker socket is mounted for Traefik, Homarr, and Dockhand.

## AdGuard Home (DNS)
- Web UI: https://dns.dennisb.xyz
- DoH Endpoint: `https://dns.dennisb.xyz/dns-query`
- DoT Endpoint: `dns.dennisb.xyz:853`
- Manage blocklists and upstream DNS via the web UI.

## Known Operational Assumptions
- Cloudflare DNS points `*.dennisb.xyz` to the VPS IP with proxy enabled.
- `auth.dennisb.xyz` (Pocket ID) is routed via Traefik labels.
- `home.dennisb.xyz` is routed to Homarr via Traefik labels.
- `torrent.dennisb.xyz` resolves via `extra_hosts` in Homarr to 192.168.0.10.

## Common Commands

```bash
# Start all stacks
./startup.sh

# View all stack status
./stackctl.sh status

# Manage individual stacks
./stackctl.sh start <stack>
./stackctl.sh stop <stack>
./stackctl.sh restart <stack>
./stackctl.sh logs <stack>

# Pull latest images
./stackctl.sh pull

# Stop everything
./stackctl.sh down
```

## Dockhand Management & API
Dockhand replaced Portainer for container management.
- **Base URL**: `https://dockhand.dennisb.xyz/api/`
- **Authentication**:
  - REST API: Requires a session cookie from the web UI.
  - Stacks: Headless updates via **Webhooks** (Settings -> Stacks -> Webhook).
- **Verified internal API flow**:
  - Use SSH to the VPS and call Dockhand on its container IP, not through the public URL.
  - Discover the current internal URL with `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' dockhand`, then use `http://<dockhand-ip>:3000`.
  - Local login works with `POST /api/auth/login` and JSON `{"username":"...","password":"..."}`.
  - Successful login sets the `dockhand_session` cookie.
  - Reuse that cookie in a `Cookie: dockhand_session=<token>` header for later API calls.
- **Remote Hosts**:
  - **NASUS** (Home): Connected via Hawser agent in TCP mode.
  - Host: `192.168.0.10`, Port: `2375`, Token: Secured in `.env` and Dockhand UI.

### Verified CLI Login Flow
```bash
# Run on the VPS over SSH. Public HTTPS goes through Pangolin auth and is not ideal for automation.
DOCKHAND_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' dockhand | awk '{print $1}')

curl -skD /tmp/dockhand.headers \
  -c /tmp/dockhand.cookie \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{"username":"jesus","password":"<dockhand-local-password>"}' \
  "http://${DOCKHAND_IP}:3000/api/auth/login"

TOKEN=$(awk '/dockhand_session/ {print $7}' /tmp/dockhand.cookie)
curl -sk -H "Cookie: dockhand_session=${TOKEN}" \
  "http://${DOCKHAND_IP}:3000/api/stacks?env=2"
```

### Environment IDs
- `env=1`: VPS
- `env=2`: NASUS

### Common API Endpoints
| Action | Method | Endpoint |
| :--- | :--- | :--- |
| List Containers | GET | `/api/containers` |
| View Logs | GET | `/api/containers/{id}/logs` |
| Restart Container | POST | `/api/containers/{id}/restart` |
| List Stacks | GET | `/api/stacks` |
| List Git Stacks | GET | `/api/git/stacks` |
| Deploy Git Stack | POST | `/api/git/stacks/{id}/deploy` |
| Trigger Webhook | GET/POST | `/api/git/stacks/{id}/webhook` |
| Activity Log | GET | `/api/activity` |

## When Editing Docs
- Keep `README.md` and `INFRASTRUCTURE.md` in sync with compose files.
- If services move between stacks, update this file too.
