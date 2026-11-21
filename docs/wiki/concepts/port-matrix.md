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
last_ingested: 2026-11-21
last_lint: 2026-11-21
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
| 3001/tcp | Dashdot | host loopback, fronted by Traefik | system dashboard | CloudNode dashdot exposed at `dash.example.com` |
| 3458/tcp | CrowdSec Web UI | host loopback | admin UI | `127.0.0.1:3458:3000` |
| 3457/tcp | Traefik Logs UI | host loopback | log dashboard | container traffic uses `traefik-dashboard:3000` |
| 5000/tcp | Traefik Agent | host loopback | log dashboard agent | container traffic uses `traefik-agent:5000` |
| 6060/tcp | CrowdSec | host loopback | metrics | `127.0.0.1:6060:6060` |
| 8080/tcp | CrowdSec | host loopback | LAPI | host firewall bouncer uses `127.0.0.1:8080`; container clients use `crowdsec:8080` |
| 3000/tcp | Dockhand | internal, fronted by Traefik | container management | exposed at `dockhand.example.com` |
| 7575/tcp | Homarr | host loopback, fronted by Traefik | dashboard UI | exposed at `home.example.com`; Pangolin targets `homarr:7575` on the shared network |
| 1411/tcp | Pocket-ID | internal, fronted by Traefik | identity provider | passkey/OIDC |

## Application edge and app ports (rammus)

Since the 2026-11-21 migration these ports belong to rammus (`192.168.0.12`).
NASUS (`192.168.0.10`) exposes only SSH, the ADM UI on 9980, and NFS.

| Port | Owner | Path | Purpose | Notes |
|---|---|---|---|---|
| 80/tcp | rammus Traefik | LAN / routed | HTTP entrypoint | redirects to HTTPS |
| 443/tcp | rammus Traefik | LAN / routed | HTTPS entrypoint | Cloudflare DNS-01 certs, `traefik:3.7.17` |
| 8082/tcp | rammus Traefik | container only | ping/health endpoint | not published |
| 2375/tcp | Hawser | LAN, bound to `192.168.0.12` only | remote Docker API proxy | token required; unauthenticated requests return `401`. UFW rules do **not** filter published container ports — Docker's own chains run first |
| 32400/tcp | Plex | direct / routed | Plex main port | host networking, `plex.example.com`; NAT forward moved from `.10` to `.12` |
| 8080/tcp | qBittorrent | internal / routed | torrent web UI | exposed via Traefik at `torrent.example.com`; `AuthSubnetWhitelist` must include the Docker subnet `172.19.0.0/16`, and peer containers depend on that whitelist instead of logging in |
| 6881/tcp+udp | qBittorrent | routed | torrent listening port | NAT forwards moved from `.10` to `.12`; binds all interfaces |
| 3003/tcp | dashdot | bound to `192.168.0.12` | system dashboard | `dash.example.com` via Traefik; the old NASUS `dash` container and `dash-nas` name are retired. Binding is explicit because UFW does not filter published ports |
| 8099/tcp | scryer | loopback only | web UI | `127.0.0.1:8099`→container `:8080`, fronted by Traefik |
| 6060/tcp | arr-mcp | loopback only | MCP endpoint | `127.0.0.1:6060`, reached from CloudNode through supervised SSH |
| 9980/tcp | NASUS ADM | LAN, proxied by rammus Traefik | NAS admin UI | `nasus.example.com` |
| 2049/tcp | NASUS NFS | LAN | NFSv3 exports | consumed by rammus at `/mnt/nasus/*` |

## How it applies here
- CrowdSec AppSec `7422/tcp` is internal-only and not published.
- Traefik ping health endpoints on CloudNode `8080/tcp` and HomeNode `8082/tcp` are internal and not published.
- CloudNode uses Traefik behind Gerbil's namespace-sharing model.
- rammus runs its own Traefik on a flat `traefik_traefik` network (subnet `172.19.0.0/16`). NASUS runs no Traefik.
- LAN name resolution is AdGuard Home on OPNsense, which rewrites each service name explicitly to `192.168.0.12`. There is no wildcard record.

## Gotchas
- CloudNode Traefik does not look like a normal network member because it rides Gerbil's namespace.
- Loopback host publication does not isolate peers already attached to a service's Docker network.
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
