---
title: "traefik-log-dashboard (agent + UI)"
slug: cloudnode-traefik-log-dashboard
type: service
status: active
tags: ["homelab", "cloudnode", "service", "traefik-log-dashboard"]
aliases: ["traefik-log-dashboard (agent + UI)", "traefik-log-dashboard"]
entities:
  primary: cloudnode-traefik-log-dashboard
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/observability/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# traefik-log-dashboard (agent + UI)

Two services, one codebase: the **agent** tails Traefik's JSON access/error
logs and exposes a parsed stream; the **dashboard** renders that stream in a
React SPA with geolocation, status-code breakdowns, and service metrics.

- **Agent image**: `hhftechnology/traefik-log-dashboard-agent:latest` ⚠️
- **UI image**: `hhftechnology/traefik-log-dashboard:latest` ⚠️
- **Compose file**: `stacks/observability/docker-compose.yml`
- **Agent port**: `5000` (host)
- **UI port**: `3457:3000` (host) → fronted by Traefik at
  `traefik-logs.example.com`
- **Agent reads**: `config/traefik/logs/` (ro)
- **Agent state**: `data/positions/` (tail position cache)

## Upstream Sources

- Reference compose: <https://raw.githubusercontent.com/hhftechnology/traefik-log-dashboard/main/docker-compose.yml>
- Repo: <https://github.com/hhftechnology/traefik-log-dashboard>

## Upstream Reference Compose

```yaml
services:
  traefik-agent:
    image: hhftechnology/traefik-log-dashboard-agent:dev-dashboard
    ...
    environment:
      - TRAEFIK_LOG_DASHBOARD_ACCESS_PATH=/logs/access.log
      - TRAEFIK_LOG_DASHBOARD_ERROR_PATH=/logs/traefik.log
      - TRAEFIK_LOG_DASHBOARD_AUTH_TOKEN=<token>
      - TRAEFIK_LOG_DASHBOARD_SYSTEM_MONITORING=true
      - TRAEFIK_LOG_DASHBOARD_LOG_FORMAT=json
      - PORT=5000
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:5000/api/logs/status"]
      interval: 2m
      timeout: 10s
      retries: 3
      start_period: 30s

  traefik-dashboard:
    image: hhftechnology/traefik-log-dashboard:dev-dashboard
    ...
    volumes:
      - dashboard-data:/data
    environment:
      - AGENT_1_NAME=Primary Agent
      - AGENT_1_URL=http://traefik-agent:5000
      - AGENT_1_TOKEN=<token>
      - DASHBOARD_AGENTS_ENV_ONLY=true
      - DASHBOARD_TRAFFIC_TOP_ITEMS_LIMIT=25
      - DASHBOARD_PARSER_TREND_WINDOW_MINUTES=30
      - GEOIP_PROVIDER_URLS=https://ipwho.is,https://ip-api.com/json
      - GEOIP_UNKNOWN_CACHE_TTL_MS=300000

volumes:
  dashboard-data:
```

## Our Compose (relevant slice)

