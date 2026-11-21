---
title: "Rammus Host"
slug: host-rammus
type: host
status: active
tags: ["homelab", "rammus", "host", "compute"]
aliases: ["Rammus", "rammus", "192.168.0.12", "pn62"]
entities:
  primary: host-rammus
  mentions: ["host-homenode", "host-cloudnode"]
related: ["../system-overview.md", "./homenode.md", "./cloudnode.md", "../networks/traefik-traefik.md", "../services-homenode/traefik.md", "../services-homenode/newt.md", "../services-homenode/plex.md", "../services-homenode/qbittorrent.md"]
sources: ["AGENTS.md", "docs/wiki/system-overview.md", "docs/wiki/hosts/homenode.md"]
confidence: high
audience_level: operator
last_ingested: 2026-11-21
last_lint: 2026-11-21
---
# Rammus Host

Compute host that runs every application workload. Formerly named `pn62`; renamed
`rammus` on 2026-11-21. NASUS became storage-only in the same migration, so this
host is now the **only** place applications run.

## Identity
- Hostname: `rammus` (previously `pn62`)
- LAN IP: `192.168.0.12`
- Hardware: ASUS Mini PC PN62, Intel Comet Lake-U, single SSD, **1 GbE** (Intel I219-V, `e1000e`, 1000 Mb/s full) — not 2.5 GbE, so the realistic NFS ceiling is about 105–112 MB/s
- OS: Ubuntu 24.04.5 LTS
- Role: all media, torrent, *arr, tunnel, and edge-proxy workloads
- DHCP: static mapping in OPNsense; AdGuard Home rewrites every `*.example.com`
  service name to this address

