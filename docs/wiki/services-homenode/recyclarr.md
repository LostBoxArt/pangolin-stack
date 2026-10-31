---
title: "recyclarr"
slug: homenode-recyclarr
type: service
status: active
tags: ["homelab", "homenode", "service", "recyclarr"]
aliases: ["recyclarr"]
entities:
  primary: homenode-recyclarr
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/config/recyclarr/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# recyclarr

Recyclarr applies configured quality profiles and custom formats to Sonarr and
Radarr. The verified deployment pins `ghcr.io/recyclarr/recyclarr:8.8.1`.
It runs as `1000:1000`, mounts `/volume1/docker/config/recyclarr:/config`, joins
`traefik_traefik`, and retains its existing daily schedule and timezone.

## Current source (2026-10-27)

The live definition is `/volume1/docker/config/recyclarr/docker-compose.yml`.
- **Tracked copy**: `host-configs/homenode/recyclarr/docker-compose.yml` (sanitized live snapshot, 2026-10-31)
The tracked repository copy matches the live `8.8.1` pin; preserve it during unrelated edits.

The upstream Docker documentation explains major/minor/exact-version tags and
migration checks. Keep the tested exact pin during unrelated maintenance. Review
release and upgrade notes before changing it.

## Verification and scope

```bash
docker inspect recyclarr --format '{{.State.Status}} {{.Config.Image}}'
```

Expected: running with the intended image. The scheduled container has no HTTP
health endpoint; process availability does not establish that its last sync
succeeded. Inspect the existing sync logs for that separate question.

Do not run a sync as a backup or availability test: it writes Sonarr/Radarr
configuration. Preserve the division of profile/custom-format ownership between
Recyclarr and [Profilarr](./profilarr.md) to avoid conflicting writers.

## Upstream sources

- [Official Docker installation and version tags](https://recyclarr.dev/guide/installation/docker/)
- [Configuration reference](https://recyclarr.dev/guide/configuration/)
- [Source and releases](https://github.com/recyclarr/recyclarr)
