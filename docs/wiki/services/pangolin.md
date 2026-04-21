---
title: "pangolin"
slug: cloudnode-pangolin
type: service
status: active
tags: ["homelab", "cloudnode", "service", "pangolin"]
aliases: ["pangolin"]
entities:
  primary: cloudnode-pangolin
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/core/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# pangolin

Fossorial Pangolin — control plane, dashboard, API, and database for the
whole stack. All other Fossorial components (Gerbil, Newt, Olm, Badger) read
config from it.

- **Image**: `fosrl/pangolin:1.17.1`
- **Compose file**: `stacks/core/docker-compose.yml`
- **Internal port**: `3001/tcp` (fronted by Traefik at `pangolin.example.com`)
- **Data**: `./config/` (bound into container at `/app/config`, includes
  `db/` with SQLite and `pangolin/config.yml`). Pangolin expects the main
  config at `/app/config/config.yml`; we keep the actual file at
  `config/pangolin/config.yml` and create a symlink at `config/config.yml`
  so the container finds it.

## Upstream Sources

- Reference compose: <https://raw.githubusercontent.com/fosrl/pangolin/main/install/config/docker-compose.yml>
- Docs: <https://docs.pangolin.net/self-host/quick-install>
- Releases: <https://github.com/fosrl/pangolin/releases>

## Upstream Reference Compose

```yaml
pangolin:
  image: docker.io/fosrl/pangolin:{{.PangolinVersion}}
  container_name: pangolin
  restart: unless-stopped
  deploy:
    resources:
      limits:
        memory: 1g
      reservations:
        memory: 256m
  volumes:
    - ./config:/app/config
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:3001/api/v1/"]
    interval: "10s"
    timeout: "10s"
    retries: 15
```

## Our Compose (relevant slice)

```11:28:stacks/core/docker-compose.yml
  pangolin:
    container_name: pangolin
    networks:
      - pangolin
    healthcheck:
      interval: 3s
      retries: 5
      test:
        - CMD
        - curl
        - -f
        - http://localhost:3001/api/v1/
      timeout: 3s
    image: fosrl/pangolin:1.17.1
    restart: unless-stopped
    volumes:
      - ../../config:/app/config
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| Version | templated (latest supported) | pinned `1.17.1` | Aligns with Newt 1.11.x, Olm 1.4.4 (per `AGENTS.md`) — ✓ |
| `deploy.resources` | `limits: 1g`, `reservations: 256m` | none | unintentional drift |
| Healthcheck timing | 10s / 10s / 15 | 3s / 3s / 5 | aggressive; more CPU churn |
| Network | `default` renamed `pangolin` | explicit `pangolin` | equivalent |

## Findings

### F-PANGOLIN-1 — no memory limits (`medium` / M1)
Without `deploy.resources.limits`, a runaway pangolin process (e.g. leaking
on a bad websocket loop) can starve other core containers. Upstream
explicitly sets both a limit and a reservation.

### F-PANGOLIN-2 — aggressive healthcheck timing (`low`)
`interval: 3s` means Docker runs `curl` 20x/minute. Across a stack that's a
lot of wake-ups. Upstream uses `10s` which is more than responsive enough for
orchestration (`depends_on: service_healthy` still only waits seconds).

### F-PANGOLIN-3 — config file path mismatch (`low`)
Pangolin expects its config at `/app/config/config.yml` inside the container.
We organize config under `config/pangolin/config.yml` for clarity. If the
symlink `config/config.yml → pangolin/config.yml` is missing, Pangolin crashes
on startup with "No configuration file found." This happened during a
`git-filter-repo` purge that removed the symlink.

## Remediation

### Fix F-PANGOLIN-1

```yaml
  pangolin:
    ...
    deploy:
      resources:
        limits:
          memory: 1g
        reservations:
          memory: 256m
```

### Fix F-PANGOLIN-2

```yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/api/v1/"]
      interval: 10s
      timeout: 10s
      retries: 15
```

### Fix F-PANGOLIN-3

Ensure the symlink exists in the working tree:

```bash
ln -s pangolin/config.yml config/config.yml
```

Or adjust the compose volume to mount `config/pangolin` directly to
`/app/config` if no other files are needed from `config/`.

```yaml
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3001/api/v1/"]
      interval: 10s
      timeout: 10s
      retries: 15
```

## Upgrade Notes

- When bumping the pin, read
  <https://github.com/fosrl/pangolin/releases> *and*
  <https://docs.pangolin.net/self-host/how-to-update> first.
- Pangolin 1.17.x ↔ Newt 1.11.x ↔ Olm 1.4.4 — keep this triplet in lockstep.
- Backup `config/db/` before every upgrade (`./backup.sh`).