```10:57:stacks/observability/docker-compose.yml
  traefik-agent:
    image: hhftechnology/traefik-log-dashboard-agent:latest
    container_name: traefik-agent
    networks:
      - pangolin
    restart: unless-stopped
    ports:
      - "5000:5000"
    volumes:
      - ../../data/positions:/data
      - ../../config/traefik/logs:/logs:ro
    environment:
      - TRAEFIK_LOG_DASHBOARD_ACCESS_PATH=/logs/access.log
      - TRAEFIK_LOG_DASHBOARD_ERROR_PATH=/logs/traefik.log
      - TRAEFIK_LOG_DASHBOARD_AUTH_TOKEN=${TRAEFIK_DASHBOARD_TOKEN}
      - TRAEFIK_LOG_DASHBOARD_SYSTEM_MONITORING=true
      - TRAEFIK_LOG_DASHBOARD_LOG_FORMAT=json
      - PORT=5000

  traefik-dashboard:
    image: hhftechnology/traefik-log-dashboard:latest
    container_name: traefik-dashboard
    networks:
      - pangolin
    restart: unless-stopped
    ports:
      - "3457:3000"
    environment:
      - AGENT_API_URL=http://traefik-agent:5000
      - AGENT_API_TOKEN=${TRAEFIK_DASHBOARD_TOKEN}
      - NODE_ENV=production
      - PORT=3000
    depends_on:
      traefik-agent:
        condition: service_healthy
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Image tags | `:dev-dashboard` | `:latest` | drift risk on both |
| Agent healthcheck interval | `2m` | `30s` | unnecessarily aggressive |
| Dashboard env scheme | `AGENT_1_*` + `DASHBOARD_AGENTS_ENV_ONLY=true` | legacy `AGENT_API_URL/TOKEN` | ⚠️ unintentional drift |
| GeoIP providers | `GEOIP_PROVIDER_URLS=...` | not set | ⚠️ unintentional; all IPs show "Unknown" |
| Dashboard persistent volume | `dashboard-data:/data` | not mounted | ⚠️ state lost on recreate |
| Dashboard tuning envs | set | not set | nice-to-have |
| Agent log volume | `./data/logs:/logs:ro` | `config/traefik/logs:/logs:ro` | intentional — our Traefik writes elsewhere |

## Findings

### F-TLD-1 — legacy agent env scheme (`high` / H4)
`AGENT_API_URL`/`AGENT_API_TOKEN` are the pre-multi-agent env names. Any
future image that drops the fallback will have the dashboard unable to find
the agent. Silent failure — the UI just shows an empty state.

### F-TLD-2 — no persistent volume (`high` / H5)
Every `docker compose up -d --force-recreate traefik-dashboard` wipes
dashboard-side state: saved filters, cached GeoIP lookups, user session if
the image ever adds one.

### F-TLD-3 — no GeoIP provider configured (`medium` / M5)
The UI's geo-map and "Top Countries" widgets will all show "Unknown". Two
free providers (ipwho.is, ip-api.com) are supplied by upstream defaults but
only activate when the `GEOIP_PROVIDER_URLS` env is set explicitly.

### F-TLD-4 — `:latest` image tag on both (`medium` / M10 scope)
Both images are third-party. `dev-dashboard` is their recommended tag. The
repo ships frequent schema changes between dashboard UI and agent; mismatched
versions = stuck "Connecting…" UI. Use the same tag on both.

### F-TLD-5 — aggressive healthcheck (`low`)
`interval: 30s` on an agent that reads a file every few seconds is fine, but
upstream `2m` is more than enough and saves wake-ups.

## Remediation

### Fix F-TLD-1 + F-TLD-2 + F-TLD-3 (single patch on the UI service)

```yaml
  traefik-dashboard:
    image: hhftechnology/traefik-log-dashboard:dev-dashboard
    ...
    volumes:
      - dashboard-data:/data
    environment:
      - AGENT_1_NAME=Primary Agent
      - AGENT_1_URL=http://traefik-agent:5000
      - AGENT_1_TOKEN=${TRAEFIK_DASHBOARD_TOKEN}
      - DASHBOARD_AGENTS_ENV_ONLY=true
      - DASHBOARD_TRAFFIC_TOP_ITEMS_LIMIT=25
      - DASHBOARD_PARSER_TREND_WINDOW_MINUTES=30
      - GEOIP_PROVIDER_URLS=https://ipwho.is,https://ip-api.com/json
      - GEOIP_UNKNOWN_CACHE_TTL_MS=300000
      - NODE_ENV=production
      - PORT=3000
    depends_on:
      traefik-agent:
        condition: service_healthy
```

Add at bottom of the stack file:

```yaml
volumes:
  dashboard-data:
    driver: local
```

### Fix F-TLD-4 — pin and align both images

Pick a known-good release (e.g. `2026.3.x`) from
<https://github.com/hhftechnology/traefik-log-dashboard/releases> and use
the **same tag** on both the agent and the dashboard image.

### Fix F-TLD-5 (optional)

```yaml
    healthcheck:
      ...
      interval: 2m
```

## Operational Notes

- Access the UI via `https://traefik-logs.example.com` (Traefik-fronted,
  Pocket-ID protected in `rules/`) rather than `:3457` directly.
- The `TRAEFIK_DASHBOARD_TOKEN` in `.env` is a shared secret used on both
  sides of the agent↔UI connection — rotating it requires restarting both
  services.
- If the UI shows "Agent offline" but the agent is healthy, suspect token
  drift first.
