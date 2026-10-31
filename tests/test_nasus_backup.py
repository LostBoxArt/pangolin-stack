import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sqlite3
import tempfile
import time
import unittest

spec = importlib.util.spec_from_file_location('nasus_backup', Path(__file__).resolve().parents[1] / 'scripts/backup-nasus-config.py')
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class BackupTests(unittest.TestCase):
    def test_wal_database_without_extension_is_consistent_and_sources_are_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); source = root / 'source'; app = source / 'volume1/docker/config/app'; app.mkdir(parents=True)
            (app / 'docker-compose.yml').write_text('services: {}\n')
            db = app / 'database'
            connection = sqlite3.connect(db)
            self.addCleanup(connection.close)
            connection.execute('PRAGMA journal_mode=WAL'); connection.execute('PRAGMA wal_autocheckpoint=0')
            connection.execute('CREATE TABLE records (value TEXT)'); connection.execute("INSERT INTO records VALUES ('committed')"); connection.commit()
            before = {p.name: p.read_bytes() for p in [db, Path(str(db) + '-wal')]}
            inventory = [{'name': '/app', 'mounts': [{'Type': 'bind', 'Source': '/volume1/docker/config/app', 'Destination': '/config'}], 'compose': '/volume1/docker/config/app/docker-compose.yml'}]
            with contextlib.redirect_stdout(io.StringIO()):manifest = backup.stage(inventory, source, root / 'stage', os.getuid(), os.getgid())
            snapshot = root / 'stage/volume1/docker/config/app/database'
            with sqlite3.connect(snapshot) as restored:self.assertEqual(restored.execute('SELECT value FROM records').fetchone()[0], 'committed')
            self.assertEqual(len(manifest['databases']), 1)
            self.assertFalse(Path(str(snapshot) + '-wal').exists())
            self.assertEqual(before, {p.name: p.read_bytes() for p in [db, Path(str(db) + '-wal')]})
            self.assertEqual(snapshot.stat().st_mode & 0o777, 0o600)

    def test_hawser_managed_compose_path_is_resolved(self):
        volume = '/volume1/.@plugins/AppCentral/docker-ce/docker_lib/volumes/example/_data'
        roots, files = backup.configuration_roots([
            {'name': '/hawser', 'mounts': [{'Type': 'volume', 'Source': volume, 'Destination': '/data/stacks'}], 'compose': '/volume1/docker/hawser/docker-compose.yml'},
            {'name': '/newt', 'mounts': [], 'compose': '/data/stacks/newt/docker-compose.yml'}])
        self.assertIn(volume, roots)
        self.assertIn(volume + '/newt/docker-compose.yml', files)

    def test_historical_wal_database_is_preserved_without_source_changes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); source = root / 'source'; app = source / 'volume1/docker/config/jellyseerr/db'; app.mkdir(parents=True)
            db = app / 'pre-request-delete-20260929T150829Z.sqlite3'
            with contextlib.closing(sqlite3.connect(db)) as connection:
                connection.execute('PRAGMA journal_mode=WAL').fetchall()
                connection.execute('CREATE TABLE records (value TEXT)'); connection.execute("INSERT INTO records VALUES ('old')"); connection.commit()
                connection.execute('PRAGMA wal_checkpoint(TRUNCATE)').fetchall()
            # Model the existing archived main file without its former live sidecars.
            for suffix in ('-wal', '-shm'):
                Path(str(db) + suffix).unlink(missing_ok=True)
            os.utime(db, (time.time() - 172800, time.time() - 172800))
            before = db.read_bytes()
            inventory = [{'name': '/seerr', 'mounts': [{'Type': 'bind', 'Source': '/volume1/docker/config/jellyseerr', 'Destination': '/config'}], 'compose': None}]
            with contextlib.closing(sqlite3.connect(app / 'db.sqlite3')) as live:
                live.execute('CREATE TABLE current_state (value TEXT)'); live.commit()
            proc = root / 'proc'; proc.mkdir()
            proof = backup.verify_historical_inactive(app, proc)['files']
            with contextlib.redirect_stdout(io.StringIO()):manifest = backup.stage(inventory, source, root / 'stage', os.getuid(), os.getgid(), historical_proofs=proof)
            self.assertEqual(manifest['historical_sqlite_artifacts'][0]['sha256'], backup.sha256_file(db))
            self.assertEqual(db.read_bytes(), before)
            self.assertFalse(Path(str(db) + '-wal').exists())
            self.assertFalse(backup.historical_database(app / 'db.sqlite3'))

    def test_only_exact_arr_diagnostic_databases_are_excluded(self):
        for app in ('sonarr', 'radarr', 'prowlarr'):
            for suffix in ('', '-wal', '-shm', '-journal'):
                self.assertTrue(backup.diagnostic_database('/volume1/docker/config/' + app + '/logs.db' + suffix))
            self.assertFalse(backup.diagnostic_database('/volume1/docker/config/' + app + '/' + app + '.db'))
            self.assertFalse(backup.diagnostic_database('/volume1/docker/config/' + app + '/logs.db.bak'))
        self.assertFalse(backup.diagnostic_database('/volume1/docker/config/arr-mcp/logs.db'))

    def test_historical_database_with_open_descriptor_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); app = root / 'jellyseerr/db'; app.mkdir(parents=True)
            database = app / 'pre-delete.sqlite3'; database.write_bytes(b'archive')
            os.utime(database, (time.time() - 172800, time.time() - 172800))
            descriptors = root / 'proc/123/fd'; descriptors.mkdir(parents=True)
            (descriptors / '4').symlink_to(database)
            with self.assertRaises(RuntimeError):backup.verify_historical_inactive(app, root / 'proc')

    def test_retired_fileflows_and_plex_cache_are_excluded(self):
        self.assertTrue(backup.excluded('/volume1/docker/config/fileflows/temp'))
        self.assertTrue(backup.excluded('/volume1/docker/config/plex/Library/Application Support/Plex Media Server/Cache'))
        self.assertFalse(backup.excluded('/volume1/docker/config/plex/Library/Application Support/Plex Media Server/Plug-in Support/Databases'))

    def test_unknown_compose_or_volume_cannot_silently_be_omitted(self):
        with self.assertRaises(RuntimeError):backup.configuration_roots([{'name': '/newt', 'mounts': [], 'compose': '/unmapped/newt/docker-compose.yml'}])
        with self.assertRaises(RuntimeError):backup.configuration_roots([{'name': '/unknown', 'mounts': [{'Type': 'volume', 'Source': '/example', 'Destination': '/unknown'}], 'compose': None}])

    def test_missing_required_configuration_fails_before_publication(self):
        with tempfile.TemporaryDirectory() as temp:
            inventory = [{'name': '/app', 'mounts': [{'Type': 'bind', 'Source': '/volume1/docker/config/app', 'Destination': '/config'}], 'compose': '/volume1/docker/config/app/docker-compose.yml'}]
            with self.assertRaises(FileNotFoundError):backup.stage(inventory, Path(temp) / 'source', Path(temp) / 'stage', os.getuid(), os.getgid())


if __name__ == '__main__':unittest.main()
