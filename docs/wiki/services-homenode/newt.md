---
title: "newt"
slug: homenode-newt
type: service
status: active
tags: ["homelab", "homenode", "service", "newt"]
aliases: ["newt"]
entities:
  primary: homenode-newt
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/newt/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-23
last_lint: 2026-10-23
---
# newt

Fossorial Newt — Pangolin site connector. Establishes the outbound tunnel
from HomeNode to the CloudNode Pangolin so that LAN services can be reached from
the public `*.example.com` without opening inbound ports on the home
router.

- **Image**: `fosrl/newt:1.19.0` ✓ (live-verified 2026-10-23)
- **Compose file**: `/volume1/docker/config/newt/docker-compose.yml`
- **Tracked copy**: **not tracked** (finding NM1)
- **Network**: `traefik_traefik` + `default`

## Upstream Sources

- Releases: <https://github.com/fosrl/newt/releases>
- Docs: <https://docs.pangolin.net/self-host/sites/newt>

Current deployed tuple (live-verified 2026-10-23): Pangolin `1.25.3` ↔
Newt `1.19.0` ↔ Olm `1.9.1` ↔ Gerbil `1.5.2`. This records the observed
state, not a forward-compatibility guarantee. Check upstream release notes and
documented minimums before future upgrades.

## Our Compose

```yaml
services:
  newt:
    image: fosrl/newt:1.19.0
    container_name: newt
    restart: unless-stopped
    environment:
      - PANGOLIN_ENDPOINT=https://pangolin.example.com
      - NEWT_ID=<REDACTED>
      - NEWT_SECRET=<REDACTED>
    networks:
      - default
      - traefik_traefik
```

## Deviations

| Aspect | Recommended | Ours | Intent |
|---|---|---|---|
| Version | pinned | `1.19.0` ✓ | intentional, aligned |
| `NEWT_ID` | in `.env` | **in compose** | unintentional — credential leak |
| `NEWT_SECRET` | in `.env` | **in compose** | unintentional — credential leak |
| Healthcheck | recommended | none | drift |

## Findings

### F-N-NEWT-1 — credentials in compose file (`high` / NH1)
`NEWT_ID` and `NEWT_SECRET` are still supplied inline in the private HomeNode
Compose file as of 2026-10-23. Their values are intentionally omitted from this
sanitized page, and the Compose file is not tracked in the public repository.
Move them to a private `.env` file before adding a sanitized Compose copy to Git.

### F-N-NEWT-2 — no healthcheck (`medium` / NM10)
If Newt's tunnel flaps, the only visible symptom is that all
`*.example.com` routes (for HomeNode-backed services) return Pangolin's
"site offline" page. A healthcheck would light up red in Dockhand / any
monitoring.

Newt exposes a status endpoint — version-dependent; check
`fosrl/newt` source for the current path.

### F-N-NEWT-3 — not tracked in repo (`high` / NM1)
Will need sanitization before tracking (strip secrets into `.env`).

## Remediation

### Fix F-N-NEWT-1 — move secrets to `.env`

On HomeNode, create `/volume1/docker/config/newt/.env`:

```
NEWT_ID=<stored-in-private-env>
NEWT_SECRET=<stored-in-private-env>
```

Update compose:

```yaml
services:
  newt:
    image: fosrl/newt:1.19.0
    container_name: newt
    restart: unless-stopped
    env_file: [.env]
    environment:
      - PANGOLIN_ENDPOINT=https://pangolin.example.com
    networks: [default, traefik_traefik]
```

Then `chmod 600 .env && chown root:root .env`. Add `.env` to your
DSM-level exclude list so it doesn't end up in automated backups.

**Rotate the secret after** — once it's been committed or readable by
DSM's administrators group it should be considered compromised. Rotate
via Pangolin UI → Sites → this site → regenerate credentials.

### Fix F-N-NEWT-2 (verify endpoint first)

```yaml
    healthcheck:
      test: ["CMD-SHELL", "wget -qO- http://127.0.0.1:3002/status >/dev/null || exit 1"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 20s
```

Adjust the port/path against what Newt 1.19.0 actually exposes (the
socket may be different — `docker exec newt netstat -tlnp` will tell you).

### Fix F-N-NEWT-3

After fixing NEWT-1, copy the sanitized compose into
`host-configs/homenode/newt/docker-compose.yml`. Do NOT commit `.env`.

## Operational Notes

- Newt registers itself with Pangolin using `NEWT_ID` — it's effectively
  the site's username. `NEWT_SECRET` is the password. Together they
  authenticate to Pangolin and establish the tunnel.
- **Upgrade policy**: before bumping `fosrl/newt`, read
  <https://github.com/fosrl/newt/releases> and cross-check with Pangolin's
  minimum-newt version for the Pangolin version running on the CloudNode.
- If the tunnel drops, check logs: `docker logs -f newt`. Watchdog:
  `/usr/local/bin/newt-watchdog.sh` runs from root's crontab every minute.
