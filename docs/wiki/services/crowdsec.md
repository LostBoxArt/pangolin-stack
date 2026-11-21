---
title: "crowdsec"
slug: cloudnode-crowdsec
type: service
status: active
tags: ["homelab", "cloudnode", "service", "crowdsec"]
aliases: ["crowdsec"]
entities:
  primary: cloudnode-crowdsec
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/security/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-04-17
---
# crowdsec

IDS/IPS that reads Traefik's access log (and host `auth.log`/`syslog`),
classifies suspicious behavior, and pushes decisions to bouncers (Traefik
Badger plugin + host firewall).

- **Image**: `crowdsecurity/crowdsec:latest` ⚠️
- **Compose file**: `stacks/security/docker-compose.yml`
- **Ports**: `6060` (Prometheus metrics), `8080` (LAPI) — published to host loopback only. The host firewall bouncer uses `http://127.0.0.1:8080/`; container clients use `crowdsec:8080`.
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
      COLLECTIONS: crowdsecurity/traefik crowdsecurity/appsec-virtual-patching crowdsecurity/appsec-generic-rules crowdsecurity/linux
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
      - "127.0.0.1:6060:6060"
      - "127.0.0.1:8080:8080"
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
| `command: -t` (config validation) | shown in older reference | not configured | validate explicitly before deployment |
| `8080` host port | not published | loopback only | required by the host firewall bouncer |
| `ACQUIRE_FILES` env | not set (uses `acquis.yaml`) | set (duplicate) | redundant |
| `CUSTOM_HOSTNAME`, `DISABLE_ONLINE_API`, `DISABLE_HUB_UPDATE` | not set | set | operator environment; preserve its current update policy |
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

### F-CROWDSEC-3 — LAPI host publication restricted (resolved 2026-10-27)
The host firewall bouncer requires `127.0.0.1:8080`; Traefik and the Web UI use Docker networking. Both host ports now bind only to loopback, preserving these consumers.

### F-CROWDSEC-4 — redundant `ACQUIRE_FILES` env (`medium` / M11)
Our `config/crowdsec/acquis.yaml` already defines the Traefik log source.
The `ACQUIRE_FILES` env var causes CrowdSec to generate an extra acquisition
definition on top. Harmless today, confusing tomorrow.

### F-CROWDSEC-5 — explicit configuration validation
Use `docker exec crowdsec crowdsec -t` before restarting the service. In the verified 1.8.1 image, the Docker entrypoint builds its daemon arguments from environment variables and does not use `command: -t` as a validation gate.

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

Keep the host firewall bouncer's loopback endpoint:

```yaml
    ports:
      - "127.0.0.1:6060:6060"
      - "127.0.0.1:8080:8080"
```

### Fix F-CROWDSEC-4

Remove `ACQUIRE_FILES` from `environment:`. Verify
`config/crowdsec/acquis.yaml` still lists the Traefik log path.

### Fix F-CROWDSEC-5

```bash
docker exec crowdsec crowdsec -t
```

The standalone command exits after validation. Keep normal daemon startup enabled. See the [1.8.1 entrypoint](https://github.com/crowdsecurity/crowdsec/blob/v1.8.1/build/docker/docker_start.sh).

## Verified SSH repair (2026-10-27)

Existing SSH detection was functioning. A targeted `cscli collections install crowdsecurity/sshd` restored the missing collection, `ssh-time-based-bf` scenario, and `sshd-success-logs` parser without `--force`. Configuration validation passed; `linux` and `sshd` are enabled without taint, custom rules were unchanged, and both firewall and Traefik bouncers authenticated afterward.

Only those three YAML files changed during the repair. Container recreations used the cached image and `NO_HUB_UPGRADE=true` for this maintenance to prevent unrelated hub upgrades. The final container references only the primary security Compose file; the private temporary override is no longer needed by Docker.

The primary Compose file contains no `NO_HUB_UPGRADE` setting. Its existing `DISABLE_HUB_UPDATE=false` policy is preserved. The running maintenance container retains `NO_HUB_UPGRADE=true` until the next normal deployment. For a reviewed update, back up the CrowdSec config, inspect the intended hub changes, validate with `crowdsec -t`, and recreate CrowdSec using the primary file alone. That deployment resumes the existing automatic hub policy. Do not make the maintenance freeze permanent accidentally.

```bash
cd /home/jesus/pangolin-stack
docker exec crowdsec crowdsec -t
docker compose -f stacks/security/docker-compose.yml --env-file .env up -d --no-deps --pull never --wait --wait-timeout 120 crowdsec
docker exec crowdsec crowdsec -t
docker exec crowdsec cscli metrics show lapi-bouncer
```

Keep the config backup until rules, bouncers and ingress are verified. A rollback restores that saved config and recreates the same cached image with a one-maintenance `NO_HUB_UPGRADE=true` guard; it must not trigger an unreviewed rule upgrade while restoring.

A bouncer's `last_pull` age alone is insufficient evidence that it is unused: Traefik's live lookup/cache mode produced authenticated `/v1/decisions` metrics despite an older timestamp, while the host firewall used `/v1/decisions/stream`. Neither active bouncer was deleted.

## Operational Notes

- **Blocklist import**: use `scripts/blocklist-import.sh` on the host — the
  `crowdsec-blocklist-import` container image is broken (docker CLI inside
  container).
- Verify decisions: `docker exec crowdsec cscli decisions list`.
- Bouncer check: `docker exec crowdsec cscli bouncers list`.
- The Traefik Badger plugin is enrolled via `traefik_config.yml`; secret is
  the LAPI key issued by `cscli bouncers add traefik-badger`.
