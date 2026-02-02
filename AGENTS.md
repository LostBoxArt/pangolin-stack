# Pangolin Stack - Agent Briefing

This file is the one-stop overview for agents working in this repo. It captures architecture, services, critical files, operational flows, and troubleshooting without requiring you to read the other docs first.

## High-Level Architecture
- Traffic flow: Internet -> Cloudflare -> CloudNode (203.0.113.1) -> Traefik -> Services.
- Pangolin is the control plane and issues configuration to Gerbil.
- Gerbil is the WireGuard relay between the CloudNode and remote sites.
- Home network (192.168.1.0/24) is reachable via Olm on the CloudNode and Newt at home.
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
- Pangolin: https://pangolin.example.com
- CrowdSec: https://crowdsec.example.com
- Traefik Logs UI: https://traefik-logs.example.com
- Pocket ID: https://auth.example.com
- Homarr: https://home.example.com
- Dashdot: https://dash.example.com
- Termix: https://termix.example.com
- LinkStack: https://example.com
- CrowdSec Web UI: http://<cloudnode-ip>:3458
- Dockhand: https://dockhand.example.com
- AdGuard Home: https://dns.example.com

## Startup and Health
- Use `./startup.sh` to pull images and start all stacks in phased order.
- Use `./stackctl.sh` to manage individual stacks.
- Health waits for container status to be running and healthchecks to be healthy.

## Home Network Tunnel (Olm)
- Olm is a systemd service on the CloudNode (not a container).
- Commands:
  - `sudo systemctl status olm`
  - `sudo journalctl -u olm -f`
  - `sudo systemctl restart olm`
- Tunnel route used: 192.168.1.0/24.

## qBittorrent Widget Fix
Homarr v0.15+ has issues with qBittorrent v5.1.4+ HTTPS secure cookies.
- Use `qbit-proxy` for widgets:
  - Widget URL: `http://qbit-proxy:8081`
  - Target host: `torrent.example.com`
  - Target IP: `192.168.1.10`
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
- Uses `/opt/homelab/backups` and logs to `backups/backup.log`.
- Install daily timer: `sudo ./backup.sh install-timer` (runs at 03:00).
- Restore stops services, restores files, and re-imports volumes.

## Docker Volumes and External Data
- External volumes: `linkstack_linkstack_data`.
- Homarr data is in `/opt/homarr/appdata` on the host.
- Dockhand data is in `./data/dockhand`.
- Docker socket is mounted for Traefik, Homarr, and Dockhand.

## AdGuard Home (DNS)
- Web UI: https://dns.example.com
- DoH Endpoint: `https://dns.example.com/dns-query`
- DoT Endpoint: `dns.example.com:853`
- Manage blocklists and upstream DNS via the web UI.

## Known Operational Assumptions
- Cloudflare DNS points `*.example.com` to the CloudNode IP with proxy enabled.
- `auth.example.com` (Pocket ID) is routed via Traefik labels.
- `home.example.com` is routed to Homarr via Traefik labels.
- `torrent.example.com` resolves via `extra_hosts` in Homarr to 192.168.1.10.

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
- **Base URL**: `https://dockhand.example.com/api/`
- **Authentication**:
  - REST API: Requires a session cookie from the web UI.
  - Stacks: Headless updates via **Webhooks** (Settings -> Stacks -> Webhook).
- **Remote Hosts**:
  - **HomeNode** (Home): Connected via Hawser agent in TCP mode.
  - Host: `192.168.1.10`, Port: `2375`, Token: Secured in `.env` and Dockhand UI.

### Common API Endpoints
| Action | Method | Endpoint |
| :--- | :--- | :--- |
| List Containers | GET | `/api/containers` |
| View Logs | GET | `/api/containers/{id}/logs` |
| Restart Container | POST | `/api/containers/{id}/restart` |
| List Stacks | GET | `/api/stacks` |
| Trigger Webhook | GET/POST | `/api/git/stacks/{id}/webhook` |
| Activity Log | GET | `/api/activity` |

## When Editing Docs
- Keep `README.md` and `INFRASTRUCTURE.md` in sync with compose files.
- If services move between stacks, update this file too.
