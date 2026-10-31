---
title: "seerr"
slug: homenode-seerr
type: service
status: active
tags: ["homelab", "homenode", "service", "seerr"]
aliases: ["seerr"]
entities:
  primary: homenode-seerr
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/seerr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-10-27
---
# seerr

Seerr manages media requests and connects to Sonarr, Radarr, and the media server.
The verified deployment uses `ghcr.io/seerr-team/seerr:v3.5.1`; this maintenance
performed no Seerr upgrade or migration.

## Current source (2026-10-27)

The live definition is `/volume1/docker/config/seerr/docker-compose.yml` and its
sanitized copy is `host-configs/homenode/seerr/docker-compose.yml`. It retains
UID/GID 1000, `init`, `no-new-privileges`, memory limits, the existing status
healthcheck, and `traefik_traefik` connectivity.

The data bind remains `/volume1/docker/config/jellyseerr:/app/config`.
That historical directory name is not an unused installation: it contains the
active Seerr data. Preserve it in backup discovery. Do not rename or delete it
merely to match the service name, and do not switch back to a different image
based on the older wiki's unsupported fork/downgrade recommendation.

Docker labels route `request.example.com` to port 5055. The duplicate NAS file
route was removed after verifying the label router; the expected public redirect
was preserved. See [NAS Traefik](./traefik.md).

## Verify safely

```bash
docker inspect seerr --format '{{.State.Status}} {{.State.Health.Status}}'
docker exec seerr wget --no-verbose --tries=1 --spider http://localhost:5055/api/v1/status
```

Expected: running/healthy and a successful native status request. Read-only
service verification also authenticated successfully. Do not submit media
requests or approvals to test availability: they can create downloads and send
notifications.

## Upstream sources

- [Seerr source and image project](https://github.com/seerr-team/seerr)
- [Seerr documentation](https://docs.seerr.dev/)
