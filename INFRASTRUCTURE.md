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
│  │   Traefik   │◄───│  Pangolin   │    │   Gerbil    │    │  CrowdSec   │            │
│  │  :80, :443  │    │   :3001     │    │  :51820/udp │    │   :8080     │            │
│  └──────┬──────┘    └─────────────┘    └──────┬──────┘    └─────────────┘            │
│         │                                      │                                      │
│         ▼                                      │ WireGuard tunnel                     │
│  ┌─────────────┐    ┌─────────────┐            │ (to Home Newt)                       │
│  │   Homarr    │◄───┤  qbit-proxy │◄───────────┘                                      │
│  │   :7575     │    │   :8081     │  (via OLM)                                       │
│  └─────────────┘    └─────────────┘                                                   │
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
        Homarr --> qbit-proxy
        qbit-proxy -- "OLM Tunnel" --> HomeTraefik
        TraefikDashboard --> TraefikAgent
        CrowdSecWebUI --> CrowdSec
        PocketID
    end
    
    subgraph "Remote"
        OlmSystemd[Olm - Systemd] --> Gerbil
        Gerbil --> Newt
        Newt --> HomeServices[Home Services]
    end
```

## Docker Compose Stacks

Stacks are organized in `stacks/<stack>/docker-compose.yml`:

| Stack | Purpose | Services |
|-------|---------|----------|
| `core` | Infrastructure (starts first) | pangolin, gerbil, traefik |
| `security` | Protection & auth | crowdsec, crowdsec-web-ui, pocket-id |
| `dns` | DNS-over-HTTPS & filtering | adguard-home |
| `observability` | Monitoring & logs | traefik-agent, traefik-dashboard, dashdot |
| `management` | Container orchestration | dockhand |
| `dashboard` | User dashboards | homarr, qbit-proxy |
| `apps` | User applications | linkstack, termix |

Use `./stackctl.sh status` to view all stacks or `./startup.sh` to start everything.

## Pinned Versions

- Pangolin: `fosrl/pangolin:1.16.2`
- Gerbil: `fosrl/gerbil:1.3.0`
- Traefik Badger plugin: `github.com/fosrl/badger@v1.3.1`
- Newt (NASUS): `fosrl/newt:1.10.1`
- Olm (VPS systemd binary): `1.4.2` with `--override-dns=false`

Compatibility note: Newt `1.10.x` adds Pangolin SSH support and aligns with Pangolin `1.16.x`. If Pangolin remains on `1.15.x`, updating Newt alone is still supported, but that new SSH path is not active.

Upgrade policy: read official Pangolin docs plus release notes for Pangolin, Gerbil, Newt, Olm, and Badger before applying image or binary changes.


## AdGuard Home

The VPS runs its own independent AdGuard Home instance with DNS-over-HTTPS (DoH) and DNS-over-TLS (DoT) support.

### Access
- **Web UI**: https://dns.dennisb.xyz
- **DoH Endpoint**: `https://dns.dennisb.xyz/dns-query`
- **DoT Endpoint**: `dns.dennisb.xyz:853`

### Management
```bash
# Access web UI to configure blocklists and upstream DNS
# https://dns.dennisb.xyz

# Check query logs
docker logs adguard-home --tail 50
```

## Olm Tunnel Configuration

Olm is currently running as a **systemd service** on the VPS host to ensure it has the necessary network permissions and stability.

### Management
```bash
sudo systemctl status olm
sudo journalctl -u olm -f
sudo systemctl status olm-watchdog.timer
```

### Reliability Guards

- VPS watchdog: `/usr/local/sbin/olm-watchdog.sh` with systemd timer `olm-watchdog.timer`.
- NASUS watchdog: `/usr/local/bin/newt-watchdog.sh` from root crontab every minute.

## Dockhand API

Use the Dockhand container's internal HTTP endpoint over SSH to the VPS for automation. The public `https://dockhand.dennisb.xyz` URL is fronted by Pangolin auth and is not the right path for CLI API calls.

Verified flow:

```bash
ssh jesus@dennisb.xyz '
DOCKHAND_IP=$(docker inspect -f "{{range .NetworkSettings.Networks}}{{.IPAddress}} {{end}}" dockhand | awk "{print \$1}")

curl -skD /tmp/dockhand.headers \
  -c /tmp/dockhand.cookie \
  -X POST \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"jesus\",\"password\":\"<dockhand-local-password>\"}" \
  "http://${DOCKHAND_IP}:3000/api/auth/login"

TOKEN=$(awk "/dockhand_session/ {print \$7}" /tmp/dockhand.cookie)
curl -sk -H "Cookie: dockhand_session=${TOKEN}" \
  "http://${DOCKHAND_IP}:3000/api/stacks?env=2"
'
```

Environment IDs:
- `1` = VPS
- `2` = NASUS

Common API endpoints:
- `GET /api/containers?env=<id>`
- `GET /api/stacks?env=<id>`
- `GET /api/git/stacks?env=<id>`
- `POST /api/git/stacks/{id}/deploy?env=<id>`
- `POST /api/containers/{id}/restart?env=<id>`

## qBittorrent Proxy Sidecar

Homarr v0.15+ has a known issue with qBittorrent v5.1.4+ API responses when served over HTTPS with "Secure" cookies. The `qbit-proxy` service acts as a bridge:

1. **Strips Secure Flag**: Removes `secure;` from cookies so Homarr can see them.
2. **Handles SNI**: Properly sets the `Host: torrent.dennisb.xyz` header.
3. **Internal HTTP**: Allows Homarr to connect via plain HTTP internally.

