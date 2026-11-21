# Pangolin Stack - Agent Briefing

This file is the one-stop overview for agents working in this repo. It captures architecture, services, critical files, operational flows, and troubleshooting without requiring you to read the other docs first.

## High-Level Architecture
- Traffic flow: Internet -> Cloudflare -> CloudNode (203.0.113.1) -> Pangolin -> Olm tunnel -> Newt on rammus -> Traefik on rammus -> services.
- Pangolin is the control plane and issues configuration to Gerbil.
- Gerbil is the WireGuard relay between the CloudNode and remote sites.
- LAN `192.168.0.0/24` is reachable via Olm on the CloudNode and Newt on **rammus** (`192.168.0.12`).
- CloudNode Traefik runs with `network_mode: service:gerbil`, so 80/443 are bound by Gerbil and shared. A **separate** Traefik on rammus owns 80/443 on the LAN.
- **Host split since 2026-11-21:** rammus runs every application. NASUS
  (`192.168.0.10`) is pure NFS storage and runs **zero containers**.

## Stack Organization

The current CloudNode deployment uses six stacks under `stacks/`. Older
template/archived definitions remain in this checkout; use the dated live
inventory before deployment.

| Stack | Services | Purpose |
|-------|----------|---------|
| **core** | pangolin, gerbil, traefik | Infrastructure (starts first, creates `pangolin` network) |
| **security** | crowdsec, crowdsec-web-ui, pocket-id | Protection & auth |
| **observability** | traefik-agent, traefik-dashboard, dashdot | Monitoring & logs |
| **management** | dockhand | Container management |
| **dashboard** | homarr, qbit-proxy | User dashboards |
| **apps** | landing | Static landing page (Termix was removed on 2026-10-16) |
| **homenode** | newt, hawser, traefik, arr-mcp, prowlarr, scryer, plex, qbittorrent, dashdot | Home tunnel, management, media and monitoring — **all now on rammus (`192.168.0.12`)** |

The `homenode` stack is the historical name; its services run on rammus under
`/opt/docker/stacks/<service>/`. `sonarr`, `radarr`, `bazarr`, `profilarr`,
`recyclarr`, `seerr`, `flaresolverr`, `qui`, and `cleanuparr` were already
stopped before the migration and are not running.

CloudNode also runs Hermes-managed SearXNG/Valkey outside these stacks.
AdGuard Home, qui, cleanuparr, and FileFlows are absent from the verified live
container inventory. AdGuard Home **does** run as a plugin on the OPNsense router
and serves all LAN DNS. Preserve historical docs without treating them as active
services. See `docs/wiki/maintenance-2026-10-27.md` and
`docs/wiki/hosts/rammus.md`.

### Startup Order
1. **core** (creates network, must start first)
2. **security**, **management** (can start in parallel)
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

Historical DNS:
- CloudNode AdGuard Home is retired. The separate router-hosted NAS backend
  remains active; do not remove its NAS Traefik route as stale.

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
- Landing: nginx static page behind Traefik.
- Termix was removed from the apps stack on 2026-10-16; no live container exists.

## Public Endpoints
- Pangolin: https://pangolin.example.com
- CrowdSec: https://crowdsec.example.com
- Traefik Logs UI: https://traefik-logs.example.com
- Pocket ID: https://auth.example.com
- Homarr: https://home.example.com
- Dashdot: https://dash.example.com
- Landing: https://example.com
- CrowdSec Web UI: use the protected CrowdSec endpoint; host port 3458 is loopback-only.
- Dockhand: https://dockhand.example.com

## Startup and Health
- Use `./startup.sh` to pull images and start all stacks in phased order.
- Use `./stackctl.sh` to manage individual stacks.
- Health waits for container status to be running and healthchecks to be healthy.
- **rammus NFS gate:** `plex` and `qbittorrent` run with `restart: "no"` and are
  started by `nasus-media-apps.timer` → `nasus-media-apps.service`, which refuses
  to start them unless `/mnt/nasus/media` is a real mountpoint. This exists so a
  slow NASUS at boot cannot bring them up against an empty local directory. Run
  `sudo systemctl stop nasus-media-apps.timer` before deliberately stopping
  either container, and re-enable it after. Do not "fix" this by restoring
  `restart: unless-stopped`; that reintroduces the empty-directory failure.

## Version and Upgrade Policy
- Verified live on 2026-11-21: Pangolin `1.26.0`, Gerbil `1.6.0`, CloudNode
  Traefik `v3.7.19`. Treat version numbers here as a snapshot, not a pin.
