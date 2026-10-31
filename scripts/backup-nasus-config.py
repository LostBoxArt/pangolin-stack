#!/usr/bin/env python3
"""Stage read-only container configuration with consistent individual SQLite backups."""
import argparse
from contextlib import closing
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import stat
import tempfile
import time


def excluded(path):
    parts = [p.casefold() for p in Path(path).parts]
    return any('fileflows' in p for p in parts) or '/plex/library/application support/plex media server/cache' in str(path).casefold()


def historical_database(path):
    path = Path(path)
    return (path.name.endswith('.empty') or
            ('/jellyseerr/db/' in str(path) and path.name.startswith('pre-')) or
            ('/plex/' in str(path).casefold() and re.fullmatch(r'com\.plexapp\.plugins\.library(?:\.blobs)?\.db-\d{4}-\d{2}-\d{2}', path.name)))


def diagnostic_database(path):
    return str(path) in {
        '/volume1/docker/config/' + app + '/logs.db' + suffix
        for app in ('sonarr', 'radarr', 'prowlarr')
        for suffix in ('', '-wal', '-shm', '-journal')
    }


def sha256_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def verify_historical_inactive(root, proc_root=Path('/proc')):
    files = {p: p.stat() for p in root.rglob('*') if p.is_file() and historical_database(p)}
    identities = {(info.st_dev, info.st_ino) for info in files.values()}
    checked = 0
    for process in proc_root.glob('[0-9]*'):
        try:
            descriptors = list((process / 'fd').iterdir())
        except FileNotFoundError:
            continue
        for descriptor in descriptors:
            try:
                info = descriptor.stat()
            except FileNotFoundError:
                continue
            checked += 1
            if (info.st_dev, info.st_ino) in identities:
                raise RuntimeError('Historical database is open in application process')
    result = {}
    for path, info in files.items():
        if time.time() - info.st_mtime < 86400 or any(Path(str(path) + suffix).exists() for suffix in ('-wal', '-journal')):
            raise RuntimeError('Historical database is recent or has active journal: ' + str(path))
        result[str(path)] = {'size': info.st_size, 'mtime_ns': info.st_mtime_ns, 'inode': info.st_ino, 'device': info.st_dev}
    return {'files': result, 'open_fds_checked': checked, 'proof': 'No matching open descriptor in application PID namespace at check time'}


def configuration_roots(inventory):
    roots, compose, mappings = set(), [], []
    for item in inventory:
        if 'fileflows' in item['name'].casefold():
            raise RuntimeError('Retired FileFlows container is unexpectedly active')
        for mount in item['mounts']:
            source, destination = mount['Source'], mount['Destination']
            if mount['Type'] == 'volume':
                if destination not in ('/config', '/data/stacks'):
                    raise RuntimeError('Unclassified active Docker volume: ' + destination)
                roots.add(source)
                mappings.append((destination, source))
            elif mount['Type'] == 'bind' and source.startswith(('/volume1/docker/', '/volume2/fast/docker-config/')):
                roots.add(source)
        compose += [p for p in (item.get('compose') or '').split(',') if p]
    resolved = []
    for path in compose:
        if not path.startswith(('/volume1/', '/volume2/')):
            matches = [(dest, source) for dest, source in mappings if path.startswith(dest + '/')]
            if len(matches) != 1:
                raise RuntimeError('Cannot map active Compose path: ' + path)
            dest, source = matches[0]
            path = source + path[len(dest):]
        roots.add(str(Path(path).parent))
        resolved.append(path)
    roots = {p for p in roots if not excluded(p)}
    for p in roots:
        if not p.startswith(('/volume1/docker/', '/volume1/.@plugins/', '/volume2/fast/docker-config/')):
            raise RuntimeError('Unexpected configuration source: ' + p)
    ordered = sorted(roots, key=lambda p: (len(Path(p).parts), p))
    unique = [p for p in ordered if not any(Path(p).is_relative_to(Path(q)) for q in ordered if q != p and len(Path(q).parts) < len(Path(p).parts))]
    return unique, resolved


def sqlite_snapshot(source, target, plex=False):
    began = time.monotonic()
    def progress(status, remaining, total):
        if time.monotonic() - began > 120:
            raise TimeoutError('SQLite backup exceeded two minutes')
    with closing(sqlite3.connect(source.as_uri() + '?mode=ro', uri=True, timeout=15)) as src:
        with closing(sqlite3.connect(target)) as dst:
            src.backup(dst, pages=512, progress=progress, sleep=0.05)
            dst.execute('PRAGMA journal_mode=DELETE').fetchone()
            if not plex:
                rows = [r[0] for r in dst.execute('PRAGMA integrity_check')]
                if rows != ['ok']:
                    raise RuntimeError('SQLite snapshot integrity check failed: ' + str(source))


