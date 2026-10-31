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
last_ingested: 2026-10-27
last_lint: 2026-10-27
---
# arr-mcp

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
See the 2026-10-27 maintenance note for the verification context.

The captured Compose environment still contains historical
`ARR_MCP_VERSION=1.21.2`. It was preserved as observed; use the image version
and authenticated protocol metadata when assessing the running release. This
maintenance did not upgrade or reconfigure arr-mcp.

## Upstream source

- [arr-mcp 1.44.5 documentation](https://github.com/bardesss/arr-mcp/blob/v1.44.5/README.md)
