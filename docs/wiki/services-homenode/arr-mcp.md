---
title: "arr-mcp"
slug: homenode-arr-mcp
type: service
status: active
tags: ["homelab", "homenode", "service", "mcp"]
aliases: ["media MCP"]
entities:
  primary: homenode-arr-mcp
  mentions: []
related: ["../maintenance-2026-10-27.md", "./newt.md"]
sources: ["host-configs/homenode/arr-mcp/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# arr-mcp

Authenticated media-stack MCP service, verified as image
`ghcr.io/bardesss/arr-mcp:1.50.0` on 2026-10-31. The contradictory
`ARR_MCP_VERSION` override was removed. Its NAS Compose file is
`/volume1/docker/config/arr-mcp/docker-compose.yml`; the sanitized reference is
`host-configs/homenode/arr-mcp/docker-compose.yml` is the sanitized live snapshot, 2026-10-31.

The config mount is `/volume1/docker/config/arr-mcp:/config`. Bearer credentials
and media-service API keys remain private in that configuration, outside Git.
NAS port 6060 is published only on loopback. CloudNode's supervised SSH tunnel
publishes its local endpoint only at `127.0.0.1:16060`.

The existing `/healthz` check verifies service availability. A separate
authenticated MCP initialization/tool listing returned 39 tools after both
Olm and Newt maintenance. Neither check invokes tools that modify media.
See the 2026-10-27 maintenance note for the verification context.

`ghcr.io/bardesss/arr-mcp:1.50.0` was verified on 2026-10-31. The earlier `ARR_MCP_VERSION=1.21.2` override has been removed; do not use the historical Compose snapshot below as the current deployment definition.

## Current release

`ghcr.io/bardesss/arr-mcp:1.50.0` is deployed. The historical
`ARR_MCP_VERSION=1.21.2` Compose override was removed so it no longer
contradicts the image tag.

## Upstream source

- [arr-mcp upstream documentation](https://github.com/bardesss/arr-mcp)