def stage(inventory, source_prefix, destination, uid, gid, additional_sources=(), historical_proofs=None):
    roots, compose = configuration_roots(inventory)
    roots += list(additional_sources)
    if destination.is_symlink():
        raise RuntimeError('Staging directory must not be a symlink')
    destination.mkdir(mode=0o700, parents=True, exist_ok=True)
    os.chown(destination, uid, gid)
    kept, metadata, databases, warnings, artifacts, exclusions = set(), {}, [], [], [], []
    def directory(path):
        if path == destination:
            return
        directory(path.parent)
        if path.is_symlink() or path.is_file():
            path.unlink()
        path.mkdir(mode=0o700, exist_ok=True)
        path.chmod(0o700)
        os.chown(path, uid, gid)
        kept.add(str(path.relative_to(destination)))
    def record(source, target, info):
        relative = str(target.relative_to(destination))
        kept.add(relative)
        metadata[relative] = {'uid': info.st_uid, 'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode), 'mtime_ns': info.st_mtime_ns, 'size': info.st_size}
    for root in roots:
        source_root = source_prefix / root.lstrip('/')
        if not source_root.exists():
            raise FileNotFoundError('Required configuration root missing: ' + root)
        paths = [source_root]
        if source_root.is_dir():
            paths = []
            for folder, dirs, files in os.walk(source_root, followlinks=False):
                dirs[:] = [n for n in dirs if not excluded(Path(folder) / n)]
                paths.append(Path(folder))
                paths += [Path(folder) / n for n in files + dirs if (Path(folder) / n).is_symlink() or n in files]
        for source in paths:
            host_path = '/' + str(source.relative_to(source_prefix))
            if excluded(host_path):
                continue
            if diagnostic_database(host_path):
                exclusions.append(host_path)
                continue
            target = destination / source.relative_to(source_prefix)
            info = source.lstat()
            if stat.S_ISDIR(info.st_mode):
                directory(target)
                record(source, target, info)
                continue
            directory(target.parent)
            if stat.S_ISLNK(info.st_mode):
                if target.is_symlink() or target.exists():
                    if target.is_dir() and not target.is_symlink():
                        shutil.rmtree(target)
                    else:
                        target.unlink()
                os.symlink(os.readlink(source), target)
                os.lchown(target, uid, gid)
                record(source, target, info)
                continue
            if not stat.S_ISREG(info.st_mode):
                warnings.append('Excluded non-regular file: ' + host_path)
                continue
            if source.name.endswith(('-wal', '-shm', '-journal')):
                continue  # SQLite's online backup incorporates committed WAL data.
            fd, temporary = tempfile.mkstemp(prefix='.snapshot-', dir=target.parent)
            os.close(fd)
            temporary = Path(temporary)
            try:
                with source.open('rb') as src:
                    header = src.read(16)
                    sqlite = header == b'SQLite format 3\x00' or (not header and Path(str(source) + '-wal').exists())
                    if not sqlite:
                        with temporary.open('wb') as dst:
                            dst.write(header)
                            shutil.copyfileobj(src, dst, length=1024 * 1024)
                if sqlite:
                    plex = '/plex/' in host_path.casefold()
                    if historical_database(source):
                        # Preserve explicitly named historical databases as artifacts.
                        # These are not the application's active database files.
                        if any(Path(str(source) + suffix).exists() for suffix in ('-wal', '-journal')):
                            raise RuntimeError('Historical database has active journal: ' + host_path)
                        expected = (historical_proofs or {}).get(str(source))
                        actual = {'size': info.st_size, 'mtime_ns': info.st_mtime_ns, 'inode': info.st_ino, 'device': info.st_dev}
                        if expected != actual:
                            raise RuntimeError('Historical database lacks current inactivity proof: ' + host_path)
                        shutil.copyfile(source, temporary)
                        if source.stat().st_mtime_ns != info.st_mtime_ns or source.stat().st_size != info.st_size or any(Path(str(source) + suffix).exists() for suffix in ('-wal', '-journal')):
                            raise RuntimeError('Historical database changed during copy: ' + host_path)
                        artifacts.append({'path': str(target.relative_to(destination)), 'sha256': sha256_file(temporary), 'validation': 'Historical raw artifact; not an online snapshot or integrity-validated database'})
                    else:
                        try:
                            sqlite_snapshot(source, temporary, plex=plex)
                        except sqlite3.Error as error:
                            raise RuntimeError('SQLite snapshot failed: ' + host_path + ': ' + str(error)) from None
                        databases.append({'path': str(target.relative_to(destination)), 'validation': 'plex-pending' if plex else 'integrity-ok'})
                elif source.stat().st_size != info.st_size or source.stat().st_mtime_ns != info.st_mtime_ns:
                    if source.suffix.casefold() == '.log' or '/logs/' in host_path.casefold():
                        warnings.append('Log changed during copy: ' + host_path)
                    else:
                        raise RuntimeError('Configuration changed during copy; rerun backup: ' + host_path)
                temporary.chmod(0o600)
                os.chown(temporary, uid, gid)
                os.replace(temporary, target)
                record(source, target, info)
            finally:
                if temporary.exists():
                    temporary.unlink()
    for path in compose:
        if not (destination / path.lstrip('/')).is_file():
            raise FileNotFoundError('Required active Compose file missing from stage: ' + path)
    if not databases:
        raise RuntimeError('No SQLite databases found; refusing incomplete backup')
    # Remove obsolete private staging files only, never any live source or repository data.
    for folder, dirs, files in os.walk(destination, topdown=False, followlinks=False):
        for name in files + dirs:
            path = Path(folder) / name
            if str(path.relative_to(destination)) not in kept:
                if path.is_dir() and not path.is_symlink():
                    path.rmdir()
                else:
                    path.unlink()
    manifest = {'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()), 'consistency': 'Individual SQLite online snapshots; not a globally atomic multi-application snapshot', 'roots': roots, 'compose_files': compose, 'files': metadata, 'databases': databases, 'historical_sqlite_artifacts': artifacts, 'diagnostic_database_exclusions': exclusions, 'warnings': warnings, 'owner_normalized_to': {'uid': uid, 'gid': gid}}
    path = destination / 'BACKUP-MANIFEST.json'
    path.write_text(json.dumps(manifest, indent=2))
    path.chmod(0o600)
    os.chown(path, uid, gid)
    print(json.dumps({'staged_files': len(metadata), 'sqlite_snapshots': len(databases), 'plex_pending': sum(d['validation'] == 'plex-pending' for d in databases), 'warnings': len(warnings)}), flush=True)
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory', default='/inventory.jsonl')
    parser.add_argument('--source-prefix', default='/source')
    parser.add_argument('--destination', default='/backup-stage/current')
    parser.add_argument('--owner-uid', type=int)
    parser.add_argument('--owner-gid', type=int)
    parser.add_argument('--host-home')
    parser.add_argument('--verify-historical-root')
    parser.add_argument('--historical-proof-directory')
    args = parser.parse_args()
    if args.verify_historical_root:
        print(json.dumps(verify_historical_inactive(Path(args.verify_historical_root))))
        return
    if args.owner_uid is None or args.owner_gid is None:
        parser.error('--owner-uid and --owner-gid are required when staging')
    inventory = [json.loads(line) for line in Path(args.inventory).read_text().splitlines() if line.strip()]
    extra = []
    if args.host_home:
        extra = ['/usr/local/bin/newt-watchdog.sh', '/usr/local/bin/docker',
                 '/usr/builtin/etc/crontabs/root',
                 args.host_home + '/.local/bin/backup-nasus-config',
                 args.host_home + '/.local/lib/homelab-backups/backup-nasus-config.py']
    destination = Path(args.destination)
    proofs = {}
    if args.historical_proof_directory:
        for path in Path(args.historical_proof_directory).glob('*.json'):
            proofs.update(json.loads(path.read_text())['files'])
    manifest = stage(inventory, Path(args.source_prefix), destination, args.owner_uid, args.owner_gid, extra, proofs)
    if args.host_home:
        vendor = Path(args.source_prefix) / 'usr/local/AppCentral/docker-ce/bin/docker'
        info = vendor.stat()
        manifest['recovery_provenance'] = {
            'restic_version': '0.19.1',
            'restic_sha256': '20d4142678d0d95ec11a4759def1b73fd9190abc9ca19e4b62d067c0b387e639',
            'restic_release': 'https://github.com/restic/restic/releases/tag/v0.19.1',
            'docker_vendor_executable': {'path': '/usr/local/AppCentral/docker-ce/bin/docker', 'uid': info.st_uid, 'gid': info.st_gid, 'mode': stat.S_IMODE(info.st_mode), 'size': info.st_size, 'mtime_ns': info.st_mtime_ns},
            'runtime_secrets_file': 'runtime/services.json',
        }
        (destination / 'BACKUP-MANIFEST.json').write_text(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
