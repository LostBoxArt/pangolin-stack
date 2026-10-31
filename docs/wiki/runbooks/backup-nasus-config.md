---
title: "NAS configuration backup and recovery"
slug: runbook-backup-nasus-config
type: runbook
status: active
tags: ["homelab", "runbook", "backup", "restic", "sqlite"]
aliases: ["NAS backup", "HomeNode configuration recovery"]
entities:
  primary: runbook-backup-nasus-config
  mentions: []
related: ["../services-homenode/plex.md", "../maintenance-2026-10-31.md"]
sources: ["scripts/backup-nasus-config", "scripts/backup-nasus-config.py", "tests/test_nasus_backup.py"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-10-27
---
# NAS configuration backup and recovery

The installed command is `$HOME/.local/bin/backup-nasus-config` on HomeNode.
The engine is `$HOME/.local/lib/homelab-backups/backup-nasus-config.py`.
Repository sources are `scripts/backup-nasus-config`,
`scripts/backup-nasus-config.py`, and `tests/test_nasus_backup.py`.

Run the command as the NAS administrative user. The CloudNode's weekly backup
runner invokes it over SSH; do not add a second NAS cron job.

```bash
$HOME/.local/bin/backup-nasus-config
```

A successful run returns zero after staging, database validation, restic backup,
and `restic check`. It prints counts and the final restic summary, including the
snapshot ID. The command takes a nonblocking lock and returns 75 if another run
is active. A failed source read, required Compose file, primary database snapshot,
integrity check, or container replacement aborts publication.

## Included recovery state

The script discovers running containers' bind mounts, configuration volumes, and
actual Compose labels. It includes active configuration roots under
`/volume1/docker/`, managed stack Compose files inside Hawser's `/data/stacks`
volume, and FlareSolverr's configuration volume. If configurations later move to
`/volume2/fast/docker-config/`, that prefix is also recognized. Unknown persistent
volume destinations fail for review.

It includes the actual Traefik and Hawser Compose parents, Seerr's `jellyseerr`
data directory as well as its separate Compose parent, and these host files:

- `/usr/local/bin/newt-watchdog.sh`
- `/usr/local/bin/docker`, preserving its bytes and original metadata
- `/usr/builtin/etc/crontabs/root`
- The installed backup wrapper and engine

The manifest records metadata for the vendor Docker executable at
`/usr/local/AppCentral/docker-ce/bin/docker`, without copying or rewriting it.
It also records the pinned restic 0.19.1 release and verified SHA256. Obtain that
binary from its official signed release during a rebuild.

`runtime/services.json` contains image IDs, complete environment arrays, Compose
labels, and mount definitions. It is necessary for cold recovery of managed
stacks whose Compose files refer to variables held in CloudNode Dockhand.
**This file contains credentials. Never print it, commit it, or attach it to a
public diagnostic report.** Stage directories use mode 0700 and files 0600.

## Consistency and exclusions

Every primary SQLite database is opened read-only through SQLite's online backup
API. Committed WAL transactions are included. Each ordinary database snapshot
must pass full `PRAGMA integrity_check`; the two current Plex databases must pass
the bundled `Plex SQLite` integrity check. Live mounts are read-only. Applications
are neither stopped nor paused. The result is consistent per database, rather
than one globally atomic transaction across applications and text files.

Only these reconstructible diagnostic databases and their `-wal`, `-shm`, and
`-journal` files are excluded from the configuration restore set:

- `/volume1/docker/config/sonarr/logs.db`
- `/volume1/docker/config/radarr/logs.db`
- `/volume1/docker/config/prowlarr/logs.db`

These applications' native backup implementations back up the main database and
configuration file; diagnostic logs are separate. Text logs remain included.
`arr-mcp/logs.db`, `arr-mcp/audit.db`, and every primary application database remain
subject to the snapshot and integrity gates. The script never uses `immutable=1`
on a live database or grants write permission to live SQLite sidecars.

Explicitly named older Seerr and Plex database archives are retained as raw,
SHA256-recorded historical artifacts. They are **not** claimed to be online
snapshots or integrity-validated recovery databases. Before copying them, a
helper checks descriptor metadata in the respective application's PID namespace,
requires no matching open descriptor, no WAL/journal, and an age over 24 hours.
It does not attach a debugger or enter the host PID namespace. Inode, size, and
modification time must still match when copied.

Shared media/downloads, device/system mounts, retired FileFlows data, and Plex's
`Library/Application Support/Plex Media Server/Cache` are excluded. This backs up
configuration and recovery state, not the media library or container images.

## Locations and verification

| Item | NAS path |
| --- | --- |
| Stable private stage | `/volume1/backups/.nasus-config-stage/current` |
| Manifest | `current/BACKUP-MANIFEST.json` below the staging parent |
| Private runtime credentials | `current/runtime/services.json` |
| Local encrypted repository | `/volume1/backups/restic-nasus-config` |
| Password file | `$HOME/.config/homelab-backups/nasus-restic.password` |
| Lock | `$HOME/.local/state/homelab-backups/nasus-config.lock` |

The repository and its password require independent recovery copies. The stage
and repository share the NAS storage system; the CloudNode's native restic copy
provides the separate host copy. This command never runs `forget` or `prune`.

Run source tests without NAS access:

```bash
python3 tests/test_nasus_backup.py
sh -n scripts/backup-nasus-config
```

The test suite must pass eight tests, including committed WAL recovery without
source changes, exact diagnostic database exclusions, archived-file identity
checks, and rejection of an archive opened by an application process.

## Restore into an isolated directory first

On the NAS, select an existing snapshot ID from the encrypted repository and
restore into a fresh private directory. This does not write to active paths.

```bash
umask 077
RESTIC="$HOME/.local/bin/restic-0.19.1"
RESTIC_REPOSITORY=/volume1/backups/restic-nasus-config
RESTIC_PASSWORD_FILE="$HOME/.config/homelab-backups/nasus-restic.password"
export RESTIC_REPOSITORY RESTIC_PASSWORD_FILE
"$RESTIC" snapshots
read -r SNAPSHOT
RESTORE_ROOT=$(mktemp -d "$HOME/nasus-restore-check.XXXXXX")
"$RESTIC" restore "$SNAPSHOT" --target "$RESTORE_ROOT" --verify
test -f "$RESTORE_ROOT/volume1/backups/.nasus-config-stage/current/BACKUP-MANIFEST.json"
```

Validate the recovered primary databases with the same SQLite and Plex tools
before any live restore. Normalized staged ownership is the NAS backup user's
UID/GID. `BACKUP-MANIFEST.json` records original UID, GID, mode, and modification
time for source files and directories. Apply those original values to the
selected restored application's files before starting that application; do not
copy the normalized staging permissions blindly over live data. Symlinks need
`lchown` rather than following their targets.

A live recovery needs an explicit maintenance window: stop only the affected
application, retain its current files as a rollback generation, restore its main
database and configuration into a **fresh application directory**, restore
original ownership/modes, and start it with
the recorded image and current credentials. Validate the application's native
health/API and its integrations before discarding rollback data. Do not restore
over a destination containing old `-wal`, `-shm`, or `-journal` files: a stale WAL
can override the restored main database. Move the complete old application
directory aside before preparing the fresh replacement. Do not restore
historical SQL artifacts over a primary database automatically. Restore root
cron or vendor-wrapper files only after reviewing their current host paths and
permissions; do not overwrite vendor binaries from this backup.

## Verified isolated restore rehearsal

On 2026-10-27, snapshot `c8f7ec4e` was restored into a fresh private directory.
Restic verified all 22,819 recovered files, and original UID/GID/mode metadata was
applied to 30,237 file and directory entries before application startup.

One application clone ran at a time, using its recorded cached image and restored
configuration, on an internal Docker network with no published ports or live
application, media, device, or Docker socket mounts. CPU was capped at one core,
with at most 1.5 GiB application memory. Native probes used the clone's own
network namespace and loopback interface, with proxy forwarding disabled.

| Restored application | Passed native/local data checks |
| --- | --- |
| Sonarr | HTTP 200 system status and series API; three durable table counts |
| Radarr | HTTP 200 system status and movie API; three durable table counts |
| Prowlarr | HTTP 200 system status and indexer API; two durable table counts |
| Bazarr | HTTP 200 native ping and authenticated local languages API; three durable table counts |
| Seerr | HTTP 200 local status and authenticated user API; three durable table counts |
| Plex | HTTP 200 identity matching the restored processed identifier and authenticated library sections; two durable table counts |

The 16 selected durable table counts matched the original restored snapshot.
Seerr's status probe used the documented
`/api/v1/status?checkUpdateAvailable=false`: the default status request performs an
external GitHub release check and timed out in isolation, despite the server
being ready. This query changes no saved setting. Bazarr's full system-status
endpoint calls its configured Sonarr and Radarr servers, so the authenticated
local languages/database endpoint was used instead. These distinctions prevent
an unavailable external dependency from being mistaken for a failed restore.

All rehearsal containers and their internal network were removed afterward.
The production containers were neither stopped nor restarted. This verifies
startup, native local APIs, restored credentials where used, and selected
database state. It does not exercise playback, downloads, subtitle providers,
external indexers, tunnel clients, or a complete multi-host disaster recovery.
Profilarr and arr-mcp databases passed snapshot integrity checks; those
applications were not started as part of this rehearsal.

References: [SQLite online backup API](https://www.sqlite.org/backup.html),
[SQLite read-only WAL requirements](https://www.sqlite.org/wal.html#read_only_databases),
[Sonarr native backup source](https://github.com/Sonarr/Sonarr/blob/develop/src/NzbDrone.Core/Backup/BackupService.cs),
[Radarr native backup source](https://github.com/Radarr/Radarr/blob/develop/src/NzbDrone.Core/Backup/BackupService.cs),
[Prowlarr native backup source](https://github.com/Prowlarr/Prowlarr/blob/develop/src/NzbDrone.Core/Backup/BackupService.cs),
[Plex's bundled SQLite guidance](https://support.plex.tv/articles/repair-a-corrupted-database/),
[Bazarr local languages API](https://github.com/morpheus65535/bazarr/blob/master/bazarr/api/system/languages.py),
[Bazarr system-status dependencies](https://github.com/morpheus65535/bazarr/blob/master/bazarr/api/system/status.py),
[Seerr 3.5.1 API specification](https://github.com/seerr-team/seerr/blob/v3.5.1/seerr-api.yml),
[Seerr status handler](https://github.com/seerr-team/seerr/blob/v3.5.1/server/routes/index.ts),
[restic repository/password handling](https://restic.readthedocs.io/en/stable/030_preparing_a_new_repo.html).
