---
title: "HomeNode media stack audit — 2026-09-05"
slug: homenode-media-stack-audit-2026-09-05
type: audit
status: current
tags: ["homelab", "homenode", "media", "audit"]
aliases: ["media stack audit"]
entities:
  primary: homenode-media-stack-audit-2026-09-05
  mentions: ["homenode-sonarr", "homenode-radarr", "homenode-qbittorrent", "homenode-plex"]
related: ["sonarr.md", "radarr.md", "qbittorrent.md", "plex.md", "recyclarr.md", "profilarr.md"]
sources: ["live Sonarr/Radarr APIs", "live NASUS Docker inspection"]
confidence: high
audience_level: operator
last_ingested: 2026-09-05
last_lint: 2026-09-05
---
# HomeNode media stack audit — 2026-09-05

## Scope

Read-only live audit plus controlled media-path migration and documentation
work. Plex was deliberately excluded: no Plex files, configuration, container,
or image were changed.

## Completed without interruption

- Added Plex notifications to Sonarr and Radarr through their APIs. Both
  application notification tests returned HTTP 200.
- Extended the existing twice-daily service watchdog to include Profilarr,
  Recyclarr, Cleanuparr, and Qui. A real run completed with exit code 0.
- Added verified Compose definitions to Git for Recyclarr, Profilarr, Cleanuparr,
  and Seerr. Seerr is pinned to the current stable `v3.4.1` and uses the
  preserved `jellyseerr` data directory.
- Added `/data` mounts to qBittorrent, Sonarr, Radarr, and Bazarr while retaining
  legacy aliases. Updated qBittorrent defaults and all 59 Sonarr / 40 Radarr
  library paths through their APIs with file movement disabled.
- Plex was not stopped, recreated, or reconfigured; it remained `running/healthy`
  throughout. qBittorrent retained all 128 torrents.
- The cross-container hardlink canary passed with matching device/inode values.
  No safe unimported real-import canary was available, so no real media item was
  altered.
- Documented the Recyclarr/Profilarr ownership boundary: one setting must have
  one writer, with Recyclarr as the preferred declarative owner.

## Current profile audit

- Sonarr: 59 series — 20 `Any`, 27 profile 6, 12 profile 7.
- Radarr: 40 movies — 3 `Any`, 1 profile 7, 36 profile 8.

The `Any` assignments were intentionally left unchanged. They require a
content-by-content decision, not a bulk replacement.

## Deferred maintenance-window work

- Observe imports, seeding, paths, and service health for 24–48 hours before
  removing the legacy `/tv`, `/movies`, and `/downloads` aliases.
- Run a genuine new-download import canary when one is available; the current
  completed torrents were already imported or could not be matched safely.
- Recreate containers to apply image pinning or healthcheck changes.
- Decide whether to move Prowlarr off `develop` after compatibility testing.
- Review whether Bazarr's stored paths should move from legacy aliases to `/data`
  after the observation period.
