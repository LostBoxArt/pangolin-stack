---
title: "adguard-home"
slug: cloudnode-adguard-home
type: service
status: active
tags: ["homelab", "cloudnode", "service", "adguard-home"]
aliases: ["adguard-home"]
entities:
  primary: cloudnode-adguard-home
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/dns/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# adguard-home

Network-wide DNS filtering. Exposed publicly as:

- DoH: `https://dns.example.com/dns-query`
- DoT: `dns.example.com:853`
- WebUI: `https://dns.example.com`

All traffic reaches AdGuard through Traefik — plain DNS (53/udp) is **not**
exposed, by design.

- **Image**: `adguard/adguardhome:latest` ⚠️
- **Compose file**: `stacks/dns/docker-compose.yml`
- **Config**: `./config/adguard-home/conf/`
- **Work dir** (filter lists, stats): `./config/adguard-home/work/`

## Upstream Sources

- Docker wiki: <https://github.com/AdguardTeam/AdGuardHome/wiki/Docker>
- Releases: <https://github.com/AdguardTeam/AdGuardHome/releases>
- Config reference: <https://github.com/AdguardTeam/AdGuardHome/wiki/Configuration>

## Upstream Reference (docker run equivalent)

```bash
docker run --name adguardhome \
  --restart unless-stopped \
  -v /my/own/workdir:/opt/adguardhome/work \
  -v /my/own/confdir:/opt/adguardhome/conf \
  -p 53:53/tcp -p 53:53/udp \
  -p 67:67/udp -p 68:68/udp \
  -p 80:80/tcp -p 443:443/tcp -p 443:443/udp -p 3000:3000/tcp \
  -p 853:853/tcp -p 853:853/udp \
  -p 5443:5443/tcp -p 5443:5443/udp \
  -p 6060:6060/tcp \
  -d adguard/adguardhome
```

Upstream also explicitly documents: the image **no longer ships a
healthcheck** — it was removed between v0.107.27 and v0.107.34 due to issues
(#5711, #5713, discussion #5939). Any healthcheck is DIY.

## Our Compose (relevant slice)

```11:54:stacks/dns/docker-compose.yml
  adguard-home:
    image: adguard/adguardhome:latest
    container_name: adguard-home
    hostname: adguard-home
    networks:
      - pangolin
    restart: unless-stopped
    volumes:
      - ../../config/adguard-home/work:/opt/adguardhome/work
      - ../../config/adguard-home/conf:/opt/adguardhome/conf
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.adguard-redirect.rule=Host(`dns.example.com`)"
      - "traefik.http.routers.adguard-redirect.entrypoints=web"
      - "traefik.http.routers.adguard-redirect.middlewares=redirect-to-https@file"
      - "traefik.http.routers.adguard.rule=Host(`dns.example.com`)"
      - "traefik.http.routers.adguard.entrypoints=websecure"
      - "traefik.http.routers.adguard.tls.certresolver=letsencrypt"
      - "traefik.http.routers.adguard.middlewares=security-headers@file"
      - "traefik.http.services.adguard.loadbalancer.server.port=80"
      - "traefik.http.routers.adguard-doh.rule=Host(`dns.example.com`) && PathPrefix(`/dns-query`)"
      - "traefik.http.routers.adguard-doh.entrypoints=websecure"
      - "traefik.http.routers.adguard-doh.tls.certresolver=letsencrypt"
      - "traefik.http.routers.adguard-doh.middlewares=doh-ratelimit@file"
      - "traefik.http.services.adguard-doh.loadbalancer.server.port=80"
      - "traefik.tcp.routers.adguard-dot.rule=HostSNI(`dns.example.com`)"
      - "traefik.tcp.routers.adguard-dot.entrypoints=dns-tls"
      - "traefik.tcp.routers.adguard-dot.tls.certresolver=letsencrypt"
      - "traefik.tcp.services.adguard-dot.loadbalancer.server.port=53"
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Image tag | `:latest` or version-pinned | `:latest` | drift risk |
| Plain DNS (53/udp) | exposed | **not exposed** | intentional — DoH/DoT only, for our public profile |
| DHCP ports (67/68) | optional | not exposed | n/a — we don't run DHCP |
| WebUI port | initially `3000`, can be moved to `80` | assumed moved to `80` via setup wizard | ⚠️ depends on runtime config; see note below |
| Healthcheck | upstream removed theirs | custom `wget localhost:80` | ✓ — but only works if WebUI was moved to :80 |
| TZ env | not set | not set | should add |

## Findings

### F-ADGUARD-1 — `:latest` image tag (`medium` / M10 scope)
Not pinned. AdGuard Home doesn't have the same plugin-compatibility risk as
Traefik, but their release notes occasionally tighten YAML schema and a
bad `latest` pull has broken setups (see <https://github.com/AdguardTeam/AdGuardHome/issues?q=docker+latest>).

### F-ADGUARD-2 — no `TZ` env (`medium` / M9)
Internal logs and query-log timestamps will be UTC. Annoying when
cross-referencing with Traefik logs (which, in our setup, inherit host TZ
via the mount).

### F-ADGUARD-3 — WebUI port implicit (`low`)
The healthcheck (`wget http://localhost:80`) assumes the AdGuard admin
moved the WebUI bind port from the first-run default of `3000` to `80`.
If a fresh install / wipe happens, the healthcheck will fail until the
setup wizard is completed. Not a compose bug, but worth documenting.

## Remediation

### Fix F-ADGUARD-1 — pin the tag

Pick a current release from
<https://github.com/AdguardTeam/AdGuardHome/releases>, e.g.:

```yaml
    image: adguard/adguardhome:v0.107.66
```

### Fix F-ADGUARD-2 — add TZ

```yaml
    environment:
      - TZ=Asia/Jerusalem
```

(Match the TZ used by `homarr` / `linkstack`.)

### Fix F-ADGUARD-3 — healthcheck that doesn't depend on user-config

Use a DNS-level probe instead:

```yaml
    healthcheck:
      test: ["CMD", "sh", "-c", "wget -q --spider http://localhost:3000 || wget -q --spider http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
```

Or rely on AdGuard's internal `healthcheck.adguardhome.test.` convention
(see upstream wiki).

## Operational Notes

- Filter lists and query log are in `config/adguard-home/work/data/`. Large
  (100s of MB) — confirm `backup.sh` excludes them if you don't want them
  in backups.
- DoT router uses a dedicated Traefik entrypoint `dns-tls` (see
  `traefik_config.yml`) — if that entrypoint isn't defined, DoT silently
  fails with no logs.
- `doh-ratelimit@file` middleware is required on DoH to prevent AdGuard
  from being used as open resolver abuse target.
