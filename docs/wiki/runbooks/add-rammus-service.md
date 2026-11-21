---
title: "Add a new service on rammus"
slug: runbook-add-rammus-service
type: runbook
status: active
tags: ["homelab", "runbook", "rammus", "traefik", "dns"]
aliases: ["add service", "new service rammus"]
entities:
  primary: runbook-add-rammus-service
  mentions: ["host-rammus", "host-cloudnode"]
related: ["../hosts/rammus.md", "../concepts/port-matrix.md", "../networks/traefik-traefik.md"]
sources: ["AGENTS.md", "docs/wiki/hosts/rammus.md"]
confidence: high
audience_level: operator
last_ingested: 2026-11-21
last_lint: 2026-11-21
---
# Add a new service on rammus

## When to use this
You are adding a service that LAN clients and possibly the internet should reach
as `something.example.com`. Since 2026-11-21 all applications run on rammus
(`192.168.0.12`).

## The five places that must agree

There is no wildcard anywhere in this chain, so a new name needs **all five**.
Miss one and you get a silent 404 or a red dashboard tile.

1. **Compose file** — `/opt/docker/stacks/<service>/docker-compose.yml`
   - Appdata at `/opt/docker/config/<service>` on the **local SSD**. Never NFS:
     SQLite on NFS risks corruption and lock failures.
   - Join the external network `traefik_traefik`.
   - Set `restart: unless-stopped` so it comes back after a reboot.
   - Add Traefik labels for the route and the `letsencrypt` cert resolver.
   - Add a `healthcheck`. If you skip it, say so in the wiki — `newt`,
     `qbittorrent`, and `dashdot` have none and that is a known weaker signal.
2. **AdGuard Home rewrite** on OPNsense — `<name>.example.com` → `192.168.0.12`.
   Web UI at `dns.example.com`. Back up
   `/usr/local/AdGuardHome/AdGuardHome.yaml` first and edit whole blocks with
   `perl -0777`; an `awk` range delete once took DNS down for three minutes.
3. **CloudNode `/etc/hosts`** — add the name pointing at `192.168.0.12`.
   The CloudNode does not use AdGuard for these names.
4. **Homarr `extra_hosts`** in `stacks/dashboard/docker-compose.yml` on the
   CloudNode, then `docker compose up -d homarr`. These land in the Homarr
   container's own `/etc/hosts` and override both DNS and the host file.
   Without this the tile shows red even when the service is healthy.
5. **Pangolin resource**, if the service must be reachable from the internet.
   Edit it while the `pangolin` container is stopped and take a DB backup first:
   `docker stop pangolin`, then `db.sqlite` → point the target at
   `192.168.0.12:<port>`, then start it.

## Verify

```bash
# from rammus: the container is up and healthy
docker ps --format '{{.Names}}\t{{.Status}}\t{{.Ports}}'

# from the CloudNode: the name resolves to rammus, not the old host
getent hosts <name>.example.com

# from inside Homarr: the tile will actually be able to reach it
docker exec homarr wget -qS -O /dev/null --timeout=10 https://<name>.example.com

# the certificate issued
docker logs traefik --since 10m 2>&1 | grep -i "<name>"
```

## Pitfalls seen in practice

- **Do not publish a port unless there is no proxy route.** Docker writes its own
  iptables rules ahead of UFW, so `-p 0.0.0.0:port:port` is reachable regardless
  of firewall rules. Bind explicitly (`192.168.0.12:port:containerport`) when a
  host port is genuinely needed, as `hawser` and `dashdot` now do.
- **Do not put appdata on `/mnt/nasus/*`.** Those are `hard` NFS mounts; if NASUS
  goes away, every process touching the mount blocks in `D`.
- **Peer containers need to be allowed by the target.** qBittorrent, for example,
  only accepts peer traffic from subnets in `AuthSubnetWhitelist`; a new service
  on a new Docker subnet gets `403` until that subnet is added.
- **A new Docker network changes container IPs.** Never hardcode `172.19.0.x`
  anywhere. Resolve names, or read the addresses fresh with
  `docker network inspect traefik_traefik`.