### Access Pattern

```
Widget URL: http://qbit-proxy:8081
    ↓ Proxy translation
Destination: https://192.168.0.10:443
    ↓ SNI injection
Host Header: torrent.dennisb.xyz
    ↓ OLM tunnel
Home Traefik
```

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

## Traefik Config

- Static config: `config/traefik/traefik_config.yml`
- Dynamic rules: `config/traefik/rules/`
- Overrides are disabled and kept as `config/traefik/rules/resource-overrides.yml.back`

## Troubleshooting Commands

### Olm Tunnel

```bash
# Check tunnel status
sudo systemctl status olm
sudo journalctl -u olm -f

# Verify interface exists
ip addr show olm

# Test connectivity
ping 192.168.0.10

# Check routes
ip route | grep 192.168.0

# Restart tunnel
sudo systemctl restart olm
```
If you run Olm via Docker instead of systemd, use `docker logs olm` and `docker restart olm`.

## Geo-Blocking

The stack implements defense-in-depth geo-blocking using both CrowdSec and Traefik to block traffic from high-risk countries.

### Configuration

**Blocked Countries**: CN, RU, KP, IR, VN, IN, PK, BD, NG, BR, ID, UA, KZ  
**Whitelisted**: IL (Israel), EU member states, US, CA, GB, AU, NZ, JP, KR, SG

### Components

1. **CrowdSec GeoIP Enrichment** (`config/crowdsec/scenarios/country-block.yaml`)
   - Enriches logs with country data
   - Bans IPs from blocked countries for 24 hours
   - Uses `crowdsecurity/geoip-enrich` parser

2. **Traefik GeoBlock Middleware** (`config/traefik/rules/geoblock-middleware.yml`)
   - Immediate edge blocking using GeoJS API
   - Applied to: LinkStack, Termix, Homarr, Dashdot
   - Not applied to: PocketID (has own MaxMind), Pangolin, CrowdSec, Dockhand

### Management

```bash
# View geo-blocking alerts
docker exec crowdsec cscli alerts list --origin custom/country-block

# Check blocked decisions
docker exec crowdsec cscli decisions list

# Whitelist an additional country: edit both files
# - config/crowdsec/scenarios/country-block.yaml
# - config/traefik/rules/geoblock-middleware.yml
# Then restart services
docker restart crowdsec
./stackctl.sh restart core
```

## Blocklist Import

The stack imports 60,000+ IPs from 28 public threat feeds into CrowdSec for proactive blocking. This provides premium-level threat protection using free, curated feeds like IPsum, Spamhaus, Firehol, and Abuse.ch.

### Running Manually

```bash
# Using the helper script
./scripts/blocklist-import.sh

# Or run directly
curl -sL https://raw.githubusercontent.com/wolffcatskyy/crowdsec-blocklist-import/main/import.sh | \
    MODE=docker CROWDSEC_CONTAINER=crowdsec bash
```

### Scheduled Import (Recommended)

Add to crontab for daily refresh at 4 AM:

```bash
crontab -e
# Add this line:
0 4 * * * /home/jesus/pangolin-stack/scripts/blocklist-import.sh
```

### View Imported Decisions

```bash
# Count imported decisions
docker exec crowdsec cscli decisions list | grep external_blocklist | wc -l

# List recent blocklist decisions
docker exec crowdsec cscli decisions list -l 20 | grep external_blocklist

# Remove all imported decisions (if needed)
docker exec crowdsec cscli decisions delete --all --reason external_blocklist
```


### CrowdSec

```bash
# Check decisions
docker exec crowdsec cscli decisions list

# Check bouncers
docker exec crowdsec cscli bouncers list

# View alerts
docker exec crowdsec cscli alerts list

# Geo-blocking metrics
docker exec crowdsec cscli metrics
docker exec crowdsec cscli alerts list -l 20 --origin custom/country-block

# Verify GeoIP enrichment is active
docker exec crowdsec cscli parsers list | grep geoip

# Verify country-block scenario is loaded
docker exec crowdsec cscli scenarios list | grep country
```

## Environment Variables

Key variables in `.env`:

| Variable | Purpose |
|----------|---------|
| `TRAEFIK_DASHBOARD_TOKEN` | Auth token for traefik-dashboard |
| `CROWDSEC_AGENT_KEY` | CrowdSec agent registration key |
| `CROWDSEC_WEB_UI_PASSWORD` | CrowdSec Web UI login |
| `HOMARR_SECRET_KEY` | Homarr encryption key |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token for notifications |
| `TELEGRAM_CHAT_ID` | Telegram chat ID for notifications |
| `POCKET_ID_APP_URL` | Pocket ID public URL |
| `POCKET_ID_ENCRYPTION_KEY` | Pocket ID encryption secret |
| `POCKET_ID_TRUST_PROXY` | Pocket ID proxy trust flag |
| `MAXMIND_ACCOUNT_ID` | MaxMind account ID for Pocket ID |
| `MAXMIND_LICENSE_KEY` | MaxMind license key for Pocket ID |
| `DISABLE_ONLINE_API` | CrowdSec online API toggle |
| `DISABLE_HUB_UPDATE` | CrowdSec hub update toggle |

## Permissions Notes

| Path | Required Owner | Why |
|------|----------------|-----|
| `config/crowdsec-web-ui/` | Container writable | SQLite database |
| `/var/run/docker.sock` | root:docker (986) | Docker API access |

If permissions break, fix with:
```bash
sudo chmod 666 config/crowdsec-web-ui/crowdsec.db*

```