## Single-point-of-failure warning
Every application now lives here. The host has **one disk and no RAID**. If the
SSD fails, the Plex database, watch history, qBittorrent resume data, *arr
configs, and `acme.json` are lost unless the nightly backup ran. See
[Backups](#backups).

## Compose layout
- Live compose files: `/opt/docker/stacks/<service>/docker-compose.yml`
- Appdata: `/opt/docker/config/<service>`
- Hawser lives outside the pattern, at `/opt/docker/hawser/docker-compose.yml`
- Appdata is **always on the local SSD, never on NFS**. Putting SQLite databases
  on NFS risks corruption and locking failures.

## Services hosted
- [[../services-homenode/traefik.md]] — public 80/443 entry, Cloudflare DNS-01 ACME
- [[../services-homenode/newt.md]] — the only Pangolin tunnel for `192.168.0.0/24`
- [[../services-homenode/plex.md]] — host networking, `/dev/dri` hardware transcoding
- [[../services-homenode/qbittorrent.md]] — WebUI `torrent.example.com`
- [[../services-homenode/prowlarr.md]] — indexer manager
- [[../services-homenode/scryer.md]] — media acquisition manager, WebUI `request.example.com`
- [[../services-homenode/arr-mcp.md]] — authenticated media MCP
- [[../services-homenode/hawser.md]] — Dockhand agent, TCP 2375
- `dashdot` — system dashboard at `dash.example.com`, published on
  `192.168.0.12:3003`. Both paths reach **this** container since the Pangolin
  `dash` target was retargeted at site `homelab` / `192.168.0.12:3003` on
  2026-11-21. The CloudNode's own dashdot still exists but binds
  `127.0.0.1:3001` and has no consumer.

## Storage mounts
NASUS exports are mounted directly (no `systemd` automount — expired automounts
left containers looking at empty directories):

| Mount | Source | Options |
|---|---|---|
| `/mnt/nasus/media` | `192.168.0.10:/volume1/media` | `nfsvers=3,proto=tcp,nolock,noatime,_netdev,nofail,hard` |
| `/mnt/nasus/storage` | `192.168.0.10:/volume1/storage` | same |
| `/mnt/nasus/backups` | `192.168.0.10:/volume1/backups` | same |
| `/mnt/nasus/fast` | `192.168.0.10:/volume2/fast` | same |

`timeo=600,retrans=2` are **kernel defaults for a `hard` NFSv3 mount** and are not
written in `/etc/fstab`; `findmnt -no OPTIONS /mnt/nasus/media` shows them on the
live mount. Editing `/etc/fstab` to add them explicitly is unnecessary.

Compatibility symlinks exist so older paths keep working:
`/volume1/{media,storage,backups}` → `/mnt/nasus/*`. There is **no**
`/volume2/fast` symlink and no `/volume2` content on rammus; nothing references
it. The NASUS export `192.168.0.10:/volume2/fast` is mounted at
`/mnt/nasus/fast`.

`hard` is deliberate. `soft` caused `EIO` errors from slow RAID5 commits during
large writes. The trade-off is that a hung NASUS freezes only the processes
touching `/mnt/nasus/*`, not SSH. Recovery is
`sudo umount -f -l /mnt/nasus/media`, then `sudo mount -a` once NASUS returns,
then restart the NFS-backed containers.

## Docker startup dependency
`/etc/systemd/system/docker.service.d/nfs.conf` uses `Wants=` + `After=` on the
four mount units, **not** `RequiresMountsFor`. With `Requires`, a dead or
still-booting NASUS would stop Docker from starting at all and take every
service down with it. With `Wants`, Docker always starts and only NFS-backed
containers are impacted.

That alone is not enough: `Wants=`/`After=` give no guarantee that a mount
actually succeeded, so with `restart: unless-stopped` the NFS-dependent
containers would start against an empty local directory. The gate:

- `plex` and `qbittorrent` use `restart: "no"` in their compose files. `no` is
  the only policy whose boot behaviour is certain — Docker never starts them on
  daemon start.
- `nasus-media-apps.service` starts them, but only if
  `/mnt/nasus/media` is a real mountpoint. `ExecCondition` is wrapped in
  `timeout 20` so a hung hard mount cannot hang the unit.
- `nasus-media-apps.timer` runs it one minute after boot and every 2 minutes
  after that, and `Wants=mnt-nasus-media.mount` makes each run retry the mount.
  NASUS returning later therefore brings both containers up without intervention.
- Trade-off: crash recovery is up to 2 minutes instead of instant, because
  Docker's own restart is no longer in play.
- **Before a deliberate `docker stop plex` or `qbittorrent`, run
  `sudo systemctl stop nasus-media-apps.timer`**, or it will start them again
  within two minutes. Re-enable it afterwards.

Proven without rebooting: `systemd-analyze verify` passes, the service reports
`Result=success`, `ActiveState=inactive`, container uptimes are unchanged by a
manual `systemctl start` (`docker start` is a no-op on a running container), and
the timer is scheduled. The mount-missing path needs a reboot with NASUS off to
observe.

## Backups
- Script: `/usr/local/sbin/rammus-backup.sh`
- Schedule: `/etc/cron.d/rammus-backup`, daily at 03:30, log at `/var/log/rammus-backup.log`
- Contents: a `/etc` tarball (fstab, hosts, netplan, ufw, ssh, sysctl, cron.d,
  systemd units, `/usr/local/{sbin,bin}`, `/home/jesus/.ssh`) plus an rsync of
  `/opt/docker` to `/mnt/nasus/backups/rammus/opt-docker-latest/`
- Guards: aborts if `/mnt/nasus/backups` is not a mountpoint, and aborts if the
  appdata copy is smaller than 100 MB — both prevent a "successful" backup that
  actually wrote to the local SSD or copied nothing
- Retention: `/etc` tarballs older than 14 days are deleted
- **History:** before each rsync the current `opt-docker-latest` is snapshotted
  to `opt-docker-YYYYMMDD` with `cp -al`. Hardlinks make this free (verified:
  same inode, link count 2), and because `rsync` replaces files instead of
  editing them in place, older snapshots stay intact even after a `--delete`
  run. Seven dated snapshots are kept.
- This closes the worst failure mode: without it, an accidental deletion of
  appdata would have been mirrored into the only copy on the next 03:30 run.
- **Consistent SQLite copies:** after the rsync, every `*.db` over 10 kB under
  `/opt/docker/config` is re-written with `sqlite3 <live> ".backup <dest>.tmp"`
  followed by `mv -f`. `rsync` reads those files while the apps have them open,
  so its copies could be torn; `.backup` is safe on a live database. `sqlite3`
  was installed on 2026-11-21 for this. Verified: `scryer.db` and
  `prowlarr.db` return `integrity_check = ok`, and the Plex library copy is
  readable with the same 258 tables as the live file.
- **The `.tmp` + `mv` is not cosmetic.** When `rsync` sees no change it leaves
  the file in `opt-docker-latest` sharing an inode with `cp -al`'s dated
  snapshot (link count 2). Writing `.backup` straight to `$dest` therefore
  rewrites the file *inside the kept snapshot*, silently replacing history with
  tonight's data. `mv` creates a new inode and leaves the snapshot alone.
  Regression-checked on 2026-11-21: a 2-link pair became inode `…089` (snapshot,
  old rows intact) plus `…090` (latest); after a full run, no `*.db` in
  `opt-docker-latest` shares an inode with any kept snapshot.
- **scryer's own encrypted backups** land in `/backups` inside the container,
  which is `/mnt/nasus/backups/scryer` → `/volume1/backups/scryer` on NASUS. Its
  pre-migration history lived in `/volume2/backups/scryer` (not exported); it was
  copied into `/volume1/backups/scryer` with `cp -p` on 2026-11-21 so the chain is
  continuous. Write access from inside the container was verified, and the
  in-container `"automatic backup scheduler started"` line appears on each start.
  The key file `.scryer-auto-backup-key` stays on `/volume2/backups` as an
  offline copy — scryer keeps its own key state and does not need that path.
- **The old `configs-*.tgz` archive producer is dead.** Those files came from the
  NASUS `config-backup` container, which is stopped. Nothing writes them now, so
  monitoring watches the `rammus-etc-*.tar.gz` tarball and `opt-docker-latest`
  instead.
- Plex's `com.plexapp.plugins.library.db` cannot be `integrity_check`ed with the
  stock `sqlite3` — it uses a custom tokenizer (`unknown tokenizer: collating`).
  That is not corruption. Plex also writes its own dated `*.db-YYYY-MM-DD`
  copies, which are the most restorable option for it.

## Rollback to NASUS

The stopped NASUS containers are the rollback path. Do it in this order or you
will create duplicate identity problems.

1. **Disable the rammus watchdog first** — comment the line in
   `/etc/cron.d/newt-watchdog` — otherwise it fights the NASUS `newt`.
2. Stop on rammus: `newt`, `traefik`, `plex`, `qbittorrent`, `prowlarr`,
   `scryer`, `arr-mcp`, and set each to `restart=no`.
3. **Copy back the diverged appdata** or you lose every change since 2026-11-21:
   `/opt/docker/config/{qbittorrent,plex-db,prowlarr,scryer,arr-mcp}` and
   `/opt/docker/qbit-incomplete`. The incomplete-downloads directory exists
   **only** on rammus and has no NASUS counterpart.
4. Start the NASUS containers individually. **Start `newt` last**, after
   everything else is healthy.
5. Repoint the five things that moved: the AdGuard rewrites (7 app names),
   `/etc/hosts` on the CloudNode (6 names), Homarr's `extra_hosts` (6 names),
   the two Pangolin targets (`request`, `plex`), and the OPNsense NAT forwards
   for 32400 and 6881.
6. Re-enable the `newt` watchdog on NASUS (its cron line is present but commented
   out) and disable the rammus copy. Exactly one host may run it.

Point of no return: `docker rm` or image prune on NASUS, deleting
`/volume1/docker/config/*`, or losing `/volume2`.

## Self-healing
`/usr/local/bin/newt-watchdog.sh` runs every minute from
`/etc/cron.d/newt-watchdog`. It starts `newt` if it is not running, and restarts
it when the tunnel interface fails. It moved here from NASUS; a leftover copy on
NASUS used to compete with this host for the same site credentials.

## Networks
- Shared external Docker network: [[../networks/traefik-traefik.md]], subnet `172.19.0.0/16`
- Reachable from the internet: `32400` (Plex, host networking so it binds
  `0.0.0.0` directly) and `6881/tcp+udp` (torrent listening port), plus the
  Pangolin tunnel for HTTP/HTTPS. Both NAT forwards moved from `.10` to `.12` in
  the migration.
- **UFW does not filter published container ports.** Docker's own iptables
  chains run before UFW's, so a `-p 0.0.0.0:port:port` mapping is reachable
  regardless of UFW rules. Rely on the bind address instead: Hawser is bound to
  `192.168.0.12:2375` and dashdot to `192.168.0.12:3003`; `6881` still binds all
  interfaces.

## Access
- SSH: `ssh jesus@rammus`, passwordless `sudo -n`
- Docker API via Hawser on `192.168.0.12:2375`, bound to the LAN address only,
  token required (unauthenticated requests return `401`)
- Rammus **cannot** SSH to NASUS: ADM's `ipblockman` crash-penalty daemon
  blacklists `.12`. Data moves NASUS → rammus under a `nasus-to-rammus` key held
  on NASUS.

## Container network map (`traefik_traefik`, `172.19.0.0/16`)

Docker assigns these dynamically, so re-check before diagnosing anything by IP:

```bash
docker network inspect traefik_traefik --format '{{range .Containers}}{{.Name}} {{.IPv4Address}}{{"\n"}}{{end}}'
```

At 2026-11-21: `traefik .2`, `qbittorrent .3`, `prowlarr .4`, `arr-mcp .5`,
`scryer .6`. Misreading `.2` as scryer once produced a completely wrong
qBittorrent auth diagnosis — `.2` is the Traefik proxy.

## qBittorrent peer access

`scryer` and the CloudNode `qbit-proxy` do **not** send credentials. They rely
entirely on `AuthSubnetWhitelistEnabled=true` with `172.19.0.0/16` listed.
Removing that setting returns `403` to both. After a `403`, scryer back-ends off
for 15–25 minutes and keeps logging `no download client answered` even though
nothing is still broken — check `download_client_status` before re-diagnosing.

## Known operational notes
- `plex` must never run on two hosts at once — both would share `MachineIdentifier`.
- `newt` must never run twice with the same site credentials; duplicate clients
  flap the tunnel and cause intermittent 502s.
- NASUS is storage only. Do not recreate application containers there.

## Hardware transcoding (verified 2026-11-21)

Comet Lake-U / `i915`, `/dev/dri/renderD128`, driver `iHD`. Confirmed working
with a live session: Plex transcoded fully on the GPU.

```
-hwaccel vaapi -hwaccel_device vaapi:/dev/dri/renderD128,driver=iHD
hwupload → deinterlace_vaapi → scale_vaapi(nv12) → hwupload
encoder: h264_vaapi
```

Requirements that must keep holding:
- `renderD128` is owned by `root:render`, **host GID 993** (`video` is 44).
  The container runs as **root** (`Config.User` empty) with `GroupAdd=[]`, so it
  opens the device as root and needs no supplementary group today. The GID only
  matters if the container is ever moved to a non-root user — then
  `group_add: ["993"]` is required, or VAAPI init fails and Plex silently falls
  back to CPU. Verify with
  `docker inspect plex --format '{{.Config.User}} {{.HostConfig.GroupAdd}}'`.
  (Do not read the GID from inside the container: its own `/etc/group` says
  `render:x:994:`, which is unrelated to the host's `993`.)
- `card0` is GID `44` (`video`); passing only `card0` is not enough.
- Capability: H.264 and HEVC 8-bit/10-bit decode **and** encode. No AV1.

Verify a session is really on the GPU instead of trusting the Plex UI:

```bash
ps -eo args | grep "[P]lex Transcoder" | tr ' ' '\n' | grep -E "vaapi|_vaapi"
```

A CPU transcode shows plain `libx264`/`libx265` with no `vaapi` entries.

To find out *why* Plex decided to transcode, the reason is in the server log, not
the UI. Grep for `MDE:` and `Decision`:

```bash
docker exec plex sh -c 'tail -n 6000 "/config/Library/Application Support/Plex Media Server/Logs/Plex Media Server.log"' \
  | grep -aE "MDE:|Decision" | tail -12
```

Lines like `Direct Play is disabled` or `Direct Streaming is disabled` are
client-side settings, not server problems — the client asked for a transcode. A
fixed quality/bitrate in the client does the same thing.
