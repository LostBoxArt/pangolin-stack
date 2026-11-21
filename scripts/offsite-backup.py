#!/usr/bin/env python3
"""Copy completed private backups between the VPS and NAS; never prune."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import tarfile


HOME = Path.home()
RESTIC = HOME / ".local/bin/restic-0.19.1"
CONFIG = HOME / ".config/homelab-backups"
STATE = HOME / ".local/state/homelab-backups"
CACHE = HOME / ".cache/homelab-restic"
BACKUPS = Path("/opt/homelab/backups")
NAS = os.environ.get("HOMELAB_BACKUP_NAS", "admin@192.168.1.10")
PROXY = shlex.join(["python3", str(HOME / ".local/lib/homelab-backups/ssh-bind-olm.py"), "%h", "%p"])
SSH_OPTIONS = ["-o", "BatchMode=yes", "-o", "StrictHostKeyChecking=yes", "-o", "ConnectTimeout=15", "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4", "-o", "ProxyCommand=" + PROXY]
SFTP_OPTIONS = "sftp.args=" + shlex.join(SSH_OPTIONS)


def run(command, log):
    result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"command failed with exit {result.returncode}; see private log")


def restic(repository, password, *arguments):
    return [str(RESTIC), "-r", repository, "--password-file", str(CONFIG / password), "--cache-dir", str(CACHE), "-o", SFTP_OPTIONS, *arguments]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def backup_vps(log, full_check):
    archives = sorted(BACKUPS.glob("pangolin-backup_????????_??????.tar.gz"))
    if not archives:
        raise RuntimeError("no completed VPS archive")
    archive = archives[-1]
    age = datetime.datetime.now().timestamp() - archive.stat().st_mtime
    if not 0 <= age <= 26 * 3600:
        raise RuntimeError("latest completed VPS archive is stale")
    if archive.stat().st_mode & 0o077:
        raise RuntimeError("VPS archive permissions are not private")
    # Read every member before publishing the archive off-host.
    with tarfile.open(archive, "r:gz") as saved:
        for member in saved:
            if member.isfile():
                stream = saved.extractfile(member)
                while stream.read(1024 * 1024):
                    pass
    repo = f"sftp:{NAS}:/volume1/backups/restic-vps-pangolin"
    run(restic(repo, "vps-restic.password", "backup", "--host", "cloudnode", "--tag", "pangolin-stack", str(archive)), log)
    run(restic(repo, "vps-restic.password", "check", *(["--read-data"] if full_check else [])), log)
    return {"archive": str(archive), "sha256": sha256(archive)}


def backup_nas(log):
    run(["ssh", *SSH_OPTIONS, NAS, 'exec "$HOME/.local/bin/backup-nasus-config"'], log)
    source = f"sftp:{NAS}:/volume1/backups/restic-nasus-config"
    target = str(BACKUPS / "restic-nasus-config")
    if not (Path(target) / "config").exists():
        run(restic(target, "nasus-restic.password", "init", "--from-repo", source, "--from-password-file", str(CONFIG / "nasus-restic.password"), "--copy-chunker-params"), log)
    run(restic(target, "nasus-restic.password", "copy", "--from-repo", source, "--from-password-file", str(CONFIG / "nasus-restic.password")), log)
    run(restic(target, "nasus-restic.password", "check", "--read-data"), log)
    return {"source_repository": source, "recovery_repository": target}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["vps", "nas"])
    parser.add_argument("--full-check", action="store_true")
    args = parser.parse_args()
    os.umask(0o077)
    for directory in [STATE, CACHE]:
        directory.mkdir(parents=True, exist_ok=True)
        directory.chmod(0o700)
    # A single lock also prevents the two timers competing for disk/network I/O.
    with (STATE / "offsite.lock").open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        stamp = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        result = {"mode": args.mode, "started": stamp, "success": False}
        log_path = STATE / f"{args.mode}-{stamp}.log"
        try:
            with log_path.open("wb") as log:
                result.update(backup_vps(log, args.full_check) if args.mode == "vps" else backup_nas(log))
            result["success"] = True
        finally:
            result["private_log"] = str(log_path)
            pending = STATE / f"{args.mode}-latest.json.partial"
            pending.write_text(json.dumps(result, indent=2) + "\n")
            pending.replace(STATE / f"{args.mode}-latest.json")
        print(f"{args.mode} off-host backup and repository check passed")


if __name__ == "__main__":
    main()
