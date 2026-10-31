---
title: "hawser"
slug: homenode-hawser
type: service
status: active
tags: ["homelab", "homenode", "service", "hawser"]
aliases: ["hawser"]
entities:
  primary: homenode-hawser
  mentions: []
related: ["./README.md", "./homenode-review-2026-04-17.md", "./system-overview.md"]
sources: ["/volume1/docker/hawser/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-10-27
---
# hawser

Dockhand's remote Docker agent. The current NAS deployment uses authenticated
Standard mode and joins `traefik_traefik`. It retains access to the Docker socket
because management operations require it; possession of its token grants powerful
host access.

## Current configuration (2026-10-27)

The live Compose file is `/volume1/docker/hawser/docker-compose.yml`.
The sanitized reference is `host-configs/homenode/hawser/docker-compose.yml`.
It requires a private `HAWSER_TOKEN` variable and publishes
`192.168.1.10:2375:2376` using the repository's example NAS address. The actual
NAS LAN binding was verified after recreating only Hawser with the same cached
image, environment, token, and Standard-mode behavior.

A LAN-only binding reduces listening interfaces. It does not block other LAN
callers or substitute for authentication, firewall policy, or encrypted transport.
Keep the management token private; do not publish the Docker API on the Internet.

## Verification

Use the actual NAS address. These checks deliberately send no credentials:

```bash
curl --noproxy '*' --fail --silent --show-error --max-time 10   http://192.168.1.10:2375/_hawser/health
curl --noproxy '*' --silent --show-error --max-time 10 -o /dev/null   -w 'Docker API without credentials: %{http_code}\n'   http://192.168.1.10:2375/_ping
```

Expected: native health 200 and unauthenticated Docker API 401. An authenticated
Dockhand environment-2 container listing also passed after the binding change.
Health alone does not prove authenticated management works.

The VPS prefers a Tailscale subnet route for ordinary NAS requests. A forced Olm
health probe was also verified; see [Olm operations](../services/olm.md).

## Edge mode boundary

Hawser supports an outbound WebSocket connection in Edge mode. The current public
Dockhand endpoint is behind Pangolin authentication and returns 401 for that WSS
path. Setting `DOCKHAND_SERVER_URL` and removing the Standard-mode port would
therefore break management in this deployment. Keep Standard mode unless a
supported, authenticated machine connection through that boundary has been
configured and tested first. Do not remove SSO globally to make Edge mode work.

## Recovery

Retain the previous private Compose/environment files. If a binding change fails,
restore only that mapping and recreate Hawser with the cached image. Re-check
native health, unauthenticated denial, and authenticated Dockhand inventory.
Never restore an optional empty-token fallback.

## Upstream sources

- [Dockhand manual](https://dockhand.pro/manual/)
- [Hawser source](https://github.com/Finsys/hawser)
