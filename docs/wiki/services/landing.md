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

- `index.html` — full-page markup (hero, body blocks, footer)
- `style.css` — all styles (grid, typography, animations, responsive)
- `avatar.jpg` — profile photo

## Design Features

- **Full-page layout** — content spans the viewport, not a centered card.
  Asymmetric hero with large serif typography left, large photo right.
- **Structural grid lines** — faint vertical and horizontal guide lines at
  key proportions (8.33%, 25%, 50%, 75%, 91.66%) for an architectural feel.
- **Film-grain noise overlay** — subtle SVG noise texture at 3% opacity for
  depth and atmosphere.
- **Editorial typography** — Cormorant Garamond serif for the name, Outfit
  sans-serif for body text. No Inter, no Roboto.
- **Warm industrial palette** — near-black `#0c0c0c` background with copper
  `#c4956a` accents. Not the default dark-mode blue-purple.
- **Rotating amber border** — conic-gradient ring around the avatar (10s loop).
- **Pulsing glow behind avatar** — soft radial gradient that breathes.
- **Staggered entrance animations** — content blocks fade up in sequence on load.
- **3+2 centered link grid** — Email, LinkedIn, GitHub top row; X, Steam
  centered below.
- **Corner brackets** — minimal L-shaped framing elements top-left and
  bottom-right.
- **Responsive** — single-column stack on mobile with photo moved above name.
- **Respects `prefers-reduced-motion`** — disables all animations for users
  who request it.

## Operational Notes

- The site is served read-only (`:ro` bind mount). No container state to
  preserve.
- To update: edit files in `sites/dennisb-landing/` and reload nginx:
  `docker exec landing nginx -s reload`.
- Design follows the "frontend-design" Anthropic skill principles:
  bold aesthetic direction, distinctive typography, intentional spatial
  composition, and avoiding generic "AI slop" aesthetics.
- The old `linkstack_linkstack_data` external Docker volume still exists
  on the host as a safety precaution; it can be removed once confirmed
  unnecessary.
- Pangolin DB was manually edited to update the `targets.ip` field from
  `linkstack` to `landing` for `resourceId=1`. If Pangolin is ever
  re-initialized, this may need to be re-done.

## Migration from LinkStack

LinkStack was replaced on 2026-04-21. See the archived
[linkstack.md](./linkstack.md) page for historical reference.
