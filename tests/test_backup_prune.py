import io
import os
import sqlite3
import subprocess
import tarfile
import time
import unittest

from test_backup import fixture


class PruneTests(unittest.TestCase):
    def prepare(self, case):
        root, stack, env = fixture("prune-" + case)
        directory = root / "backups"
        directory.mkdir()
        database = root / "db.sqlite"
        with sqlite3.connect(database) as db:
            db.execute("CREATE TABLE proof(value TEXT)")
        archives = []
        for index in range(4):
            prefix = f"pangolin-backup_202610{27-index:02d}_120000"
            path = directory / (prefix + ".tar.gz")
            with tarfile.open(path, "w:gz") as archive:
                archive.add(database, arcname=prefix + "/config/db/db.sqlite")
                member = tarfile.TarInfo(prefix + "/MANIFEST.md")
                member.size = 7
                archive.addfile(member, io.BytesIO(b"fixture"))
            os.utime(path, (time.time() - (index + 10) * 86400,) * 2)
            archives.append(path)
        return root, stack, env, archives

    def run_prune(self, stack, env, days="7"):
        return subprocess.run(["bash", str(stack / "backup.sh"), "prune", days], env=env, capture_output=True, text=True, timeout=15)

    def test_all_old_and_invalid_retention_keep_every_archive(self):
        root, stack, env, archives = self.prepare("stale")
        self.assertNotEqual(self.run_prune(stack, env).returncode, 0)
        self.assertTrue(all(path.exists() for path in archives))
        os.utime(archives[0], None)
        for value in ["-1", "invalid", "1.5"]:
            self.assertNotEqual(self.run_prune(stack, env, value).returncode, 0)
            self.assertTrue(all(path.exists() for path in archives))

    def test_corrupt_newest_keeps_every_archive(self):
        root, stack, env, archives = self.prepare("corrupt")
        archives[0].write_bytes(b"corrupt")
        os.utime(archives[0], None)
        self.assertNotEqual(self.run_prune(stack, env).returncode, 0)
        self.assertTrue(all(path.exists() for path in archives))

    def test_fresh_valid_archive_still_protects_two_generations(self):
        root, stack, env, archives = self.prepare("fresh")
        os.utime(archives[0], None)
        result = self.run_prune(stack, env)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(archives[0].exists() and archives[1].exists())
        self.assertFalse(archives[2].exists() or archives[3].exists())

    def test_corrupt_second_generation_refuses_all_deletion(self):
        root, stack, env, archives = self.prepare("second-corrupt")
        os.utime(archives[0], None)
        archives[1].write_bytes(b"corrupt")
        self.assertNotEqual(self.run_prune(stack, env).returncode, 0)
        self.assertTrue(all(path.exists() for path in archives))

    def test_zero_disables_pruning_even_with_old_archives(self):
        root, stack, env, archives = self.prepare("disabled")
        self.assertEqual(self.run_prune(stack, env, "0").returncode, 0)
        self.assertTrue(all(path.exists() for path in archives))


if __name__ == "__main__":
    unittest.main()
