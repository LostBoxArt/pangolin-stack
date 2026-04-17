---
title: "qbit-proxy"
slug: vps-qbit-proxy
type: service
status: active
tags: ["homelab", "vps", "service", "qbit-proxy"]
aliases: ["qbit-proxy"]
entities:
  primary: vps-qbit-proxy
  mentions: []
related: ["./README.md", "./compose-review-2026-04-17.md", "./system-overview.md"]
sources: ["stacks/dashboard/docker-compose.yml"]
confidence: high
audience_level: operator
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# qbit-proxy

Local reverse-proxy sidecar for Homarr's qBittorrent widget. Built from
in-repo Dockerfile.

- **Build context**: `./qbit-proxy/`
- **Compose file**: `stacks/dashboard/docker-compose.yml`
- **Internal port**: `8081`
- **Target**: `torrent.dennisb.xyz` (resolves via Homarr's `extra_hosts` to
  `192.168.0.10`)

## Purpose

Homarr v0.15+ ships a qBittorrent widget that breaks against qBittorrent
v5.1.4+ because the newer qBit sets the `Secure` flag on its `SID` cookie.
Homarr (running in a browser over HTTPS) cannot read `Secure` cookies when
the widget calls qBit's API through a non-TLS path, or when the `Host`
header doesn't match what qBit expects.

`qbit-proxy`:

1. Accepts HTTPS calls from Homarr at `http://qbit-proxy:8081`.
2. Forwards them to `torrent.dennisb.xyz` (i.e. qBit on NASUS) with the
   correct `Host:` header.
3. **Strips the `Secure` flag** off response cookies so Homarr can read them.

Documented in `AGENTS.md` under "qBittorrent Widget Fix".

## Upstream Sources

None — this is bespoke code living in `qbit-proxy/`. The upstream issue is
tracked on Homarr's GitHub (search "qbittorrent secure cookie"). Confirm
the fix is still needed when bumping Homarr:
<https://github.com/homarr-labs/homarr/issues?q=qbittorrent+cookie>.

## Our Compose (relevant slice)

```10:20:stacks/dashboard/docker-compose.yml
  qbit-proxy:
    container_name: qbit-proxy
    networks:
      - pangolin
    build:
      context: ../../qbit-proxy
    restart: unless-stopped
    environment:
      - TARGET_HOST=torrent.dennisb.xyz
      - TARGET_IP=192.168.0.10
```

## Deviations

Not applicable — no upstream.

## Findings

### F-QBP-1 — no healthcheck (`low`)
The proxy is tiny and stable, but Homarr `depends_on: qbit-proxy` would be
more reliable with a healthcheck attached.

### F-QBP-2 — workaround may become obsolete
Homarr upstream has an open issue for this. When that lands, this service
can be removed along with the `extra_hosts` line in Homarr's compose.

## Remediation

### Fix F-QBP-1 (optional)

```yaml
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8081/health"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
```

(Add a `/health` route to `qbit-proxy/index.js` if one doesn't exist.)

### Retirement path (F-QBP-2)

When Homarr's qBit widget supports the current qBit cookie behavior
natively:

1. Remove `depends_on: qbit-proxy` from Homarr.
2. Remove the `qbit-proxy` service block.
3. Remove `qbit-proxy/` directory.
4. Homarr widget URL changes from `http://qbit-proxy:8081` to
   `https://torrent.dennisb.xyz`.
5. Document the change in `AGENTS.md`.

## Operational Notes

- The proxy runs on the `pangolin` docker network, so Homarr references it
  by `http://qbit-proxy:8081`, not by host IP.
- If qBit on NASUS changes hostname or IP, update both
  `TARGET_HOST`/`TARGET_IP` env vars here and the `extra_hosts` entry in
  Homarr's service.
