---
title: "HomeNode Host"
slug: host-homenode
type: host
status: active
tags: ["homelab", "homenode", "nasus", "storage", "host"]
aliases: ["HomeNode", "NASUS", "nasus", "192.168.0.10", "192.168.1.10"]
entities:
  primary: host-homenode
  mentions: ["host-rammus", "host-cloudnode"]
related: ["../system-overview.md", "./rammus.md", "../homenode-review-2026-04-17.md", "../networks/traefik-traefik.md", "../runbooks/backup-nasus-config.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md", "docs/wiki/homenode-review-2026-04-17.md"]
confidence: high
audience_level: operator
last_ingested: 2026-11-21
last_lint: 2026-11-21
---
# HomeNode Host (NASUS)

ASUSTOR NAS. As of 2026-11-21 it is **pure storage: it runs zero Docker
containers**. Every application workload moved to [[./rammus.md]].

## Identity
- Hostname: `NASUS` (ADM reports `AS6704T-2D47`)
- LAN IP: `192.168.0.10`
- OS: ASUSTOR ADM
- Role: NFS storage only — media library, backups, and a fast scratch volume

## What it provides
| Export | Mounted on rammus as | Notes |
|---|---|---|
| `/volume1/media` | `/mnt/nasus/media` | media library + downloads, the `downloads/incomplete` path is overridden onto rammus local SSD |
| `/volume1/storage` | `/mnt/nasus/storage` | general storage |
| `/volume1/backups` | `/mnt/nasus/backups` | holds the nightly rammus backup |
| `/volume2/fast` | `/mnt/nasus/fast` | single-NVMe scratch volume, **no redundancy** |

`/volume1` is RAID5 across four healthy disks. `/volume2` is RAID1 with a single
member, so it has no redundancy at all.

## NFS configuration
- Exports served over **NFSv3**; clients pin `nfsvers=3`
- `RPCNFSDOPTS` keeps `--udp` and disables v4, but that setting **does not
  persist**: ADM rebuilds its own init script at boot and re-enables NFSv4. This
  is a known, accepted risk. Do not attempt to drain `rpc.nfsd` at runtime —
  doing so previously wedged nfsd and required a reboot.
- `/volume1/docker` is deliberately **not** exported

## Containers
**All fourteen were set to `restart=no` on 2026-11-21**, including `sonarr`,
`radarr`, `bazarr`, `recyclarr`, and `profilarr`, which had been left on
`unless-stopped`. Docker will now never start any of them, on daemon restart or
after a reboot. A manual `docker start` still works, which is what preserves the
rollback path.

The two dangerous ones — `newt` and `plex` — must stay `restart=no`, or a reboot
produces a duplicate tunnel client and a duplicate Plex identity.

Do not "roll back" by starting everything: two `newt` instances with the same
site credentials flap the tunnel, and two `plex` instances with the same
`MachineIdentifier` corrupt library state.

## Access
- SSH: `ssh jesus@192.168.0.10` — requires the explicit key,
  `-o IdentitiesOnly=yes -i ~/.ssh/id_rsa`
- `sudo` is password-based; the password is held on the host, not in this repo
- **Rammus cannot SSH here.** ADM runs `ipblockman`, which blacklists
  `192.168.0.12` after a seccomp violation in its `sshd-session`. Data
  synchronisation therefore runs NASUS → rammus with a dedicated key on NASUS.
- ADM web UI: `nasus.example.com` → rammus Traefik → `192.168.0.10:9980`

## Known operational notes
- Reboots are performed from the ADM GUI by the owner. Do not click the NFS page
  in the ADM GUI; each click queues a stuck job.
- Host monitoring via a `dashdot` container was retired on 2026-11-21, so
  `dash-nas.example.com` no longer exists. Use ADM's Activity Monitor and
  Storage Manager for CPU, disk, and SMART data.
- A `newt-watchdog` cron entry and a `/dev/dri` permission-entry cron were
  removed on 2026-11-21; both existed only for workloads that moved to rammus.
- **Two OPNsense rules block traffic to `.10:2375`** (Hawser). They are
  `block drop` rules on `igc1` and `igc3`, not permits — verified with
  `pfctl -sr | grep 2375`. They are protective, harmless, and can stay. The
  `.10:22` and `.10:9980` block rules are likewise legitimate.
- The NFS exports use `no_root_squash` and `async` for several subnets. Only
  `192.168.0.12` actually mounts them; the export list is wider than it needs to
  be.
- Historical service pages under `docs/wiki/services-homenode/` still describe
  the pre-migration NASUS layout. They are marked `status: historical` and carry
  a banner. Read [[./rammus.md]] for current state.
