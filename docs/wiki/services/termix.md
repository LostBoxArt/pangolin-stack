---
title: "termix"
slug: vps-termix
type: service
status: active
tags: ["homelab", "vps", "service", "termix"]
aliases: ["termix"]
entities:
  primary: vps-termix
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/apps/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# termix

Web-based SSH terminal / tunneling / file editor at `termix.dennisb.xyz`.

- **Image**: `ghcr.io/lukegus/termix:latest` ⚠️
- **Compose file**: `stacks/apps/docker-compose.yml`
- **Internal port**: `8080` (Traefik-fronted)
- **Data**: named volume `termix_data` → `/app/data`

## Upstream Sources

- Reference compose: <https://docs.termix.site/install/server/docker>
- Repo: <https://github.com/LukeGus/Termix>
- Releases: <https://github.com/Termix-SSH/Termix/releases>

## Upstream Reference Compose

```yaml
services:
  termix:
    image: ghcr.io/lukegus/termix:latest
    container_name: termix
    restart: unless-stopped
    ports:
      - '8080:8080'
    volumes:
      - termix-data:/app/data
    environment:
      PORT: '8080'
    depends_on:
      - guacd
    networks:
      - termix-net

  guacd:
    image: guacamole/guacd:latest
    container_name: guacd
    restart: unless-stopped
    ports:
      - "4822:4822"
    networks:
      - termix-net

volumes:
  termix-data:
    driver: local

networks:
  termix-net:
    driver: bridge
```

Key detail: upstream ships a **`guacd` sidecar** for RDP/VNC tunneling. We
don't include it.

## Our Compose (relevant slice)

```37:53:stacks/apps/docker-compose.yml
  termix:
    image: ghcr.io/lukegus/termix:latest
    container_name: termix
    networks:
      - pangolin
    restart: unless-stopped
    volumes:
      - termix_data:/app/data
    environment:
      - PORT=8080
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.termix.rule=Host(`termix.dennisb.xyz`)"
      - "traefik.http.routers.termix.entrypoints=websecure"
      - "traefik.http.routers.termix.tls.certresolver=letsencrypt"
      - "traefik.http.routers.termix.middlewares=geoblock@file,security-headers@file"
      - "traefik.http.services.termix.loadbalancer.server.port=8080"
```

And:

```60:62:stacks/apps/docker-compose.yml
  termix_data:
    driver: local
```

## Deviations

| Aspect | Upstream | Ours | Intent |
|---|---|---|---|
| `guacd` sidecar | present | **absent** | SSH-only for us; no RDP/VNC |
| `depends_on: guacd` | yes | n/a | consequence of the above |
| `:latest` tag | yes | yes | drift risk |
| Port publish | `8080:8080` | not published | ✓ Traefik-fronted |
| Network | `termix-net` | `pangolin` (shared) | intentional — Traefik needs to reach it |
| Volume name | `termix-data` | `termix_data` | cosmetic |

## Findings

### F-TERMIX-1 — no `guacd` sidecar (`medium` / M8)
If someone tries to add an RDP/VNC connection in the Termix UI, it will
fail with a cryptic "guacd unreachable" error. We currently only use SSH,
so this is intentional drift, but worth documenting so it's not a mystery
later.

### F-TERMIX-2 — `:latest` image tag (`medium` / M10 scope)
Termix is under very active development. Pin a release from
<https://github.com/Termix-SSH/Termix/releases>.

### F-TERMIX-3 — no healthcheck (`low` / L4)
Termix exposes `/`; a simple probe suffices.

## Remediation

### Fix F-TERMIX-1 (only if you want RDP/VNC)

Add alongside the termix service:

```yaml
  guacd:
    image: guacamole/guacd:latest
    container_name: guacd
    networks:
      - pangolin
    restart: unless-stopped
```

Then:

```yaml
  termix:
    depends_on:
      - guacd
```

No ports needed — Termix talks to guacd over the `pangolin` network on
`4822/tcp` internally.

### Fix F-TERMIX-2

```yaml
    image: ghcr.io/lukegus/termix:vX.Y.Z
```

Pin the same version you tested locally. Image changes on patch releases
occasionally require re-initialization of stored SSH host keys.

### Fix F-TERMIX-3

```yaml
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8080/"]
      interval: 1m
      timeout: 10s
      retries: 3
      start_period: 30s
```

## Operational Notes

- SSH host keys and saved credentials are encrypted at rest in
  `termix_data`. Losing that volume loses the saved connection list.
- `:8080/api/health` may be added in newer builds — check changelog before
  hard-coding a health path.
- Docker-Hub mirror is available as `bugattiguy527/termix:latest` if GHCR
  rate limits become a problem.