- Source pins after the 2026-11-06 sweep (`stacks/*/docker-compose.yml`): Pangolin
  `1.26.0`, Gerbil `1.6.0`, Traefik `v3.7.19`, Badger plugin `v1.8.0`, Homarr
  `v2.13.1`, Pocket-ID `v2.19.2`, CrowdSec Web UI `2026.11.11`. Traefik, Homarr
  and CrowdSec Web UI were corrected to the running images on 2026-11-21
  (`docker inspect`), so the reference pins now match the deployed set.
- CrowdSec Web UI persistent state uses `/app/data` (`state.db`) and the host service UID.
- Newt runs on **rammus**; its current snapshot pins `1.19.0`.
- rammus runs Traefik `3.7.17` (pinned) and Plex/qBittorrent/dashdot on `:latest`.
- CloudNode Olm was upgraded `1.9.1` -> `1.10.1` on 2026-11-06, with
  `--override-dns=false`; the previous binary is kept as `/usr/local/bin/olm.1.9.1.rollback`.
- Recheck upstream compatibility notes (Pangolin/Traefik, Badger plugin integrity) before changing any pin.
- Before upgrades, read:
  - `https://docs.pangolin.net/self-host/how-to-update`
  - `https://github.com/fosrl/pangolin/releases`
  - `https://github.com/fosrl/gerbil/releases`
  - `https://github.com/fosrl/newt/releases`
  - `https://github.com/fosrl/olm/releases`
  - `https://github.com/fosrl/badger/releases`

## Home Network Tunnel (Olm)
- Olm is a systemd service on the CloudNode (not a container).
- Its unit uses `CONFIG_FILE=/root/.config/olm-client/config.json` and `UMask=0077`.
  Keep that config root-owned `0600`, its directory `0700`, and credentials out
  of `ExecStart`. The sanitized unit is in `host-configs/cloudnode/systemd/`.
- Pin `pangolin.example.com` to `203.0.113.1` in `/etc/hosts` on the CloudNode. This avoids resolver drift inside Olm and keeps the UDP hole-punch path stable.
- Commands:
  - `/usr/local/sbin/hermes-safe-service status olm`
  - `/usr/local/sbin/hermes-safe-logs olm --since 30m`
  - `/usr/local/sbin/hermes-safe-service restart olm`
  - `/usr/local/sbin/hermes-safe-service status olm-watchdog.timer`
- Tunnel route used: 192.168.0.0/24.

### Tunnel Watchdogs
- CloudNode: `/usr/local/sbin/olm-watchdog.sh` + `olm-watchdog.timer` (systemd, every minute).
- rammus: `/usr/local/bin/newt-watchdog.sh` + `/etc/cron.d/newt-watchdog` (every minute). It starts `newt` if it is down and restarts it on tunnel-interface failure.
- **Do not recreate the old NASUS copy.** A leftover `newt-watchdog` cron on NASUS kept resurrecting a second `newt` with the same site credentials, which flapped the tunnel and caused intermittent 502s. It was removed on 2026-11-21.
- If Dockhand on the CloudNode cannot reach rammus at `192.168.0.12:2375`, first check for `192.168.0.0/24 dev olm`. If it is missing, inspect `/usr/local/sbin/hermes-safe-logs olm --since 30m` and restart `olm` with `/usr/local/sbin/hermes-safe-service restart olm`.
- Rammus has no native `newt` healthcheck; the watchdog is the availability check.
- rammus compose files live under `/opt/docker/stacks/<service>/docker-compose.yml`
  with appdata at `/opt/docker/config/<service>`. NASUS has no live compose files
  now; its old `/volume1/docker/config/*` trees are rollback and history only.
- Source-controlled backup copies live in this repo under `host-configs/homenode/`
  and are stale relative to rammus.
- FileFlows and `fileflows-dv-watcher` were decommissioned on 2026-10-27. Do not recreate their containers, routes, watcher jobs or service registrations from historical backups.

## qBittorrent Widget Fix
Homarr v0.15+ has issues with qBittorrent v5.1.4+ HTTPS secure cookies.
- Use `qbit-proxy` for widgets:
  - Widget URL: `http://qbit-proxy:8081`
  - Target host: `torrent.example.com`
  - Target IP: `192.168.0.12`
- The proxy strips the Secure cookie flag and sets the correct Host header.
- The proxy uses Node 24 with upstream certificate verification and a 10-second request deadline.
- Its Docker healthcheck requires HTTP 200 and a qBittorrent version body through the proxy; tunnel or upstream failures can make it unhealthy.
- **`AuthSubnetWhitelist` must contain rammus's Docker subnet `172.19.0.0/16`.** The old config only listed `172.18.0.0/16` (NASUS), so peer containers got `403 Forbidden` and scryer's download client silently failed. Verify with `curl -s -o /dev/null -w '%{http_code}' http://172.19.0.3:8080/api/v2/app/version`.
- **scryer and `qbit-proxy` do not authenticate to qBittorrent at all.** No `/auth/login`, no `SID` cookie, no `Authorization` header — they work *only* because `AuthSubnetWhitelistEnabled=true`. Turning the whitelist off returns `403` on every call from both, and breaks them. Do not "harden" that setting without first giving scryer real credentials and testing a whitelist narrowing separately.
- **A fixed cause does not immediately clear the symptom.** On a `403` scryer escalates a back-off (`download_client_status.escalation_level`, `disabled_until`) and then skips the client entirely, logging `no download client answered` for roughly 15–25 more minutes. Wait out the timer before concluding a fix failed, or read the table:
  `sudo sqlite3 /opt/docker/config/scryer/scryer.db "SELECT escalation_level, disabled_until FROM download_client_status;"`
