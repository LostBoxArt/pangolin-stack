---
title: "Encrypted backup and recovery"
slug: runbook-backup-recovery
type: runbook
status: active
tags: ["homelab", "runbook", "backup", "restic", "sqlite"]
aliases: ["CloudNode backup", "Encrypted off-host recovery"]
entities:
  primary: runbook-backup-recovery
  mentions: []
related: ["backup-nasus-config.md"]
sources: ["backup.sh", "scripts/offsite-backup.py", "tests/test_backup_restore.py", "tests/test_backup_prune.py"]
confidence: high
audience_level: operator
last_ingested: 2026-10-27
last_lint: 2026-10-27
---
# Encrypted backup and recovery

The local CloudNode archive contains six independent online SQLite snapshots:
Pangolin, Pocket ID, Dockhand, Homarr, CrowdSec, and CrowdSec Web UI. They are
individually consistent; they are not one transaction across all applications.
The archive also contains private runtime settings, image identities, the local
qbit-proxy image, Traefik plugin cache, and allowlisted host recovery files.

Treat archives, extracted runtime metadata, and recovery files as credentials.
Keep the parent directory mode `0700` and archive/password files mode `0600`.
Never paste runtime JSON, `.env`, bouncer configuration, or passwords into logs.

## Installed schedules

The existing local backup runs at 03:00 in the VPS timezone. The new user timers
run the encrypted VPS copy at 03:40 daily and the NAS snapshot/recovery copy at
05:00 Saturday, both explicitly in `Asia/Jerusalem`. They require user lingering.
The weekly job also performs a full data read of the VPS repository.
No restic forget/prune policy is installed. The existing local seven-day policy
continues, with a fresh valid archive required before pruning and a minimum of
two validated generations retained. If either protected generation fails
validation, pruning refuses every deletion. Maintenance runs use
`RETAIN_DAYS=0`; no live prune is part of the maintenance verification.

Source defaults are sanitized. Deployment must create the private file
`~/.config/homelab-backups/offsite.env` with the actual existing SSH destination:

```sh
HOMELAB_BACKUP_NAS=admin@192.168.1.10
```

The installed runner is `~/.local/bin/offsite-backup`. It uses the signed and
checksum-verified restic `0.19.1` binary at `~/.local/bin/restic-0.19.1`.
Provenance is in `~/.config/homelab-backups/restic-version.json`.
The VPS runner uses the installed `~/.local/lib/homelab-backups/ssh-bind-olm.py`
as an SSH ProxyCommand for NAS traffic. This binds only that connection to Olm;
the default route otherwise nests Tailscale inside Olm and caused severe TCP
retransmissions. The tested connected upload improved from about 0.032 to
1.63 MiB/s. The proxy fails if Olm is unavailable and changes no global route,
interface MTU, or service configuration. Independent recovery computers use
their own trusted SSH path.
Password files are `vps-restic.password` and `nasus-restic.password` in that same
private directory. Independent password copies are on the maintenance Mac,
outside both repositories, under the private maintenance folder's
`phase2/backup/recovery/`. Losing those copies and the host copies loses recovery.

```sh
systemctl --user list-timers 'homelab-offsite-*'
systemctl --user show homelab-offsite-vps.service homelab-offsite-nas.service -p Result -p ExecMainStatus
loginctl show-user "$USER" -p Linger
cat "$HOME/.local/state/homelab-backups/vps-latest.json"
cat "$HOME/.local/state/homelab-backups/nas-latest.json"
```

Successful jobs report `success: true`; logs remain in the same private state
directory. A failed job exits nonzero and does not prune earlier snapshots.

## Restore a repository into a fresh private directory

Run on the VPS with its existing private key files and SSH trust. On an
independent recovery computer, first install the verified matching restic
binary and recover the password files and private connection configuration.
Never restore over a live application directory.

```sh
set -eu
umask 077
. "$HOME/.config/homelab-backups/offsite.env"
RESTIC="$HOME/.local/bin/restic-0.19.1"
RECOVERY="$HOME/recovery-$(date +%Y%m%dT%H%M%S)"
mkdir -m 700 "$RECOVERY"
"$RESTIC" -r "sftp:${HOMELAB_BACKUP_NAS}:/volume1/backups/restic-vps-pangolin" \
  --password-file "$HOME/.config/homelab-backups/vps-restic.password" \
  -o 'sftp.args=-o BatchMode=yes -o StrictHostKeyChecking=yes' check --read-data
"$RESTIC" -r "sftp:${HOMELAB_BACKUP_NAS}:/volume1/backups/restic-vps-pangolin" \
  --password-file "$HOME/.config/homelab-backups/vps-restic.password" \
  -o 'sftp.args=-o BatchMode=yes -o StrictHostKeyChecking=yes' restore latest --target "$RECOVERY/vps"
"$RESTIC" -r /opt/homelab/backups/restic-nasus-config \
  --password-file "$HOME/.config/homelab-backups/nasus-restic.password" \
  check --read-data
"$RESTIC" -r /opt/homelab/backups/restic-nasus-config \
  --password-file "$HOME/.config/homelab-backups/nasus-restic.password" \
  restore latest --target "$RECOVERY/nas"
```

