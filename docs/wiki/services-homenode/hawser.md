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
last_ingested: 2026-04-17
last_lint: 2026-04-17
---
# hawser

Dockhand's remote agent. The CloudNode Dockhand connects to this agent over TCP
to manage HomeNode containers in the same UI as CloudNode containers.

- **Image**: `ghcr.io/finsys/hawser:latest` ⚠️
- **Compose file**: `/volume1/docker/hawser/docker-compose.yml`
- **Tracked copy**: **not tracked** (finding NM1)
- **Port**: `2375:2376` (Standard mode — Dockhand initiates from CloudNode)
- **Mode**: Standard (inbound). Edge mode commented-out.
- **Network**: `traefik_traefik`

## Upstream Sources

- Dockhand docs (parent project): <https://dockhand.pro/manual/>
- Hawser image: <https://github.com/finsys/hawser>
- Note image org is **`finsys`** (with "i"), while Dockhand on CloudNode is
  `fnsys/dockhand` (no "i"). Not a typo — two image names, same vendor.

## Our Compose

```yaml
services:
  hawser:
    image: ghcr.io/finsys/hawser:latest
    container_name: hawser
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    ports:
      - "2375:2376"   # host:container
    environment:
      - TOKEN=${HAWSER_TOKEN:-}
      - AGENT_NAME=homenode
      - LOG_LEVEL=info
      # Edge mode alternative:
      # - DOCKHAND_SERVER_URL=wss://dockhand.example.com/api/hawser/connect
    networks: [traefik_traefik]
```

## Deviations / Upstream Patterns

Hawser has two deployment modes:

- **Standard** (what we use): Hawser listens on a port; Dockhand connects
  inbound. Requires the token to authenticate incoming requests.
- **Edge**: Hawser opens an outbound WebSocket to Dockhand; no inbound
  port needed.

For a home NAS reachable only via Olm tunnel from the CloudNode, **Edge mode is
strictly safer** — no publicly listening port at all.

## Findings

### F-N-HAWSER-1 — empty-token fallback (`critical` / NC2)
`TOKEN=${HAWSER_TOKEN:-}` defaults to empty string if the variable isn't
set. If `.env` is ever missing, renamed, or not loaded (Synology's Compose
UI has bitten people here when re-pasting the YAML without the env file),
Hawser starts with **no authentication** at all and accepts any client.

Combined with `docker.sock:/var/run/docker.sock` mounted rw and port
`2375` published on `0.0.0.0`, this is full remote root on HomeNode.

### F-N-HAWSER-2 — `docker.sock` rw (`medium` / NM12)
Hawser legitimately needs write access to the Docker API (otherwise it
couldn't start/stop/create containers, which is its whole job). Tracked
here so the combined risk with F-N-HAWSER-1 is visible in one place.

### F-N-HAWSER-3 — `:latest` image (`medium` / NM2)
Hawser is tightly coupled to the Dockhand server's API schema. A
dockhand-side schema bump that ships faster than hawser's `:latest` rebuild
will cause the agent to silently stop working. Pin both sides together.

### F-N-HAWSER-4 — inbound mode on a tunnel-only host (`medium`)
For HomeNode, which is only reachable from the CloudNode via Olm tunnel, Edge mode
is the cleaner architecture. Inbound mode requires publishing a port and
trusting the LAN / tunnel perimeter.

### F-N-HAWSER-5 — not tracked in repo (`high` / NM1)
One of the 8 missing files in `host-configs/homenode/`. Given this file
literally contains the auth token variable name and the architecture
choice, it belongs in version control.

## Remediation

### Fix F-N-HAWSER-1 — require a token

Change the env from optional to required:

```yaml
    environment:
      - TOKEN=${HAWSER_TOKEN:?HAWSER_TOKEN is required}
      - AGENT_NAME=homenode
      - LOG_LEVEL=info
```

`${VAR:?message}` causes Docker Compose to **refuse to start** the service
if `VAR` is unset or empty, which is what we want. Pair with bind to
loopback:

```yaml
    ports:
      - "127.0.0.1:2375:2376"
```

…but this only works if Dockhand reaches HomeNode from the host's own
loopback, which it does NOT (it comes from 192.168.1.1 via the Olm
tunnel). So instead, bind to the tunnel interface or switch to Edge
mode (next fix).

### Fix F-N-HAWSER-4 — switch to Edge mode

```yaml
    # drop ports entirely
    environment:
      - TOKEN=${HAWSER_TOKEN:?}
      - AGENT_NAME=homenode
      - LOG_LEVEL=info
      - DOCKHAND_SERVER_URL=wss://dockhand.example.com/api/hawser/connect
```

This removes the public listen port on HomeNode entirely. The agent connects
outbound to the CloudNode Dockhand, which authenticates via the token during
the WebSocket handshake.

### Fix F-N-HAWSER-3

Pick a concrete tag from
<https://github.com/finsys/hawser/pkgs/container/hawser> matching the
Dockhand version you're running on the CloudNode:

```yaml
    image: ghcr.io/finsys/hawser:df2ca0e3-baseline
```

### Fix F-N-HAWSER-5

`scp /volume1/docker/hawser/docker-compose.yml` into
`host-configs/homenode/hawser/docker-compose.yml` and commit.

## Operational Notes

- Dockhand-side registration: Environments → New → "Hawser Standard" →
  host `192.168.1.10`, port `2375`, token matches `.env`.
- CloudNode-to-HomeNode network path requires the Olm tunnel (`192.168.1.0/24 dev
  olm`) up. If `docker exec dockhand curl http://192.168.1.10:2375/...`
  hangs, check `olm-watchdog.timer` on the CloudNode first.
- Hawser logs (`docker logs hawser`) are the best source for auth failures
  ("token mismatch" vs "empty token").
