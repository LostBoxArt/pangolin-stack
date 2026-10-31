import io
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import tarfile
import unittest

from test_backup import fixture


DATABASES = ["config/db/db.sqlite", "config/crowdsec/db/crowdsec.db", "config/crowdsec-web-ui/crowdsec.db", "data/pocket-id/pocket-id.db", "data/dockhand/db/dockhand.db"]


class RestoreTests(unittest.TestCase):
    def prepare(self, case):
        root, stack, env = fixture("restore-" + case)
        paths = [stack / path for path in DATABASES] + [root / "homarr/appdata/db/db.sqlite"]
        for path in paths:
            with sqlite3.connect(path) as db:
                db.execute("CREATE TABLE proof(value TEXT)")
                db.execute("INSERT INTO proof VALUES ('backup-value')")
            path.chmod(0o640)
            if os.geteuid() == 0 and "crowdsec-web-ui" in path.parts:
                os.chown(path, 1001, 1001)
        with sqlite3.connect(paths[0]) as db:
            db.execute("CREATE TABLE journalproof(id INTEGER PRIMARY KEY, value TEXT)")
            db.executemany("INSERT INTO journalproof(value) VALUES (?)", [("A" * 5000,)] * 150)
        (stack / ".env").write_text("BACKUP_MARKER=true\n")
        (stack / "stackctl.sh").write_text('#!/bin/sh\nprintf called > "$STOP_MARKER"\n[ "${FAIL_STOP:-0}" = 1 ] && exit 7\nexit 0\n')
        (stack / "stackctl.sh").chmod(0o700)
        env["STOP_MARKER"] = str(root / "stop-called")
        result = subprocess.run(["bash", str(stack / "backup.sh"), "backup"], env=env, capture_output=True, text=True, timeout=25)
        self.assertEqual(result.returncode, 0, result.stderr)
        archive = next((root / "backups").glob("*.tar.gz"))
        # The fixture has only files owned by the current test user. Mock the
        # root gate for control-flow tests; test the real gate separately below.
        script = stack / "backup.sh"
        source = script.read_text()
        guard = 'do_restore() {\n    if [ "$EUID" -ne 0 ]; then'
        self.assertEqual(source.count(guard), 1)
        script.write_text(source.replace(guard, 'do_restore() {\n    if false; then', 1) + "\n# FIXTURE_KEEP_RUNNING_TOOL\n")
        (stack / ".env").write_text("LIVE_UNCHANGED=true\n")
        return root, stack, env, archive, paths

    def restore(self, stack, env, archive):
        return subprocess.run(["bash", str(stack / "backup.sh"), "restore", str(archive)], input="y\n", env=env, capture_output=True, text=True, timeout=25)

    def rewrite_archive(self, archive, transform):
        pending = archive.with_suffix(".fixture")
        with tarfile.open(archive) as source, tarfile.open(pending, "w:gz") as target:
            for member in source:
                content = source.extractfile(member).read() if member.isfile() else None
                changed = transform(member, content)
                if changed is None:
                    continue
                member, content = changed
                if content is not None:
                    member.size = len(content)
                target.addfile(member, io.BytesIO(content) if content is not None else None)
        pending.replace(archive)

    def test_stop_failure_never_changes_live_files(self):
        root, stack, env, archive, paths = self.prepare("stop-failure")
        env["FAIL_STOP"] = "1"
        sidecar = paths[0].with_name("db.sqlite-wal")
        sidecar.write_bytes(b"existing recovery state")
        result = self.restore(stack, env, archive)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((stack / ".env").read_text(), "LIVE_UNCHANGED=true\n")
        self.assertEqual(sidecar.read_bytes(), b"existing recovery state")

    @unittest.skipIf(os.geteuid() == 0, "root gate is exercised by an unprivileged test user")
    def test_unprivileged_restore_fails_before_shutdown(self):
        root, stack, env, archive, paths = self.prepare("root-gate")
        script = stack / "backup.sh"
        source = script.read_text().replace('do_restore() {\n    if false; then', 'do_restore() {\n    if [ "$EUID" -ne 0 ]; then', 1)
        script.write_text(source)
        result = self.restore(stack, env, archive)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires root", result.stderr)
        self.assertFalse((root / "stop-called").exists())

    def test_running_container_or_failed_docker_inventory_never_overwrites(self):
        for key, value in [("RUNNING_CONTAINERS", "pangolin"), ("FAIL_DOCKER_PS", "1"), ("FAIL_IMAGE_INSPECT", "1")]:
            root, stack, env, archive, paths = self.prepare(key)
            env[key] = value
            result = self.restore(stack, env, archive)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((stack / ".env").read_text(), "LIVE_UNCHANGED=true\n")

    def test_dirty_wal_is_not_replayed_and_captured_mode_owner_apply(self):
        root, stack, env, archive, paths = self.prepare("dirty-wal")
        for path in paths:
            subprocess.run(["python3", "-c", "import sqlite3,sys,os; c=sqlite3.connect(sys.argv[1]); c.execute('PRAGMA journal_mode=WAL'); c.execute('PRAGMA wal_autocheckpoint=0'); c.execute(\"UPDATE proof SET value='post-backup-value'\"); c.commit(); os._exit(0)", str(path)], check=True)
            self.assertTrue(path.with_name(path.name + "-wal").exists())
        result = self.restore(stack, env, archive)
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in paths:
            self.assertFalse(path.with_name(path.name + "-wal").exists())
            self.assertFalse(path.with_name(path.name + "-shm").exists())
            with sqlite3.connect(path) as db:
                self.assertEqual(db.execute("SELECT value FROM proof").fetchall(), [("backup-value",)])
                self.assertEqual(db.execute("PRAGMA integrity_check").fetchall(), [("ok",)])
            self.assertEqual(path.stat().st_mode & 0o777, 0o640)
            expected_owner = (1001, 1001) if os.geteuid() == 0 and "crowdsec-web-ui" in path.parts else (os.getuid(), os.getgid())
            self.assertEqual((path.stat().st_uid, path.stat().st_gid), expected_owner)
            self.assertTrue(os.access(path.parent, os.W_OK))
        self.assertTrue((stack / "data/.hidden-key").exists())
        self.assertIn("FIXTURE_KEEP_RUNNING_TOOL", (stack / "backup.sh").read_text())

    def test_crashed_hot_rollback_journal_cannot_override_snapshot(self):
        root, stack, env, archive, paths = self.prepare("hot-journal")
        with sqlite3.connect(paths[0]) as db:
            db.execute("UPDATE journalproof SET value=?", ("B" * 5000,))
        subprocess.run(["python3", "-c", "import sqlite3,sys,os; c=sqlite3.connect(sys.argv[1]); c.execute('PRAGMA cache_size=5'); c.execute('PRAGMA cache_spill=ON'); c.execute('BEGIN IMMEDIATE'); c.execute('UPDATE journalproof SET value=?',('C'*5000,)); os._exit(0)", str(paths[0])], check=True)
        journal = paths[0].with_name(paths[0].name + "-journal")
        self.assertTrue(journal.exists())
        result = self.restore(stack, env, archive)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(journal.exists())
        with sqlite3.connect(paths[0]) as db:
            self.assertEqual(db.execute("SELECT DISTINCT substr(value,1,1) FROM journalproof").fetchall(), [("A",)])
            self.assertEqual(db.execute("PRAGMA integrity_check").fetchall(), [("ok",)])

    def test_legacy_archive_without_runtime_or_agents_restores(self):
        root, stack, env, archive, paths = self.prepare("legacy")
        def transform(member, content):
            relative = member.name.split("/", 1)[-1]
            return None if relative == "AGENTS.md" or relative == "runtime" or relative.startswith("runtime/") else (member, content)
        self.rewrite_archive(archive, transform)
        result = self.restore(stack, env, archive)
        self.assertEqual(result.returncode, 0, result.stderr)
        with sqlite3.connect(paths[0]) as db:
            self.assertEqual(db.execute("SELECT value FROM proof").fetchall(), [("backup-value",)])

    def test_invalid_archive_database_fails_before_shutdown(self):
        root, stack, env, archive, paths = self.prepare("invalid-source")
        def transform(member, content):
            return (member, b"invalid SQLite") if member.name.endswith("config/db/db.sqlite") else (member, content)
        self.rewrite_archive(archive, transform)
        result = self.restore(stack, env, archive)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse((root / "stop-called").exists())
        self.assertEqual((stack / ".env").read_text(), "LIVE_UNCHANGED=true\n")


if __name__ == "__main__":
    unittest.main()