The NAS repository on the VPS is an independent native restic copy of
`/volume1/backups/restic-nasus-config`; copying uses repository locks rather
than copying a changing repository with rsync. See
[NAS configuration recovery](backup-nasus-config.md) for its coverage and
explicit exclusions. Media/download payloads are not included.

## Restore CloudNode data and start reviewed images

First extract the recovered archive into a fresh private directory. Compare
its SHA256 with the recorded source archive hash. Check all six databases and
review the private runtime/image metadata. Load the archived local image with
`docker image load --input runtime/qbit-proxy-image.tar`; obtain other recorded
images by their recorded registry digest if they are not cached. Verify every
image ID before restoring. Never pull a moving tag during recovery.

`sudo ./backup.sh restore /absolute/path/to/archive.tar.gz` restores data only.
The deployed script's `STACK_DIR` must point to the actual installation before
running it. It validates copied SQLite snapshots and image availability before
shutdown, requires successful shutdown and an empty stack-container inventory,
then replaces data, removes matching destination WAL/SHM/rollback journals, and
applies captured ownership. It preserves the current recovery tool. A failure
leaves services stopped for diagnosis; it never starts them automatically.

Host recovery files and private runtime metadata are placed in the printed
`restored-recovery_*` directory. Root service units/credentials, host firewall
bouncer configuration, watchdogs, and SSH tunnel units require separate review
and installation. The captured host bouncer package was
`crowdsec-firewall-bouncer-iptables 0.0.34`; restore its matching package/policy
and configuration before claiming equivalent host firewall protection.

Do not use `startup.sh` for recovery: it pulls images. The following complete
command generates a private startup script using only captured image IDs and
only services present in the backup. Set its two arguments to the deployed
stack and the printed private recovery directory. It refuses missing cached
images and does not start services while generating the script.

```sh
python3 - /opt/homelab /opt/homelab/backups/restored-recovery_TIMESTAMP <<'PY'
import json
import os
from pathlib import Path
import shlex
import subprocess
import sys

stack, recovery = map(lambda value: Path(value).resolve(), sys.argv[1:])
os.umask(0o077)
runtime = json.loads((recovery / 'runtime/services.json').read_text())
for service in runtime['services'].values():
    subprocess.run(['docker', 'image', 'inspect', service['image_id']],
                   check=True, stdout=subprocess.DEVNULL)
commands = ['#!/bin/sh', 'set -eu']
covered = set()
for name in ['core', 'security', 'management', 'dns', 'observability', 'dashboard', 'apps']:
    compose = stack / 'stacks' / name / 'docker-compose.yml'
    if not compose.exists():
        continue
    base = ['docker', 'compose', '--env-file', str(stack / '.env'), '-f', str(compose)]
    names = subprocess.check_output(base + ['config', '--services'], text=True).split()
    selected = [item for item in names if item in runtime['services']]
    if not selected:
        continue
    overrides = {'services': {item: {'image': runtime['services'][item]['image_id'],
                                    'pull_policy': 'never'} for item in selected}}
    if 'crowdsec' in selected:
        # Boot restored rules directly; the image bootstrap otherwise installs
        # parsers and can update rules. Review normal hub policy afterward.
        overrides['services']['crowdsec'].update(
            entrypoint=['crowdsec'], command=['-c', '/etc/crowdsec/config.yaml'])
    path = recovery / ('images-' + name + '.json')
    path.write_text(json.dumps(overrides))
    commands.append(shlex.join(base + ['-f', str(path), 'up', '-d', '--pull', 'never',
                                      '--no-build', '--wait', '--wait-timeout', '180', *selected]))
    covered.update(selected)
if covered != set(runtime['services']):
    raise RuntimeError('some recorded services have no reviewed Compose mapping')
script = recovery / 'start-reviewed-images.sh'
script.write_text('\n'.join(commands) + '\n')
script.chmod(0o700)
print(script)
PY
```

Review the generated script, then run it in the normal maintenance window and
verify core health before proceeding to dependent applications. Inspect the
Pangolin/Gerbil/Traefik namespace relationship, CrowdSec bouncers and rules,
authentication, tunnel routes, and external endpoints separately. The isolated
application rehearsal verifies application data and startup, not production
DNS, ACME renewal, firewall enforcement, VPN reachability, or external media
integrations. Archives without runtime metadata require explicit image and
ownership review; exact-image startup cannot be inferred from old archives.

## Roll back the new schedules

```sh
systemctl --user disable --now homelab-offsite-vps.timer homelab-offsite-nas.timer
```

This stops future scheduled copies without deleting archives, repositories,
snapshots, credentials, or the existing local backup timer.

Supported mechanisms: [SQLite online backup](https://www.sqlite.org/backup.html),
[restic recovery](https://restic.readthedocs.io/en/stable/050_restore.html),
[restic repository copy](https://restic.readthedocs.io/en/stable/045_working_with_repos.html#copying-snapshots-between-repositories),
[Docker image save](https://docs.docker.com/reference/cli/docker/image/save/),
[Docker image load](https://docs.docker.com/reference/cli/docker/image/load/), and
[Compose no-pull startup](https://docs.docker.com/reference/cli/docker/compose/up/).