- **Container addresses on `traefik_traefik` are not stable, and misreading them causes wrong conclusions.** At 2026-11-21: `traefik .2`, `qbittorrent .3`, `prowlarr .4`, `arr-mcp .5`, `scryer .6`. A capture on `.2 → .3:8080` is Traefik relaying a browser, not scryer. Always confirm with
  `docker network inspect traefik_traefik --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}'`.
- **Known security debt:** the whitelist currently bypasses qBittorrent auth for `192.168.0.0/24`, `172.17.0.0/16`, `172.18.0.0/16`, `172.19.0.0/16`, `10.0.0.0/8`, and `100.90.0.0/16`. `172.18.0.0/16` no longer exists on rammus and can be removed. The safe end state is real credentials in scryer plus a `/32` whitelist pinned with a static container IP.

## File Layout
```
pangolin-stack/
├── stacks/
│   ├── core/docker-compose.yml         # pangolin, gerbil, traefik
│   ├── security/docker-compose.yml     # crowdsec, crowdsec-web-ui, pocket-id
│   ├── observability/docker-compose.yml # traefik-agent, traefik-dashboard, dashdot
│   ├── management/docker-compose.yml   # dockhand
│   ├── dashboard/docker-compose.yml    # homarr, qbit-proxy
│   ├── apps/docker-compose.yml         # landing
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
├── docs/wiki/hosts/rammus.md           # compute host that runs every app
├── docs/wiki/hosts/homenode.md         # NASUS, storage only
├── docs/wiki/hosts/cloudnode.md        # public edge and control plane
├── README.md                           # quick start
├── INFRASTRUCTURE.md                   # detailed architecture
└── AGENTS.md                           # this file
```

Live application compose files are **not** in this repo. They run on rammus under
`/opt/docker/stacks/<service>/docker-compose.yml`, with appdata at
`/opt/docker/config/<service>`. The `host-configs/homenode/` tree is a stale
snapshot and must not be deployed over the live host.

**The CloudNode clone `/home/jesus/pangolin-stack` is the deployment source and
is deliberately dirty.** It carries the real `dennisb.xyz` hostnames where this
repo uses `example.com`, and it is often ahead on image pins. Never
`git reset --hard` or `git checkout .` there: that would replace live hostnames
with placeholders and roll back pins on a running host. On 2026-11-21 the working
tree was ahead of `main` by three pins (`traefik:v3.7.19`,
`homarr:v2.13.1`, `crowdsec-web-ui:2026.11.11`); those were copied into the repo
rather than the clone being reset.

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
- Uses `/opt/homelab/backups` and logs to `backups/backup.log`.
- The existing live daily timer runs at 03:00. Inspect it with `systemctl status
  pangolin-backup.timer`; do not replace it with the older template installer
  without adapting its account and installation paths.
- Restore stops services, restores files, and re-imports volumes.
- New archives use private permissions and include landing sites, the proxy build context and the full CrowdSec configuration tree.
- Pangolin, CrowdSec, CrowdSec Web UI, Pocket ID, Dockhand and Homarr use validated
  online SQLite snapshots. Runtime metadata and allowlisted host recovery files
  are private recovery content, not Git source. Each database is consistent
  independently; this is not one atomic transaction across applications.

## Docker Volumes and External Data
- Active stacks have no declared named volumes (landing uses a bind-mounted
  `sites/` directory).
- Homarr data is in `/opt/homarr/appdata` on the host.
- Dockhand data is in `./data/dockhand`.
- Docker socket is mounted for Traefik and Dockhand.

## AdGuard Home (DNS)
- Web UI: https://dns.example.com
- DoH Endpoint: `https://dns.example.com/dns-query`
- DoT Endpoint: `dns.example.com:853`
- AdGuard Home runs as a plugin on the **OPNsense router** (`os-adguardhome-maxit`)
  and listens on `:53`. Unbound is on `:53530` and dnsmasq on `:53053`; neither
  serves LAN clients.
- Every service name is an explicit rewrite pointing at `192.168.0.12`. There is
  no wildcard, so a new service needs both a Traefik route and an AdGuard rewrite.
