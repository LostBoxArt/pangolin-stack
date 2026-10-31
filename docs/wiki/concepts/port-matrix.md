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
related: ["../system-overview.md", "../services/traefik.md", "../services-homenode/traefik.md", "../networks/pangolin.md", "../networks/traefik-traefik.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md", "docs/wiki/compose-review-2026-04-17.md", "docs/wiki/homenode-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-10-31
last_lint: 2026-10-31
---
# Port Matrix

## TL;DR
This page is the quickest view of which host or service owns which important port, whether it is public, tunneled, LAN-only, or considered a risk surface.

## CloudNode edge and management

| Port | Owner | Path | Purpose | Notes |
|---|---|---|---|---|
| 80/tcp | Gerbil namespace with CloudNode Traefik | public edge | HTTP entrypoint | CloudNode Traefik shares Gerbil namespace |
| 443/tcp | Gerbil namespace with CloudNode Traefik | public edge | HTTPS entrypoint | primary public ingress |
| 443/udp | Gerbil namespace with CloudNode Traefik | public edge | HTTP/3 QUIC entrypoint | CloudNode Traefik HTTP/3 via Gerbil namespace |
| 51820/udp | Gerbil | public edge | WireGuard relay | documented in `AGENTS.md` |
| 21820/udp | Gerbil | public edge | additional WireGuard-related relay port | documented in `AGENTS.md` |
| 3001/tcp | Pangolin | internal, fronted by Traefik | control plane UI/API | exposed at `pangolin.example.com` |
| 3001/tcp | Dashdot | internal, fronted by Traefik | system dashboard | CloudNode dashdot exposed at `dash.example.com` |
| 3458/tcp | CrowdSec Web UI | host-published | admin UI | explicitly documented as host-published |
| 3000/tcp | Dockhand | internal, fronted by Traefik | container management | exposed at `dockhand.example.com` |
| 7575/tcp | Homarr | internal, fronted by Traefik | dashboard UI | exposed at `home.example.com` |
| 1411/tcp | Pocket-ID | internal, fronted by Traefik | identity provider | passkey/OIDC |

## HomeNode edge and app ports

| Port | Owner | Path | Purpose | Notes |
|---|---|---|---|---|
| 80/tcp | HomeNode Traefik | LAN / routed | HTTP entrypoint | LAN reverse proxy |
| 443/tcp | HomeNode Traefik | LAN / routed | HTTPS entrypoint | Cloudflare DNS-01 certs |
| 9080/tcp | HomeNode Traefik | not published | former dashboard/API host port | old host mapping removed; API insecure disabled |
| 2375/tcp | Hawser | LAN / CloudNode-reachable | remote Docker API proxy | `NC2`, token-protected but high risk if misconfigured |
| 1411/tcp | Pocket-ID equivalent not on HomeNode | n/a | n/a | identity is CloudNode-side |
| 32400/tcp | Plex | WAN forward → HomeNode NAS | direct media ingress | router forwards WAN `32400/tcp` to the NAS; Pangolin/Newt is web UI only |
| 6881/tcp | qBittorrent | WAN forward → HomeNode NAS | peer traffic | published by qBittorrent and forwarded on the router |
| 6881/udp | qBittorrent | WAN forward → HomeNode NAS | peer traffic | published by qBittorrent and forwarded on the router |
| 8080/tcp | qBittorrent | internal / routed | torrent web UI | exposed via Traefik |

## How it applies here
- CrowdSec AppSec `7422/tcp` is internal-only and not published.
- Traefik ping health endpoints on CloudNode `8080/tcp` and HomeNode `8082/tcp` are internal and not published.
- CloudNode uses Traefik behind Gerbil's namespace-sharing model.
- HomeNode uses a flat `traefik_traefik` network and a separate Traefik instance.
- The quickest port-risk checks are currently `2375` on Hawser; HomeNode Traefik's insecure API setting has been removed.

## Gotchas
- CloudNode Traefik does not look like a normal network member because it rides Gerbil's namespace.
- HomeNode Traefik's insecure API setting has been removed; Hawser API port remains a known risk surface.
- Port ownership questions often require both the service page and the network page, not just compose snippets.

## Related concepts
- [[../networks/pangolin.md]]
- [[../networks/traefik-traefik.md]]
- [[../services/traefik.md]]
- [[../services-homenode/traefik.md]]
- [[../services-homenode/hawser.md]]

## References
- [[../system-overview.md]]
- [[../compose-review-2026-04-17.md]]
- [[../homenode-review-2026-04-17.md]]
