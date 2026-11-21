---
title: "arr-mcp"
slug: homenode-arr-mcp
type: service
status: historical
tags: ["homelab", "homenode", "service", "mcp"]
aliases: ["media MCP"]
entities:
  primary: homenode-arr-mcp
  mentions: []
related: ["../runbooks/monitoring-and-arr-mcp.md", "./newt.md"]
sources: ["host-configs/homenode/arr-mcp/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-10-27
---
# arr-mcp

**Historical (pre-2026-11-21 NASUS layout). Do not deploy. Live: [[../hosts/rammus.md]].**

Authenticated media-stack MCP service, verified as image
`ghcr.io/bardesss/arr-mcp:1.44.5` on 2026-10-27. Its NAS Compose file is
`/volume1/docker/config/arr-mcp/docker-compose.yml`; the sanitized reference is
`host-configs/homenode/arr-mcp/docker-compose.yml`.

The config mount is `/volume1/docker/config/arr-mcp:/config`. Bearer credentials
and media-service API keys remain private in that configuration, outside Git.
NAS port 6060 is published only on loopback. CloudNode's supervised SSH tunnel
publishes its local endpoint only at `127.0.0.1:16060`.

The existing `/healthz` check verifies service availability. A separate
authenticated MCP initialization/tool listing returned 39 tools after both
Olm and Newt maintenance. Neither check invokes tools that modify media.
See [monitoring and tunnel operations](../runbooks/monitoring-and-arr-mcp.md)
for exact verification and recovery commands.

A subsequent [functional audit](../maintenance-2026-10-27.md#functional-tooling-follow-up)
called all 39 tools: 18 configured read paths succeeded, 18 write tools returned
terminal dry-run previews with `applied: false`, and three capabilities remain
unavailable. `get_profile_issues` does not check drift without a compatible
Profilarr connection; `sync_database` likewise requires Profilarr. `set_watched`
requires Jellyfin and cannot write Plex watch state. That read/dry-run audit did
not exercise native apply operations. A later authorized
[queue cleanup](../maintenance-2026-10-27.md#authorized-queue-cleanup) used the
native APIs for targeted imports and queue housekeeping; MCP destructive
permissions remain disabled.

The captured Compose environment still contains historical
`ARR_MCP_VERSION=1.21.2`, which also overrides the version reported by MCP.
It was preserved as observed; use the inspected image to establish the running
release rather than treating that overridden metadata as its version. This
maintenance did not upgrade or reconfigure arr-mcp.

## Upstream source

- [arr-mcp 1.44.5 documentation](https://github.com/bardesss/arr-mcp/blob/v1.44.5/README.md)