- Editing `/usr/local/AdGuardHome/AdGuardHome.yaml` by hand is risky: a malformed
  edit took DNS down for about three minutes. Back up first and edit whole blocks
  (`perl -0777`), never with `awk` range deletes.

## Known Operational Assumptions
- Cloudflare DNS points `*.example.com` to the CloudNode IP with proxy enabled.
- `auth.example.com` (Pocket ID) is routed via Traefik labels.
- `home.example.com` is routed to Homarr via Traefik labels.
- **Two independent `.10` pins existed on the CloudNode and both had to be
  updated for the 2026-11-21 move:** `/etc/hosts` (4 names: `nasus`, `prowlarr`,
  `torrent`, `adguard`) and the six `extra_hosts` entries in
  `stacks/dashboard/docker-compose.yml` (those four plus `request` and `plex`).
  The second list lands in the Homarr container's own `/etc/hosts`, so it
  overrides DNS *and* the host file.
  If a Homarr tile is red while the service answers directly, check the
  container: `docker exec homarr getent hosts <name>`. It should return
  `192.168.0.12`.
- **`dash.example.com` now resolves to rammus from both directions.** The
  Pangolin `dash` target was retargeted on 2026-11-21 from the CloudNode's
  `dashdot:3001` to site `homelab`, `192.168.0.12:3003`, matching the AdGuard
  rewrite. The CloudNode's own dashdot still runs but binds `127.0.0.1:3001`
  only and now has no consumer; it is no longer monitored.

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
- **Verified internal API flow**:
  - Use SSH to the CloudNode and call Dockhand on its container IP, not through the public URL.
  - Discover the current internal URL with `docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' dockhand`, then use `http://<dockhand-ip>:3000`.
  - Local login works with `POST /api/auth/login` and JSON `{"username":"...","password":"..."}`.
  - Successful login sets the `dockhand_session` cookie.
  - Reuse that cookie in a `Cookie: dockhand_session=<token>` header for later API calls.
- **Remote Hosts**:
  - **Rammus** (Home): Connected via Hawser agent in TCP mode.
  - Host: `192.168.0.12`, Port: `2375`, Token: Secured in `.env` and Dockhand UI.
  - Hawser binds `192.168.0.12:2375` only, and unauthenticated requests return
    `401`. Do not widen the bind: UFW does not filter published container ports
    because Docker's own iptables chains run first.
  - Dockhand's environment list still contains a stale `Nasus` entry pointing at
    `192.168.0.10:2375`, which no longer answers. It can be removed from the UI.

### Verified CLI Login Flow
```bash
# Run on the CloudNode over SSH. Public HTTPS goes through Pangolin auth and is not ideal for automation.
DOCKHAND_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}' dockhand | awk '{print $1}')

curl -skD /tmp/dockhand.headers \
  -c /tmp/dockhand.cookie \
  -X POST \
  -H 'Content-Type: application/json' \
  -d '{"username":"admin","password":"<dockhand-local-password>"}' \
  "http://${DOCKHAND_IP}:3000/api/auth/login"

TOKEN=$(awk '/dockhand_session/ {print $7}' /tmp/dockhand.cookie)
curl -sk -H "Cookie: dockhand_session=${TOKEN}" \
  "http://${DOCKHAND_IP}:3000/api/stacks?env=3"
```

### Environment IDs
- `env=1`: CloudNode
- `env=2`: Nasus (`192.168.0.10`) — **stale and dead**; no Hawser runs there since 2026-11-21
- `env=3`: Rammus (`192.168.0.12`) — the live home environment

Use `env=3` for anything on the home side. A request with `env=2` fails or returns
empty, which is not evidence that rammus is down. The `Nasus` entry still exists in
the Dockhand UI and can be deleted.

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

No Dockhand Git stacks are configured; the `/api/git/*` rows are API capability only.

## When Editing Docs
- Keep `README.md` and `INFRASTRUCTURE.md` in sync with compose files.
- If services move between stacks, update this file too.

## Historical maintenance record — 2026-10-27

Superseded by the 2026-11-21 move to rammus (`docs/wiki/hosts/rammus.md`).
Still valid from that pass: FileFlows and its DV watcher are decommissioned (do
not recreate them from old archives); Olm uses a root-only `CONFIG_FILE` with
`UMask=0077` and its credential was rotated; backup archives, logs and the NAS
recovery-kit PDF are owner-only; six CloudNode database snapshots, encrypted
off-host copies in both directions and isolated native recovery were verified,
with both off-host timers enabled under user lingering (see the recovery runbook).
NASUS-era details in `docs/wiki/maintenance-2026-10-27.md` (NAS Traefik, Newt's
Dockhand Git compose) no longer describe the live layout: Newt runs on rammus and
Dockhand has no Git integration.
