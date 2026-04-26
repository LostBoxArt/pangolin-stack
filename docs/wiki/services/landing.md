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

- `index.html` — full-page markup (topbar, hero, ops panel, field notes, footer)
- `style.css` — all styles (console layout, typography, portrait ring, note rows, responsive, reduced-motion)
- `avatar.jpg` — profile photo
- `logo.png` — favicon / mark
- `DESIGN.md` — design system reference (colors, typography, spacing tokens, component specs)

## Design Features

- **Field notes concept** — the body content is presented as journal-style
  numbered entries (Work, Home, AI/agents, Signals) rather than cards or a
  traditional portfolio grid.
- **Three-tone identity** — "Cloud / Lab / Home" eyebrow breadcrumb mapping
  work, research, and personal stacks.
- **Mixed typography** — Playfair Display serif for the name, Outfit
  sans-serif for body, IBM Plex Mono for labels, tags, and telemetry.
- **Dark technical palette** — near-black `#0d0f0d` background with warm gold
  (`#d5a15f`) accents and a green status dot (`#9ccf92`).
- **Infrastructure-map portrait** — avatar framed inside a panel with
  route lines and node labels (Cloud, HPC, Home) suggesting a network topology.
- **Rotating gold ring** — a conic-gradient ring on a `::before` pseudo-element
  sweeps gold arcs around the portrait border (10s loop). Uses CSS `@property`
  for GPU-friendly angle animation that doesn't rotate the square element.
- **Telemetry rows** — Base, Role, and Stack data displayed as definition-list
  pairs below the portrait.
- **Note rows** — four numbered field notes with a two-column layout:
  numbered index + title on the left, body text + metadata tags on the right.
  Each row has a gold left border accent and subtle gold gradient background.
  Covers: Work (Linux/storage), Home (tunnels/dashboards), AI/agents (local
  models/tool use), and Signals (focus tags).
- **Focus tags as pill labels** — monospace, uppercase, gold-bordered pill
  labels in the Signals note.
- **Primary action buttons** — Email, GitHub, LinkedIn with inline SVG icons.
- **Secondary links** — X and Steam moved to the footer, split layout with
  the status tagline.
- **Responsive** — single-column stack on mobile with ops panel collapsing
  below the identity section. Note rows collapse to single-column.
- **Respects `prefers-reduced-motion`** — disables all animations for users
  who request it.

## Operational Notes

- The site is served read-only (`:ro` bind mount). No container state to
  preserve.
- Cache buster is currently `style.css?v=12`.
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
curl -I https://dennisb.xyz/style.css?v=12
curl -I https://dennisb.xyz/avatar.jpg
curl -I https://dennisb.xyz/logo.png
```

## Migration from LinkStack

LinkStack was replaced on 2026-04-21. See the archived
[linkstack.md](./linkstack.md) page for historical reference.

The landing page received two major redesigns:
- **2026-04-24** (commit `4172993`) — operations console concept with systems cards
- **2026-04-26** (commit `deb6eb9`) — field notes redesign with journal-style entries,
  rotating portrait ring, footer secondary links
