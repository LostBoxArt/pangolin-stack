---
title: "linkstack"
slug: cloudnode-linkstack
type: service
status: active
tags: ["homelab", "cloudnode", "service", "linkstack"]
aliases: ["linkstack"]
entities:
  primary: cloudnode-linkstack
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/apps/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# linkstack

Self-hosted Linktree replacement — single-page "all my links" landing page
at the apex `example.com`.

- **Image**: `linkstackorg/linkstack:latest` ⚠️
- **Compose file**: `stacks/apps/docker-compose.yml`
- **Internal port**: `80` (Traefik-fronted)
- **Data**: external Docker volume `linkstack_linkstack_data` → `/htdocs`
  (SQLite-backed, no external DB)
- **TZ**: `Asia/Jerusalem`

## Upstream Sources

- Reference compose: <https://raw.githubusercontent.com/LinkStackOrg/linkstack-docker/main/docker-compose.yml>
- Docs: <https://docs.linkstack.org/docker/setup/>
- Releases: <https://hub.docker.com/r/linkstackorg/linkstack/tags>

## Upstream Reference Compose

```yaml
services:
  linkstack:
    hostname: 'linkstack'
    image: 'linkstackorg/linkstack:latest'
    environment:
      TZ: 'Europe/Berlin'
      SERVER_ADMIN: 'admin@example.com'
      HTTP_SERVER_NAME: 'example.com'
      HTTPS_SERVER_NAME: 'example.com'
      LOG_LEVEL: 'info'
      PHP_MEMORY_LIMIT: '256M'
      UPLOAD_MAX_FILESIZE: '8M'
    volumes:
      - '/htdocs'
    ports:
      - '8080:80'
      - '8081:443'
    restart: unless-stopped
    user: apache:apache
    depends_on:
      - mysql
    links:
      - mysql
  mysql:
    image: mysql:8
    environment:
      MYSQL_ROOT_PASSWORD: xeFgUGb5mPPn5q2d
```

Upstream assumes MySQL. LinkStack *also* supports SQLite out of the box,
which is what we use to keep the stack lighter.

## Our Compose (relevant slice)

```11:35:stacks/apps/docker-compose.yml
  linkstack:
    image: linkstackorg/linkstack:latest
    container_name: linkstack
    networks:
      - pangolin
    restart: unless-stopped
    group_add:
      - "986"  # docker group
    environment:
      - HTTP_SERVER_NAME=example.com
      - HTTPS_SERVER_NAME=example.com
      - LOG_LEVEL=info
      - PHP_MEMORY_LIMIT=256M
      - UPLOAD_MAX_FILESIZE=8M
      - TZ=Asia/Jerusalem
      - SERVER_ADMIN=admin@example.com
    volumes:
      - linkstack_data:/htdocs
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.linkstack.rule=Host(`example.com`)"
      - "traefik.http.routers.linkstack.entrypoints=websecure"
      - "traefik.http.routers.linkstack.tls.certresolver=letsencrypt"
      - "traefik.http.routers.linkstack.middlewares=geoblock@file,security-headers@file"
      - "traefik.http.services.linkstack.loadbalancer.server.port=80"
```

And:

```55:58:stacks/apps/docker-compose.yml
volumes:
  linkstack_data:
    external: true
    name: linkstack_linkstack_data
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| DB | MySQL sidecar | SQLite (bundled) | ✓ intentional — lighter |
| `user: apache:apache` | set | not set | unintentional — defaults to root inside container |
| `group_add: 986` | not in upstream | set | questionable — see F-LINKSTACK-2 |
| `:latest` image tag | upstream ships `:latest` | same | drift risk |
| Port publish | `8080:80`, `8081:443` | not published | ✓ Traefik-fronted |
| Volume | named (bind path in upstream) | external named volume `linkstack_linkstack_data` | intentional — pre-existing data from an older compose iteration |

## Findings

### F-LINKSTACK-1 — runs as root (`medium` / M7)
Without `user: apache:apache`, the PHP/Apache processes inside the container
run as root. Upstream defaults to the `apache` user for defense in depth; we
should too. A filesystem-write vuln in the PHP app becomes kernel-level only
when the container is compromised *and* escapes to the host, but it's a free
layer of hardening.

### F-LINKSTACK-2 — `group_add: 986` of dubious value
The Docker GID is added to the container. LinkStack has no Docker-related
feature, does not bind docker.sock, and has no GPU needs. This
`group_add` looks copy-pasted from dashdot/dockhand and should simply be
dropped.

### F-LINKSTACK-3 — `:latest` image tag (`medium` / M10 scope)
Pick a release from <https://hub.docker.com/r/linkstackorg/linkstack/tags>
and pin.

### F-LINKSTACK-4 — no healthcheck (`low` / L4)
Apache serves `/` always; a simple probe is sufficient.

## Remediation

### Fix F-LINKSTACK-1 + F-LINKSTACK-2

```yaml
    user: apache:apache
    # remove: group_add
```

After switching `user`, verify write access to `/htdocs` — if LinkStack
complains about permissions, the volume contents may be owned by `root`
from the previous startup. Fix once with:

```bash
docker run --rm -v linkstack_linkstack_data:/htdocs alpine \
  chown -R 33:33 /htdocs
```

(`33:33` is typically `www-data`; inside this image it's `apache:apache` —
check `docker exec linkstack id apache` for the actual UID/GID.)

### Fix F-LINKSTACK-3

```yaml
    image: linkstackorg/linkstack:v4.x.x
```

### Fix F-LINKSTACK-4

```yaml
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/"]
      interval: 1m
      timeout: 10s
      retries: 3
      start_period: 60s
```

## Operational Notes

- The external volume is named `linkstack_linkstack_data` (double-prefix is
  a hangover from when we had a separate stack). **Do not `docker volume rm`
  without a full backup** — losing it loses the site.
- Config lives inside the volume at `/htdocs/.env` and `/htdocs/database/`.
- Default admin account is created through the first-run web wizard.
