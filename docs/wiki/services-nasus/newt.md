---
title: "newt"
slug: nasus-newt
type: service
status: active
tags: ["homelab", "nasus", "service", "newt"]
aliases: ["newt"]
entities:
  primary: nasus-newt
  mentions: []
related: ["./README.md", "./nasus-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/newt/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# newt

Fossorial Newt — Pangolin site connector. Establishes the outbound tunnel
from NASUS to the VPS Pangolin so that LAN services can be reached from
the public `*.dennisb.xyz` without opening inbound ports on the home
router.

- **Image**: `fosrl/newt:1.11.0` ✓ (pinned — matches Pangolin 1.17.x)
- **Compose file**: `/volume1/docker/config/newt/docker-compose.yml`
- **Tracked copy**: **not tracked** (finding NM1)
- **Network**: `traefik_traefik` + `default`

## Upstream Sources

- Releases: <https://github.com/fosrl/newt/releases>
- Docs: <https://docs.pangolin.net/self-host/sites/newt>

Version alignment is mandatory:

- Pangolin 1.17.x ↔ Newt 1.11.x ↔ Olm 1.4.x ↔ Gerbil 1.3.x (per `AGENTS.md`)

## Our Compose

```yaml
services:
  newt:
    image: fosrl/newt:1.11.0
    container_name: newt
    restart: unless-stopped
    environment:
      - PANGOLIN_ENDPOINT=https://pangolin.dennisb.xyz
      - NEWT_ID=8d7jieh8md475z8
      - NEWT_SECRET=85a8sjbtpdvzxrigwqw0jkotokmyskvfj4vc04umhvgks3fc
    networks:
      - default
      - traefik_traefik
```

## Deviations

| Aspect | Recommended | Ours | Intent |
|---|---|---|---|
| Version | pinned | `1.11.0` ✓ | intentional, aligned |
| `NEWT_ID` | in `.env` | **in compose** | unintentional — credential leak |
| `NEWT_SECRET` | in `.env` | **in compose** | unintentional — credential leak |
| Healthcheck | recommended | none | drift |

## Findings

### F-N-NEWT-1 — credentials in compose file (`high` / NH1)
`NEWT_ID` and `NEWT_SECRET` are plaintext in the compose file. As soon as
this file goes into `host-configs/nasus/` in git (which NM1 asks us to
do), the tunnel credentials are in the repo forever.

Even without git, they're readable by anyone who can `cat` the compose
file on NASUS, which on Synology DSM is anyone in the `administrators`
group.

### F-N-NEWT-2 — no healthcheck (`medium` / NM10)
If Newt's tunnel flaps, the only visible symptom is that all
`*.dennisb.xyz` routes (for NASUS-backed services) return Pangolin's
"site offline" page. A healthcheck would light up red in Dockhand / any
monitoring.

Newt exposes a status endpoint — version-dependent; check
`fosrl/newt` source for the current path.

### F-N-NEWT-3 — not tracked in repo (`high` / NM1)
Will need sanitization before tracking (strip secrets into `.env`).

## Remediation

### Fix F-N-NEWT-1 — move secrets to `.env`

On NASUS, create `/volume1/docker/config/newt/.env`:

```
NEWT_ID=8d7jieh8md475z8
NEWT_SECRET=85a8sjbtpdvzxrigwqw0jkotokmyskvfj4vc04umhvgks3fc
```

Update compose:

```yaml
services:
  newt:
    image: fosrl/newt:1.11.0
    container_name: newt
    restart: unless-stopped
    env_file: [.env]
    environment:
      - PANGOLIN_ENDPOINT=https://pangolin.dennisb.xyz
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

Adjust the port/path against what Newt 1.11.0 actually exposes (the
socket may be different — `docker exec newt netstat -tlnp` will tell you).

### Fix F-N-NEWT-3

After fixing NEWT-1, copy the sanitized compose into
`host-configs/nasus/newt/docker-compose.yml`. Do NOT commit `.env`.

## Operational Notes

- Newt registers itself with Pangolin using `NEWT_ID` — it's effectively
  the site's username. `NEWT_SECRET` is the password. Together they
  authenticate to Pangolin and establish the tunnel.
- **Upgrade policy**: before bumping `fosrl/newt`, read
  <https://github.com/fosrl/newt/releases> and cross-check with Pangolin's
  minimum-newt version for the Pangolin version running on the VPS.
- If the tunnel drops, check logs: `docker logs -f newt`. Watchdog:
  `/usr/local/bin/newt-watchdog.sh` runs from root's crontab every minute.
