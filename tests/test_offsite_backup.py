import importlib.util
import io
import os
from pathlib import Path
import tarfile
import tempfile
import time
import unittest
import shlex
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("offsite", Path(__file__).resolve().parents[1] / "scripts/offsite-backup.py")
backup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(backup)


class OffsiteBackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.calls = []
        self.patches = [patch.object(backup, "BACKUPS", self.root), patch.object(backup, "run", self.record)]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)

    def record(self, command, log):
        self.calls.append(command)

    def archive(self):
        path = self.root / "pangolin-backup_20261027_120000.tar.gz"
        with tarfile.open(path, "w:gz") as archive:
            content = b"fixture only"
            member = tarfile.TarInfo("backup/fixture")
            member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
        path.chmod(0o600)
        return path

    def test_verified_archive_uploaded_then_full_checked(self):
        archive = self.archive()
        result = backup.backup_vps(io.BytesIO(), True)
        self.assertEqual(result["archive"], str(archive))
        self.assertEqual(len(result["sha256"]), 64)
        self.assertEqual(self.calls[0][-1], str(archive))
        self.assertEqual(self.calls[1][-2:], ["check", "--read-data"])
        self.assertFalse(any("prune" in call or "forget" in call for call in self.calls))

    def test_missing_stale_public_and_corrupt_archives_never_upload(self):
        with self.assertRaises(RuntimeError):
            backup.backup_vps(io.BytesIO(), False)
        archive = self.archive()
        os.utime(archive, (time.time() - 27 * 3600,) * 2)
        with self.assertRaises(RuntimeError):
            backup.backup_vps(io.BytesIO(), False)
        os.utime(archive, None)
        archive.chmod(0o644)
        with self.assertRaises(RuntimeError):
            backup.backup_vps(io.BytesIO(), False)
        archive.chmod(0o600)
        archive.write_bytes(b"invalid gzip")
        with self.assertRaises(tarfile.ReadError):
            backup.backup_vps(io.BytesIO(), False)
        self.assertEqual(self.calls, [])

    def test_upload_failure_stops_validation(self):
        self.archive()
        with patch.object(backup, "run", side_effect=RuntimeError("fixture failure")) as run:
            with self.assertRaises(RuntimeError):
                backup.backup_vps(io.BytesIO(), False)
            self.assertEqual(run.call_count, 1)

    def test_nas_initializes_then_native_copies_and_checks(self):
        backup.backup_nas(io.BytesIO())
        self.assertEqual(len(self.calls), 4)
        self.assertEqual(self.calls[0][0], "ssh")
        self.assertIn("--copy-chunker-params", self.calls[1])
        self.assertIn("copy", self.calls[2])
        self.assertEqual(self.calls[3][-2:], ["check", "--read-data"])

    def test_existing_nas_copy_repository_is_not_reinitialized(self):
        target = self.root / "restic-nasus-config"
        target.mkdir()
        (target / "config").write_text("fixture only")
        backup.backup_nas(io.BytesIO())
        self.assertEqual(len(self.calls), 3)
        self.assertFalse(any("init" in call for call in self.calls))

    def test_failed_nas_source_never_initializes_or_copies(self):
        with patch.object(backup, "run", side_effect=RuntimeError("fixture failure")) as run:
            with self.assertRaises(RuntimeError):
                backup.backup_nas(io.BytesIO())
            self.assertEqual(run.call_count, 1)

    def test_sftp_preserves_the_single_proxy_command_argument(self):
        self.assertEqual(shlex.split(backup.SFTP_OPTIONS.removeprefix("sftp.args=")), backup.SSH_OPTIONS)
        self.assertIn("ProxyCommand=", backup.SFTP_OPTIONS)


if __name__ == "__main__":
    unittest.main()
