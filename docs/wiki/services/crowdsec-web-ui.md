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
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# crowdsec-web-ui

Web admin UI for CrowdSec decisions / alerts / bouncers. Third-party image
(not shipped by CrowdSec team).

- **Image**: `ghcr.io/theduffman85/crowdsec-web-ui:2026.3.1` (pinned)
- **Compose file**: `stacks/security/docker-compose.yml`
- **Exposed**: `3458:3000` on the host (direct, not fronted by Traefik)
- **Data**: `./config/crowdsec-web-ui/` bound at `/app/config`

## Upstream Sources

- Image repo: <https://github.com/duffman85/crowdsec-web-ui>
- GHCR: <https://ghcr.io/theduffman85/crowdsec-web-ui>

There's no officially supported upstream compose reference — the image's
README is the only documentation.

## Our Compose (relevant slice)

```53:71:stacks/security/docker-compose.yml
  crowdsec-web-ui:
    image: ghcr.io/theduffman85/crowdsec-web-ui:2026.3.1
    container_name: crowdsec-web-ui
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
      DB_DIR: /app/config
    volumes:
      - ../../config/crowdsec-web-ui:/app/config
```

## Deviations

No upstream to compare against. The pin (`2026.3.1`) is explicitly documented
in `AGENTS.md` because the moving `latest` tag shipped a broken image on
2026-03-30.

## Findings

### F-CSWUI-1 — not behind Traefik (`low`)
Exposed on `3458:3000` directly to the host interface, no TLS, no auth beyond
the CrowdSec LAPI credentials. Acceptable for a CloudNode-admin tool reached over
SSH tunnel, but if an operator ever opens the host firewall for port 3458,
the UI is available unauthenticated at HTTP on the public interface.

### F-CSWUI-2 — credential in-plaintext in env (acceptable)
`CROWDSEC_PASSWORD=${CROWDSEC_WEB_UI_PASSWORD}` sourced from `.env`. No fix
needed — this is the standard pattern; `.env` is not committed.

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
