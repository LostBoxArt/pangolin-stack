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

Read-only live audit plus interruption-free configuration and documentation
work. No media files, application databases, torrent paths, containers, or
images were changed.

## Completed without interruption

- Added Plex notifications to Sonarr and Radarr through their APIs. Both
  application notification tests returned HTTP 200.
- Extended the existing twice-daily service watchdog to include Profilarr,
  Recyclarr, Cleanuparr, and Qui. A real run completed with exit code 0.
- Added verified Compose definitions to Git for Recyclarr, Profilarr, and
  Cleanuparr. They were not deployed.
- Corrected hardlink documentation: a real in-container link test returned
  `Cross-device link` because the current bind mounts are separate.
- Documented the Recyclarr/Profilarr ownership boundary: one setting must have
  one writer, with Recyclarr as the preferred declarative owner.

## Current profile audit

- Sonarr: 59 series — 20 `Any`, 27 profile 6, 12 profile 7.
- Radarr: 40 movies — 3 `Any`, 1 profile 7, 36 profile 8.

The `Any` assignments were intentionally left unchanged. They require a
content-by-content decision, not a bulk replacement.

## Deferred maintenance-window work

- Add the common `/data` mount and migrate stored paths through supported APIs.
- Verify a completed-torrent canary, a real hardlink import, and seeding state.
- Remove legacy path aliases only after observation.
- Recreate containers to apply image pinning or healthcheck changes.
- Decide whether to move Prowlarr off `develop` after compatibility testing.
- Reconstruct the missing authoritative Seerr Compose definition; it was not
  guessed or invented during this audit.
