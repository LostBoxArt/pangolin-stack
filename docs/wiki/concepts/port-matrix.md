---
title: "Port Matrix"
slug: concept-port-matrix
type: concept
status: active
tags: ["homelab", "concept", "ports", "networking"]
aliases: ["service ports", "port map"]
entities:
  primary: concept-port-matrix
  mentions: []
related: ["../system-overview.md", "../services/traefik.md", "../services-nasus/traefik.md", "../networks/pangolin.md", "../networks/traefik-traefik.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md", "docs/wiki/compose-review-2026-04-17.md", "docs/wiki/nasus-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# Port Matrix

## TL;DR
This page is the quickest view of which host or service owns which important port, whether it is public, tunneled, LAN-only, or considered a risk surface.

## VPS edge and management

| Port | Owner | Path | Purpose | Notes |
|---|---|---|---|---|
| 80/tcp | Gerbil namespace with VPS Traefik | public edge | HTTP entrypoint | VPS Traefik shares Gerbil namespace |
| 443/tcp | Gerbil namespace with VPS Traefik | public edge | HTTPS entrypoint | primary public ingress |
| 51820/udp | Gerbil | public edge | WireGuard relay | documented in `AGENTS.md` |
| 21820/udp | Gerbil | public edge | additional WireGuard-related relay port | documented in `AGENTS.md` |
| 3001/tcp | Pangolin | internal, fronted by Traefik | control plane UI/API | exposed at `pangolin.dennisb.xyz` |
| 3458/tcp | CrowdSec Web UI | host-published | admin UI | explicitly documented as host-published |
| 3000/tcp | Dockhand | internal, fronted by Traefik | container management | exposed at `dockhand.dennisb.xyz` |
| 7575/tcp | Homarr | internal, fronted by Traefik | dashboard UI | exposed at `home.dennisb.xyz` |
| 8080/tcp | Termix | internal, fronted by Traefik | web terminal | exposed at `termix.dennisb.xyz` |
| 1411/tcp | Pocket-ID | internal, fronted by Traefik | identity provider | passkey/OIDC |
| 53/tcp+udp | AdGuard Home | host-published | DNS | DNS service |
| 853/tcp | AdGuard Home | host-published | DNS-over-TLS | public DNS endpoint |

## NASUS edge and app ports

| Port | Owner | Path | Purpose | Notes |
|---|---|---|---|---|
| 80/tcp | NASUS Traefik | LAN / routed | HTTP entrypoint | LAN reverse proxy |
| 443/tcp | NASUS Traefik | LAN / routed | HTTPS entrypoint | Cloudflare DNS-01 certs |
| 9080/tcp | NASUS Traefik dashboard | LAN / risk surface | admin dashboard | `NC1`, currently insecure |
| 2375/tcp | Hawser | LAN / VPS-reachable | remote Docker API proxy | `NC2`, token-protected but high risk if misconfigured |
| 1411/tcp | Pocket-ID equivalent not on NASUS | n/a | n/a | identity is VPS-side |
| 32400/tcp | Plex | direct / routed | Plex main port | media server |
| 8080/tcp | qBittorrent | internal / routed | torrent web UI | exposed via Traefik |

## How it applies here
- VPS uses Traefik behind Gerbil's namespace-sharing model.
- NASUS uses a flat `traefik_traefik` network and a separate Traefik instance.
- The quickest port-risk checks are currently `9080` on NASUS Traefik and `2375` on Hawser.

## Gotchas
- VPS Traefik does not look like a normal network member because it rides Gerbil's namespace.
- NASUS Traefik dashboard and Hawser API port are the current known compromise-risk surfaces.
- Port ownership questions often require both the service page and the network page, not just compose snippets.

## Related concepts
- [[../networks/pangolin.md]]
- [[../networks/traefik-traefik.md]]
- [[../services/traefik.md]]
- [[../services-nasus/traefik.md]]
- [[../services-nasus/hawser.md]]

## References
- [[../system-overview.md]]
- [[../compose-review-2026-04-17.md]]
- [[../nasus-review-2026-04-17.md]]
