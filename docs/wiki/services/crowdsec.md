---
title: "crowdsec"
slug: vps-crowdsec
type: service
status: active
tags: ["homelab", "vps", "service", "crowdsec"]
aliases: ["crowdsec"]
entities:
  primary: vps-crowdsec
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/security/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# crowdsec

IDS/IPS that reads Traefik's access log (and host `auth.log`/`syslog`),
classifies suspicious behavior, and pushes decisions to bouncers (Traefik
Badger plugin + host firewall).

- **Image**: `crowdsecurity/crowdsec:latest` ⚠️
- **Compose file**: `stacks/security/docker-compose.yml`
- **Ports**: `6060` (Prometheus metrics), `8080` (LAPI) — both published to
  host
- **Config**: `./config/crowdsec/` (acquis, profiles, parsers)
- **DB**: `./config/crowdsec/db/` (SQLite by default)

## Upstream Sources

- Pangolin-bundled compose: <https://raw.githubusercontent.com/fosrl/pangolin/main/install/config/crowdsec/docker-compose.yml>
- Install docs: <https://docs.crowdsec.net/u/getting_started/install_crowdsec/>
- Traefik integration: <https://docs.pangolin.net/self-host/community-guides/crowdsec>

## Upstream Reference Compose

```yaml
crowdsec:
  image: docker.io/crowdsecurity/crowdsec:latest
  container_name: crowdsec
  environment:
    GID: "1000"
    COLLECTIONS: crowdsecurity/traefik crowdsecurity/appsec-virtual-patching crowdsecurity/appsec-generic-rules
    ENROLL_INSTANCE_NAME: "pangolin-crowdsec"
    PARSERS: crowdsecurity/whitelists
    ENROLL_TAGS: docker
  healthcheck:
    test: [CMD, cscli, lapi, status]
    interval: 10s
    timeout: 5s
    retries: 3
    start_period: 30s
  labels:
    - "traefik.enable=false"
  volumes:
    - ./config/crowdsec:/etc/crowdsec
    - ./config/crowdsec/db:/var/lib/crowdsec/data
    - ./config/traefik/logs:/var/log/traefik:ro
  ports:
    - 6060:6060
  restart: unless-stopped
  command: -t
```

## Our Compose (relevant slice)

```10:47:stacks/security/docker-compose.yml
  crowdsec:
    container_name: crowdsec
    networks:
      - pangolin
    environment:
      ACQUIRE_FILES: /var/log/traefik/*.log
      COLLECTIONS: crowdsecurity/traefik crowdsecurity/appsec-virtual-patching crowdsecurity/appsec-generic-rules
      ENROLL_INSTANCE_NAME: pangolin-crowdsec
      ENROLL_TAGS: docker
      GID: "1000"
      PARSERS: crowdsecurity/whitelists
      CUSTOM_HOSTNAME: "crowdsec"
      DISABLE_ONLINE_API: "${DISABLE_ONLINE_API}"
      DISABLE_HUB_UPDATE: "${DISABLE_HUB_UPDATE}"
    hostname: crowdsec
    expose:
      - 6060
      - 8080
    healthcheck:
      test:
        - CMD
        - cscli
        - lapi
        - status
    image: crowdsecurity/crowdsec:latest
    labels:
      - traefik.enable=false
    ports:
      - 6060:6060
      - 8080:8080
    restart: unless-stopped
    volumes:
      - ../../config/crowdsec:/etc/crowdsec
      - ../../config/crowdsec/db:/var/lib/crowdsec/data
      - /var/log/auth.log:/var/log/auth.log:ro
      - /var/log/syslog:/var/log/syslog:ro
      - ../../config/traefik/logs:/var/log/traefik
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Traefik logs mount | `:ro` | read-write | unintentional drift |
| Healthcheck timing | `10s / 5s / 3 / 30s` | only `test` | unintentional drift |
| `command: -t` (config validation) | yes | no | unintentional drift |
| `8080` host port | not published | published | extra — maybe unnecessary |
| `ACQUIRE_FILES` env | not set (uses `acquis.yaml`) | set (duplicate) | redundant |
| `CUSTOM_HOSTNAME`, `DISABLE_ONLINE_API`, `DISABLE_HUB_UPDATE` | not set | set | intentional for our offline/controlled profile |
| `auth.log` + `syslog` mounts | not in upstream | bound read-only | intentional for host SSH protection |

## Findings

### F-CROWDSEC-1 — Traefik log mount is read-write (`high` / H2)
Path: `../../config/traefik/logs:/var/log/traefik`. CrowdSec only *reads*
Traefik logs. Allowing write means a bug in CrowdSec or a compromised
container could corrupt Traefik's audit log (which, ironically, is also
where our evidence of the compromise would be).

### F-CROWDSEC-2 — Healthcheck lacks timing params (`medium` / M3)
Without `interval`, `timeout`, `retries`, `start_period`, Docker falls back
to implementation defaults. On slow boots CrowdSec may be reported healthy
before the hub sync finishes, or thrash between states.

### F-CROWDSEC-3 — LAPI port `8080` exposed on host (`medium` / M4)
Every bouncer we run lives on the `pangolin` docker network (Traefik-Badger
plugin, crowdsec-web-ui). None of them need to reach CrowdSec over the host
interface. Publishing `8080:8080` broadens attack surface and produces
confusing `iptables` rules.

### F-CROWDSEC-4 — redundant `ACQUIRE_FILES` env (`medium` / M11)
Our `config/crowdsec/acquis.yaml` already defines the Traefik log source.
The `ACQUIRE_FILES` env var causes CrowdSec to generate an extra acquisition
definition on top. Harmless today, confusing tomorrow.

### F-CROWDSEC-5 — no `command: -t` (`low` / L1)
Upstream starts CrowdSec with `-t` which validates all config before
switching to normal run. Without it, a busted parser only surfaces once
CrowdSec is already taking traffic.

## Remediation

### Fix F-CROWDSEC-1

```yaml
      - ../../config/traefik/logs:/var/log/traefik:ro
```

### Fix F-CROWDSEC-2

```yaml
    healthcheck:
      test: ["CMD", "cscli", "lapi", "status"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 30s
```

### Fix F-CROWDSEC-3

Drop `8080:8080` from `ports:` (keep `6060:6060` for Prometheus if you
scrape externally, otherwise drop that too and rely on `expose:`):

```yaml
    ports:
      - 6060:6060
```

### Fix F-CROWDSEC-4

Remove `ACQUIRE_FILES` from `environment:`. Verify
`config/crowdsec/acquis.yaml` still lists the Traefik log path.

### Fix F-CROWDSEC-5

```yaml
    command: ["-t"]
```

Note: `-t` exits after validation; the CrowdSec container's ENTRYPOINT
normally passes it to `crowdsec` as a runtime flag that runs validation
*then* continues. Double-check against the current image's ENTRYPOINT
before committing (Pangolin's upstream uses it without issue).

## Operational Notes

- **Blocklist import**: use `scripts/blocklist-import.sh` on the host — the
  `crowdsec-blocklist-import` container image is broken (docker CLI inside
  container).
- Verify decisions: `docker exec crowdsec cscli decisions list`.
- Bouncer check: `docker exec crowdsec cscli bouncers list`.
- The Traefik Badger plugin is enrolled via `traefik_config.yml`; secret is
  the LAPI key issued by `cscli bouncers add traefik-badger`.
