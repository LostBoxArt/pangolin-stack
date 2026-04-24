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
last_ingested: 2026-04-24
last_lint: 2026-04-24
---

# landing

Custom-built static landing page at the apex `example.com`. Replaces the
previous LinkStack container with a bespoke HTML+CSS page served by nginx.

- **Image**: `nginx:alpine`
- **Compose file**: `stacks/apps/docker-compose.yml`
- **Internal port**: `80` (Traefik-fronted)
- **Data**: bind-mounted site directory `sites/dennisb-landing/` (tracked in git)
  → `/usr/share/nginx/html`
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

Located under `sites/dennisb-landing/` (all tracked in git):

- `index.html` — full-page markup (topbar, hero, ops panel, systems cards, footer)
- `style.css` — all styles (console layout, typography, responsive, reduced-motion)
- `avatar.jpg` — profile photo
- `logo.png` — favicon / mark (optimized to ~119 KB)
- `DESIGN.md` — design system reference (colors, typography, spacing tokens)

## Design Features

- **Operations console concept** — presents the page as an infrastructure
  operator profile rather than a traditional portfolio.
- **Three-tone identity** — "Cloud / Lab / Home" eyebrow breadcrumb mapping
  work, research, and personal stacks.
- **Mixed typography** — Playfair Display serif for the name, Outfit
  sans-serif for body, IBM Plex Mono for labels and telemetry.
- **Dark technical palette** — near-black `#0d0f0d` background with warm gold
  `#c9a96e` accents and a green status dot.
- **Infrastructure-map portrait** — avatar framed inside a panel with
  route lines and node labels (Cloud, HPC, Home) suggesting a network topology.
- **Telemetry rows** — Base, Role, and Stack data displayed as definition-list
  pairs below the portrait.
- **Systems cards** — six numbered cards (01-06) covering Operating Principle,
  Day Work, Night Work, Focus tags, Elsewhere links, and Current Focus.
- **AI hobbies surfaced explicitly** — "local models, tool-using agents,
  coding assistants, agent workflows" called out in the Current Focus card.
- **Primary action buttons** — Email, GitHub, LinkedIn with inline SVG icons.
- **Secondary links** — X and Steam in a dedicated Elsewhere card.
- **Responsive** — single-column stack on mobile with ops panel collapsing
  below the identity section.
- **Respects `prefers-reduced-motion`** — disables entrance animations for
  users who request it.

## Operational Notes

- The site is served read-only (`:ro` bind mount). No container state to
  preserve.
- Cache buster is currently `style.css?v=9`.
- To update: edit files in `sites/dennisb-landing/`, commit, push, then reload
  nginx on the live host:
  `docker exec landing nginx -s reload`.
- The old `linkstack_linkstack_data` external Docker volume still exists
  on the host as a safety precaution; it can be removed once confirmed
  unnecessary.
- Pangolin DB was manually edited to update the `targets.ip` field from
  `linkstack` to `landing` for `resourceId=1`. If Pangolin is ever
  re-initialized, this may need to be re-done.

## Deployment Steps

After pulling the latest repo state on the deployment host:

```bash
git pull --ff-only
docker exec landing nginx -s reload
```

If the container is not running or the mount/path changed, recreate:

```bash
docker compose -f stacks/apps/docker-compose.yml --env-file .env up -d landing
```

Verify:

```bash
curl -I https://dennisb.xyz
curl -I https://dennisb.xyz/style.css?v=9
curl -I https://dennisb.xyz/avatar.jpg
curl -I https://dennisb.xyz/logo.png
```

## Migration from LinkStack

LinkStack was replaced on 2026-04-21. See the archived
[linkstack.md](./linkstack.md) page for historical reference.

The page received a full visual redesign on 2026-04-24 (commit `4172993`)
from a dark editorial aesthetic into the current operations console concept.
