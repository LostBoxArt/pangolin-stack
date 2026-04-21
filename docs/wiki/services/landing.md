---
title: "landing"
slug: cloudnode-landing
type: service
status: active
tags: ["homelab", "cloudnode", "service", "landing", "admin-xyz"]
aliases: ["landing", "example-landing"]
entities:
  primary: cloudnode-landing
  mentions: []
related: ["./README.md", "./system-overview.md", "./linkstack.md"]
sources: ["stacks/apps/docker-compose.yml", "sites/dennisb-landing/"]
confidence: high
audience_level: operator
last_ingested: 2026-04-21
last_lint: 2026-04-21
---

# landing

Custom-built static landing page at the apex `example.com`. Replaces the
previous LinkStack container with a single HTML+CSS page served by nginx.

- **Image**: `nginx:alpine`
- **Compose file**: `stacks/apps/docker-compose.yml`
- **Internal port**: `80` (Traefik-fronted)
- **Data**: bind-mounted site directory `sites/dennisb-landing/` (gitignored; contains
  personal info) → `/usr/share/nginx/html`
- **Container name**: `landing`

## Upstream Sources

None — this is a bespoke static page built in-repo.

## Our Compose (relevant slice)

```yaml:stacks/apps/docker-compose.yml
  landing:
    image: nginx:alpine
    container_name: landing
    networks:
      - pangolin
    restart: unless-stopped
    volumes:
      - ../../sites/dennisb-landing:/usr/share/nginx/html:ro
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.linkstack.rule=Host(`example.com`)"
      - "traefik.http.routers.linkstack.entrypoints=websecure"
      - "traefik.http.routers.linkstack.tls.certresolver=letsencrypt"
      - "traefik.http.routers.linkstack.middlewares=geoblock@file,security-headers@file"
      - "traefik.http.services.linkstack.loadbalancer.server.port=80"
```

Note: Traefik router and service names intentionally kept as `linkstack-*`
so Pangolin continues to route `example.com` without config changes. The
Pangolin SQLite `targets` table row for this resource was updated from
`ip='linkstack'` to `ip='landing'` to point at the new container name.

## Site Files

Located under `sites/dennisb-landing/` (gitignored):

- `index.html` — profile card markup
- `style.css` — all styles (glassmorphism, animations, responsive)
- `avatar.jpg` — profile photo

## Design Features

- **Rotating amber border** — thin conic-gradient border that slowly rotates
  around the card (10s cycle, soft opacity)
- **Mouse-tracking spotlight** — radial amber glow follows cursor inside the
  card on desktop; disabled on touch devices
- **Mesh gradient background** — three large soft blobs (amber, purple, pink)
  that drift at different speeds
- **Text shimmer** — slow warm highlight sweeps across "Admin B." every 6s
- **Enhanced glassmorphism** — increased backdrop blur, inner top-edge
  highlight, soft inner glow
- **Staggered fade-up entrance animations** on all card elements
- **3+2 social link grid** — fixed-width pill buttons: Email, LinkedIn,
  GitHub on top row; X, Steam on bottom row

## Operational Notes

- The site is served read-only (`:ro` bind mount). No container state to
  preserve.
- To update: edit files in `sites/dennisb-landing/`, bump the `?v=N`
  cache-buster in `index.html`, and reload nginx inside the container:
  `docker exec landing nginx -s reload`.
- The old `linkstack_linkstack_data` external Docker volume still exists
  on the host as a safety precaution; it can be removed once confirmed
  unnecessary.
- Pangolin DB was manually edited to update the `targets.ip` field from
  `linkstack` to `landing` for `resourceId=1`. If Pangolin is ever
  re-initialized, this may need to be re-done.

## Migration from LinkStack

LinkStack was replaced on 2026-04-21. See the archived
[linkstack.md](./linkstack.md) page for historical reference.
