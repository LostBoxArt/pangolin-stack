---
title: "crowdsec-web-ui"
slug: cloudnode-crowdsec-web-ui
type: service
status: active
tags: ["homelab", "cloudnode", "service", "crowdsec-web-ui"]
aliases: ["crowdsec-web-ui"]
entities:
  primary: cloudnode-crowdsec-web-ui
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/security/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-23
last_lint: 2026-10-23
---
# crowdsec-web-ui

Web admin UI for CrowdSec decisions / alerts / bouncers. Third-party image
(not shipped by CrowdSec team).

- **Image**: `ghcr.io/theduffman85/crowdsec-web-ui:2026.10.9` (live-verified 2026-10-23)
- **Compose file**: `stacks/security/docker-compose.yml`
- **Host port**: `3458:3000` (direct local access; keep filtered)
- **Public route**: Pangolin-fronted `crowdsec.example.com` with SSO
- **Data**: `./config/crowdsec-web-ui/` bound at `/app/data`; the container runs as UID/GID `1001:1001` to preserve owner-only host permissions

## Upstream Sources

- Image repo: <https://github.com/duffman85/crowdsec-web-ui>
- GHCR: <https://ghcr.io/theduffman85/crowdsec-web-ui>

There's no officially supported upstream compose reference — the image's
README is the only documentation.

## Our Compose (relevant slice)

```53:71:stacks/security/docker-compose.yml
  crowdsec-web-ui:
    image: ghcr.io/theduffman85/crowdsec-web-ui:2026.10.9
    container_name: crowdsec-web-ui
    user: "1001:1001"
    networks:
      - pangolin
    restart: unless-stopped
    ports:
      - "3458:3000"
    depends_on:
      crowdsec:
        condition: service_healthy
    environment:
      CROWDSEC_URL: http://crowdsec:8080
      CROWDSEC_USER: crowdsec-web-ui
      CROWDSEC_PASSWORD: ${CROWDSEC_WEB_UI_PASSWORD}
    volumes:
      - ../../config/crowdsec-web-ui:/app/data
```

## Deviations

Release `2026.10.3` migrated the persistent state layout from `/app/config` to
`/app/data`. The current `2026.10.9` image retains that layout; the deployment
keeps the state directory owner-only and runs as UID/GID `1001:1001` so the host
account and watchdog can still read the tracked configuration. The current
container was healthy with zero restarts on 2026-10-23.

## Findings

### F-CSWUI-1 — direct host port remains a defense-in-depth risk (`low`)
The public route is fronted by Pangolin and SSO, but `3458:3000` is still
published directly on the host without TLS. Keep the host port filtered and do
not treat the public SSO route as a substitute for application authentication.

### F-CSWUI-2 — credential in-plaintext in env (acceptable)
`CROWDSEC_PASSWORD=${CROWDSEC_WEB_UI_PASSWORD}` sourced from `.env`. No fix
needed — this is the standard pattern; `.env` is not committed.

### F-CSWUI-3 — application auth disabled (`medium`, pre-existing 2026-09-28)
`GET /api/auth/status` reports `{"authEnabled":false,...}` and `auth_users` has 0
rows. Upstream's README says auth must be enabled *explicitly* on installations
migrated from older releases. This UI can create and delete CrowdSec bans, so the
app-level auth is a real control, not decoration. Currently masked because the
Pangolin resource `crowdsec.example.com` enforces SSO (unauthenticated requests
get 401/302) and host port 3458 is filtered from the internet. Enable app auth
before relying on either of those to hold.

### F-CSWUI-4 — 1.8 GB state directory with permissive modes (`low`, 2026-09-28)
`config/crowdsec-web-ui/` is `drwx-xrwx` and its files are `-rw-r--rw-`
(world-readable, group-writable). It holds `crowdsec.db` (1.4 GB) plus a 455 MB
WAL. Tighten to `0700`/`0600` and check whether the DB size is expected.

## Remediation

### Optional — Fix F-CSWUI-1

Drop the `3458:3000` host publish and add Traefik labels pointing at a
`cswui.example.com` (or sub-path) hostname with Pocket-ID auth:

```yaml
  crowdsec-web-ui:
    ...
    # no ports
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.cswui.rule=Host(`crowdsec-ui.example.com`)"
      - "traefik.http.routers.cswui.entrypoints=websecure"
      - "traefik.http.routers.cswui.tls.certresolver=letsencrypt"
      - "traefik.http.routers.cswui.middlewares=security-headers@file"
      - "traefik.http.services.cswui.loadbalancer.server.port=3000"
```

Only useful if Pocket-ID-gated admin UIs is a desired pattern for you.

## Operational Notes

- The LAPI user used here (`crowdsec-web-ui`) must be registered:
  `docker exec -it crowdsec cscli machines add crowdsec-web-ui --auto`.
- Resetting the UI DB: stop stack, delete
  `config/crowdsec-web-ui/users.db`, restart — you'll get the
  first-run wizard again.
