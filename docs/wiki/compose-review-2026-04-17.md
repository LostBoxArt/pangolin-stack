---
title: "Compose-File Review — 2026-04-17"
slug: cloudnode-compose-review-2026-04-17
type: review
status: active
tags: ["homelab", "cloudnode", "review", "audit"]
aliases: ["cloudnode audit 2026-04-17"]
entities:
  primary: cloudnode-compose-review-2026-04-17
  mentions: []
related: ["./README.md", "./system-overview.md"]
sources: ["stacks/core/docker-compose.yml", "stacks/security/docker-compose.yml", "stacks/dns/docker-compose.yml", "stacks/observability/docker-compose.yml", "stacks/management/docker-compose.yml", "stacks/dashboard/docker-compose.yml", "stacks/apps/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# Compose-File Review — 2026-04-17

Full audit of every `docker-compose.yml` under `stacks/` against upstream
documentation and reference compose files. Findings, severities, and
remediation steps are collected here. Per-service detail lives in the
[`services/`](./services) pages.

- Reviewer: agent session 2026-04-17
- Scope: 7 stacks, 14 services
- Method: each compose file diffed against its upstream reference compose or
  official docs (URLs captured per service page)

---

## TL;DR Scoreboard

| Stack | File | Services | Critical | High | Medium | Low | Status |
|---|---|---|---|---|---|---|---|
| core | `stacks/core/docker-compose.yml` | pangolin, gerbil, traefik | 0 | 1 | 3 | 1 | active |
| security | `stacks/security/docker-compose.yml` | crowdsec, crowdsec-web-ui, pocket-id | 1 | 2 | 2 | 0 | active |
| dns | `stacks/dns/docker-compose.yml` | adguard-home | 0 | 0 | 1 | 1 | **removed 2026-04-21** |
| observability | `stacks/observability/docker-compose.yml` | traefik-agent, traefik-dashboard, dashdot | 0 | 2 | 2 | 1 | active |
| management | `stacks/management/docker-compose.yml` | dockhand | 0 | 0 | 1 | 0 |
| dashboard | `stacks/dashboard/docker-compose.yml` | homarr, qbit-proxy | 0 | 0 | 0 | 2 |
| apps | `stacks/apps/docker-compose.yml` | landing, termix | 0 | 0 | 2 | 2 |
| **total** | — | 14 | **1** | **5** | **11** | **7** |

---

## Critical Findings (fix first)

### C1. Pocket-ID shares the repo `data/` directory with other services
- **Service**: [pocket-id](./services/pocket-id.md)
- **File**: `stacks/security/docker-compose.yml` line ~85
- **Symptom**: Volume is `../../data:/app/data`, which mounts the *entire*
  repo `data/` folder (which also holds `data/dockhand/`, `data/positions/`)
  into Pocket-ID's writable data directory. Upstream mounts `./data` as a
  dedicated directory.
- **Risk**: Pocket-ID may write siblings (e.g. `pocket-id.db`, `keys/`) into
  the shared tree. On a wipe/restore it's unclear what belongs to which
  service. Permission changes made by Pocket-ID (runs as root in container)
  can affect other services' files.
- **Remediation**: change volume to `../../data/pocket-id:/app/data`,
  migrate existing files with `sudo mv data/<pocket-id-files> data/pocket-id/`
  while stack is down, then `docker compose up -d`.

---

## High Findings

### H2. CrowdSec Traefik log mount is read-write; upstream is `:ro`
- **Service**: [crowdsec](./services/crowdsec.md)
- **File**: `stacks/security/docker-compose.yml`
- **Upstream** (`fosrl/pangolin/install/config/crowdsec/docker-compose.yml`):
  `./config/traefik/logs:/var/log/traefik:ro`
- **Risk**: CrowdSec runs as root and only needs to read Traefik's JSON
  access log. A rogue parser bug could truncate/rotate logs unexpectedly.
- **Remediation**: add `:ro` suffix.

### H3. Traefik-log-dashboard uses legacy env-var scheme
- **Service**: [traefik-log-dashboard](./services/traefik-log-dashboard.md)
- **File**: `stacks/observability/docker-compose.yml`
- **Upstream** (`hhftechnology/traefik-log-dashboard/docker-compose.yml`):
  uses `AGENT_1_NAME` / `AGENT_1_URL` / `AGENT_1_TOKEN` +
  `DASHBOARD_AGENTS_ENV_ONLY=true`. Ours uses `AGENT_API_URL`/`AGENT_API_TOKEN`.
- **Risk**: Older env scheme may silently stop being read on image bumps.
  Also prevents adding a second agent cleanly.
- **Remediation**: rewrite the dashboard's `environment:` block, see
  service page for the exact diff.

### H4. Dashboard state has no persistent volume
- **Service**: [traefik-log-dashboard](./services/traefik-log-dashboard.md)
- **File**: `stacks/observability/docker-compose.yml`
- **Upstream**: declares a named volume `dashboard-data:/data`.
- **Risk**: any saved preferences / cached GeoIP lookups are lost on
  `docker compose down` or image update.
- **Remediation**: add named volume `dashboard-data` and mount into the
  dashboard service at `/data`.

---

## Medium Findings

### M1. `pangolin` has no memory limits
Upstream sets `limits: memory: 1g`, `reservations: memory: 256m`. Our
`pangolin` can grow unbounded. See [pangolin](./services/pangolin.md).

### M2. Gerbil is missing `443/udp` (HTTP/3 QUIC)
Upstream exposes `443:443/udp` on gerbil alongside TCP. Our file exposes only
TCP 443. This disables HTTP/3 for all downstream sites behind Traefik. See
[gerbil](./services/gerbil.md).

### M3. CrowdSec healthcheck has no interval/timeout/retries/start_period
Upstream declares all four. Ours declares only `test`. Without them Docker
uses defaults that may flap at startup. See [crowdsec](./services/crowdsec.md).

### M4. CrowdSec exposes LAPI `8080:8080` on the host
Not needed if all bouncers live on the `pangolin` docker network (they do).
Exposing it broadens attack surface. See [crowdsec](./services/crowdsec.md).

### M5. Traefik-log-dashboard has no GeoIP configuration
Upstream sets `GEOIP_PROVIDER_URLS=https://ipwho.is,https://ip-api.com/json`.
Without it, all source IPs show "Unknown" in the UI. See
[traefik-log-dashboard](./services/traefik-log-dashboard.md).

### M6. Dockhand image pin
`fnsys/dockhand:latest`. Dockhand writes its own SQLite schema; a breaking
release shipped as `latest` could corrupt state. Pin to a known tag. See
[dockhand](./services/dockhand.md).

### M7. LinkStack runs as root in container
Upstream compose sets `user: apache:apache`. Ours doesn't. See
[linkstack](./services/linkstack.md) (archived — replaced by [landing](./services/landing.md) on 2026-04-21).

### M8. Termix is missing the `guacd` sidecar
Upstream ships with `guacamole/guacd` for RDP/VNC support. If you only ever
SSH through Termix this is fine; if you ever want RDP/VNC it will fail. See
[termix](./services/termix.md).

### M9. AdGuard Home has no `TZ`
Timestamps in logs will be UTC. See [adguard-home](./services/adguard-home.md).

### M10. Most service images use `:latest`
Specifically `traefik`, `adguardhome`, `dockhand`, `homarr`, `landing`,
`termix`, `dashdot`, `crowdsec`, `traefik-log-dashboard*`. Drift risk per
`AGENTS.md` policy. See each service page.

### M11. CrowdSec env has a redundant `ACQUIRE_FILES`
Our `acquis.yaml` already defines acquisition. The env var duplicates this.
Low-risk cruft. See [crowdsec](./services/crowdsec.md).

---

## Low Findings

- **L1**. `command: -t` (CrowdSec config validation on start) present upstream,
  missing here. [crowdsec](./services/crowdsec.md).
- **L2**. Gerbil healthcheck absent. Upstream also omits it, but adding one
  is trivial. [gerbil](./services/gerbil.md).
- **L3**. Homarr has no healthcheck. [homarr](./services/homarr.md).
- **L4**. LinkStack/Termix have no healthcheck.
  [linkstack](./services/linkstack.md) (archived), [termix](./services/termix.md).
- **L5**. Dashdot: we already use `group_add: "986"` instead of upstream's
  `privileged: true`. **This is better than upstream** — recorded so nobody
  "helpfully" adds `privileged: true` back. [dashdot](./services/dashdot.md).

---

## Remediation Plan (suggested order)

1. **C1 / H3** — fix Pocket-ID volume path (critical data-layout bug).
2. **H1** — pin Traefik to `v3.6`.
3. **H2** — make CrowdSec Traefik log mount read-only.
4. **M1, M2** — memory limits + QUIC port on core.
5. **H4, H5, M5** — observability dashboard refresh.
6. **M3, M4, M11, L1** — CrowdSec hardening sweep.
7. **M10** — global pin pass on all `:latest` tags.
8. **M7, M8, M9** — app-level hardening.
9. **L2–L5** — healthcheck additions.

Each step should be a separate commit so any breakage is bisectable.

---

## Rollback

All proposed changes are limited to compose files (and possibly `AGENTS.md`).
Rollback is always:

```bash
git restore -- stacks/**/docker-compose.yml AGENTS.md
./stackctl.sh restart <stack>
```

For the Pocket-ID volume migration (C1), also move data back:

```bash
./stackctl.sh stop security
sudo mv data/pocket-id/* data/
rmdir data/pocket-id
git restore -- stacks/security/docker-compose.yml
./stackctl.sh start security
```

---

## Upstream Sources Consulted

| Service | Source |
|---|---|
| pangolin / gerbil / traefik | `https://raw.githubusercontent.com/fosrl/pangolin/main/install/config/docker-compose.yml` |
| crowdsec | `https://raw.githubusercontent.com/fosrl/pangolin/main/install/config/crowdsec/docker-compose.yml` |
| pocket-id | `https://raw.githubusercontent.com/pocket-id/pocket-id/main/docker-compose.yml` + `https://pocket-id.org/docs/setup/installation` |
| adguard-home | `https://github.com/AdguardTeam/AdGuardHome/wiki/Docker` |
| traefik-log-dashboard | `https://raw.githubusercontent.com/hhftechnology/traefik-log-dashboard/main/docker-compose.yml` |
| dashdot | `https://getdashdot.com/docs/installation/docker-compose` + repo README |
| dockhand | `https://github.com/Finsys/dockhand/blob/main/docker-compose.yaml` + `https://dockhand.pro/manual/` |
| homarr | `https://homarr.dev/docs/getting-started/installation/docker/` |
| landing | N/A (bespoke static page) |
| termix | `https://docs.termix.site/install/server/docker` |

---

## Changelog

- 2026-04-21 — LinkStack replaced by bespoke `landing` static page. See
  [landing.md](./services/landing.md) for the new service and
  [linkstack.md](./services/linkstack.md) for the archived page.
- 2026-04-17 — Added: initial compose review, findings, and per-service wiki
  pages. No compose edits performed this session.
