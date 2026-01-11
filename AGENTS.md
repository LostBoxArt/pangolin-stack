# Pangolin Stack - Agent Briefing

This file is the one-stop overview for agents working in this repo. It captures architecture, services, critical files, operational flows, and troubleshooting without requiring you to read the other docs first.

## High-Level Architecture
- Traffic flow: Internet -> Cloudflare -> CloudNode (203.0.113.1) -> Traefik -> Services.
- Pangolin is the control plane and issues configuration to Gerbil.
- Gerbil is the WireGuard relay between the CloudNode and remote sites.
- Home network (192.168.1.0/24) is reachable via Olm on the CloudNode and Newt at home.
- Traefik runs with `network_mode: service:gerbil`, so 80/443 are bound by Gerbil and shared.

## Core vs Add-ons
Core services are in `docker-compose.yml`:
- traefik, pangolin, gerbil, crowdsec, traefik-agent
- traefik-dashboard, crowdsec-web-ui, pocket-id, portainer

Add-ons are in `docker-compose.addons.yml`:
- homarr, dashdot, linkstack, termix, qbit-proxy
- olm is commented out in compose; it runs as systemd on the CloudNode.

## Service Inventory (Ports and Roles)
Core:
- Pangolin: control plane, 3001 (internal).
- Gerbil: WireGuard relay, 51820/udp and 21820/udp; also binds 80/443 for Traefik.
- Traefik: reverse proxy, uses Gerbil network namespace, routes HTTPS via Let's Encrypt.
- CrowdSec: 6060/8080, LAPI and bouncers; ingests Traefik logs.
- Traefik Agent: log dashboard agent, 5000.
- Traefik Dashboard: UI for Traefik logs, 3457.
- CrowdSec Web UI: admin UI for CrowdSec, 3458 (mapped to 3000 in container).
- Pocket ID: auth provider, 1411 (behind Traefik).
- Portainer: Docker management, 9000/9443 (and 8000).

Add-ons:
- Homarr: dashboard, 7575 (behind Traefik).
- Dashdot: system dashboard, 3001 (behind Traefik).
- LinkStack: landing page, 80 (behind Traefik).
- Termix: web SSH, 8080 (behind Traefik).
- qbit-proxy: local proxy for qBittorrent widget, 8081 (internal).

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
- Portainer: https://<cloudnode-ip>:9443

## Startup and Health
- Use `./startup.sh` to pull images, start all services, and wait for health.
- The script assumes everything is off and brings the entire stack up.
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
- `README.md`: quick start and overview.
- `INFRASTRUCTURE.md`: detailed architecture and troubleshooting.
- `docker-compose.yml`: core services + select add-ons.
- `docker-compose.addons.yml`: optional dashboards/tools.
- `startup.sh`: start everything and wait for health.
- `backup.sh`: backup/restore and systemd timer automation.
- `config/`: service configs and secrets (pangolin, crowdsec, traefik).
- `config/db/`: Pangolin database.
- `config/traefik/rules/`: Traefik dynamic rules.
- `config/letsencrypt/`: ACME certs (`acme.json`).
- `qbit-proxy/`: proxy build context (`Dockerfile`, `index.js`).
- `data/`: runtime data, used by Pocket ID and other services.
- `logs/`: stack logs (Traefik logs live under `config/traefik/logs/`).

## Key Environment Variables
From `.env` (all are referenced in compose):
- TRAEFIK_DASHBOARD_TOKEN
- CROWDSEC_AGENT_KEY
- CROWDSEC_WEB_UI_PASSWORD
- HOMARR_SECRET_KEY
- PORTAINER_LICENSE_KEY
- POCKET_ID_APP_URL
- POCKET_ID_ENCRYPTION_KEY
- POCKET_ID_TRUST_PROXY
- MAXMIND_ACCOUNT_ID
- MAXMIND_LICENSE_KEY
- DISABLE_ONLINE_API
- DISABLE_HUB_UPDATE

## Traefik Notes
- Traefik config lives in `config/traefik/traefik_config.yml` (example in `config/traefik/traefik_config.yml.example`).
- Dynamic rules live in `config/traefik/rules/`.
- Access and error logs live in `config/traefik/logs/`.
- Traefik uses Docker socket for service discovery.

## CrowdSec Notes
- Configs under `config/crowdsec/`.
- Data DB under `config/crowdsec/db/`.
- Common commands:
  - `docker exec crowdsec cscli decisions list`
  - `docker exec crowdsec cscli bouncers list`
  - `docker exec crowdsec cscli alerts list`

## Backup and Restore
`./backup.sh` handles full backup/restore and daily timers.
- Backup includes compose files, `.env`, configs, db, certs, volumes, docs.
- Uses `/opt/homelab/backups` and logs to `backups/backup.log`.
- Install daily timer: `sudo ./backup.sh install-timer` (runs at 03:00).
- Restore stops services, restores files, and re-imports volumes.

## Docker Volumes and External Data
- External volumes: `portainer_data`, `linkstack_linkstack_data`.
- Homarr data is in `/opt/homarr/appdata` on the host.
- Docker socket is mounted for Traefik and Homarr.

## Known Operational Assumptions
- Cloudflare DNS points `*.example.com` to the CloudNode IP with proxy enabled.
- `auth.example.com` (Pocket ID) is routed via Traefik labels.
- `home.example.com` is routed to Homarr via Traefik labels.
- `torrent.example.com` resolves via `extra_hosts` in Homarr to 192.168.1.10.

## Common Commands
```bash
docker compose -f docker-compose.yml -f docker-compose.addons.yml ps
docker compose -f docker-compose.yml -f docker-compose.addons.yml logs -f
docker compose -f docker-compose.yml -f docker-compose.addons.yml pull
docker compose -f docker-compose.yml -f docker-compose.addons.yml up -d
```

## When Editing Docs
- Keep `README.md` and `INFRASTRUCTURE.md` in sync with compose files.
- If services move between core/add-ons, update this file too.
