import atexit
import re
import json
import os
import pathlib
import shutil
import sqlite3
import stat
import subprocess
import tarfile
import tempfile

FIXTURE_PATH = pathlib.Path(__file__).resolve().parent / "fixtures/backup_docker.py"
SOURCE = (pathlib.Path(__file__).resolve().parents[1] / "backup.sh").read_text()
HERE = pathlib.Path(tempfile.mkdtemp(prefix="pangolin-backup-tests-"))
atexit.register(shutil.rmtree, HERE)
REAL_TAR = shutil.which("tar")

def fixture(case):
    root = pathlib.Path(tempfile.mkdtemp(prefix=f"backup-fixture-{case}-", dir=HERE))
    stack = root / "stack"
    homarr = root / "homarr"
    for rel in ["scripts", "docs/wiki/runbooks", "tests", "host-configs/cloudnode/systemd/user", "stacks/core", "sites", "qbit-proxy", "config/pangolin", "config/db", "config/traefik/rules", "config/letsencrypt", "config/crowdsec/scenarios", "config/crowdsec/parsers", "config/crowdsec/collections", "config/crowdsec/hub/collections", "config/crowdsec/db", "config/crowdsec-web-ui", "data/pocket-id", "data/dockhand/db"]:
        (stack / rel).mkdir(parents=True, exist_ok=True)
    (homarr / "appdata/db").mkdir(parents=True)
    for rel in ["docs/wiki/runbooks/backup-recovery.md", "tests/test_backup.py", "scripts/offsite-backup.py", "host-configs/cloudnode/systemd/user/homelab-offsite-vps.timer", "stacks/core/docker-compose.yml", "sites/index.html", "qbit-proxy/index.js", "qbit-proxy/Dockerfile", "config/pangolin/config.yml", "config/config.yml", "config/crowdsec-web-ui/config.json", "config/traefik/traefik_config.yml", "config/traefik/rules/test.yml", "config/letsencrypt/acme.json", "config/crowdsec/config.yaml", "config/crowdsec/scenarios/custom.yaml", "config/crowdsec/parsers/custom.yaml", "config/crowdsec/hub/collections/test.yaml", "config/key", "data/test.txt", "README.md", "INFRASTRUCTURE.md", "AGENTS.md"]:
        (stack / rel).write_text("fixture\n")
    (stack / ".env").write_text("FIXTURE_ONLY=true\n")
    (homarr / "appdata/test.txt").write_text("fixture\n")
    (stack / "data/.hidden-key").write_text("fixture\n")
    (stack / "config/crowdsec/collections/test.yaml").symlink_to("/etc/crowdsec/hub/collections/test.yaml")
    script, backup_count = re.subn(r'^BACKUP_DIR=.*$', f'BACKUP_DIR="{root}/backups"', SOURCE, count=1, flags=re.MULTILINE)
    script, stack_count = re.subn(r'^STACK_DIR=.*$', f'STACK_DIR="{stack}"', script, count=1, flags=re.MULTILINE)
    script = script.replace('/opt/homarr', str(homarr))
    assert backup_count == stack_count == 1
    assert '/opt/homarr' not in script
    (stack / "backup.sh").write_text(script)
    for name in ["startup.sh", "stackctl.sh"]:
        (stack / name).write_text("#!/bin/sh\nexit 0\n")
        (stack / name).chmod(0o700)
    bin_dir = root / "bin"
    bin_dir.mkdir()
    stubs = {
        "docker": "#!/bin/sh\nif [ \"$1 $2\" = \"volume inspect\" ]; then exit 1; fi\nif [ \"$1 $2\" = \"exec crowdsec\" ]; then\n  [ \"${FAIL_CROWDSEC:-0}\" = 1 ] && exit 19\n  exec \"$REAL_TAR\" -C \"$FIXTURE_CROWDSEC\" -cf - .\nfi\nexit 99\n",
        "sudo": "#!/bin/sh\n[ \"$1\" = -n ] && shift\nif [ \"$1\" = /usr/local/sbin/homarr-appdata-tar ]; then exec \"$REAL_TAR\" -C \"$FIXTURE_HOMARR\" -cf - .; fi\nif [ \"$1\" = mkdir ] || [ \"$1\" = cp ]; then exec \"$@\"; fi\nexit 99\n",
        "curl": "#!/bin/sh\nprintf 'fixture-ip'\n",
        "tar": "#!/bin/sh\nif [ \"${CORRUPT_ARCHIVE:-0}\" = 1 ] && [ \"$1\" = -czf ]; then printf invalid > \"$2\"; exit 0; fi\nexec \"$REAL_TAR\" \"$@\"\n",
    }
    for name, content in stubs.items():
        if name == "docker":
            content = FIXTURE_PATH.read_text()
        p = bin_dir / name
        p.write_text(content.replace('\\"', '"'))
        p.chmod(0o700)
    env = dict(os.environ, PATH=str(bin_dir) + os.pathsep + os.environ["PATH"], RETAIN_DAYS="0", FIXTURE_CROWDSEC=str(stack / "config/crowdsec"), FIXTURE_HOMARR=str(homarr / "appdata"), REAL_TAR=REAL_TAR)
    if case == "existing-log-permissions":
        (root / "backups").mkdir(mode=0o700)
        (root / "backups/backup.log").write_text("existing fixture log\n")
        (root / "backups/backup.log").chmod(0o644)
    host = root / "host-recovery"
    for name in ["root/.config/olm-client/config.json", "etc/systemd/system/olm.service", "etc/systemd/system/arr-mcp-tunnel.service", "etc/systemd/system/olm-watchdog.service", "etc/systemd/system/olm-watchdog.timer", "usr/local/sbin/olm-watchdog.sh", "usr/local/sbin/homarr-appdata-tar", "etc/crowdsec/bouncers/crowdsec-firewall-bouncer.yaml", "etc/systemd/system/crowdsec-firewall-bouncer.service"]:
        p = host / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("fixture\n")
        p.chmod(0o600)
    plugins = root / "traefik-plugins/sources/plugin"
    plugins.mkdir(parents=True)
    (plugins / "main.go").write_text("fixture\n")
    fake_home = root / "home"
    private_config = fake_home / ".config/homelab-backups"
    private_config.mkdir(parents=True)
    for name in ["offsite.env", "restic-version.json"]:
        (private_config / name).write_text("fixture\n")
    env["HOME"] = str(fake_home)
    env.update(FIXTURE_HOST_RECOVERY=str(host), FIXTURE_TRAEFIK_PLUGINS=str(root / "traefik-plugins"))
    return root, stack, env

def run(case, mutate=None):
    root, stack, env = fixture(case)
    db = sqlite3.connect(stack / "config/db/db.sqlite")
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA wal_autocheckpoint=0")
    db.execute("CREATE TABLE proof(value TEXT)")
    db.execute("INSERT INTO proof VALUES ('committed-in-wal')")
    db.commit()
    extra_paths = [stack / "config/crowdsec/db/crowdsec.db", stack / "config/crowdsec-web-ui/crowdsec.db", stack / "data/pocket-id/pocket-id.db", stack / "data/dockhand/db/dockhand.db", root / "homarr/appdata/db/db.sqlite"]
    writers = []
    for path in extra_paths:
        writer = sqlite3.connect(path)
        writer.execute("PRAGMA journal_mode=WAL")
        writer.execute("PRAGMA wal_autocheckpoint=0")
        writer.execute("CREATE TABLE proof(value TEXT)")
        writer.execute("INSERT INTO proof VALUES ('committed-in-wal')")
        writer.commit()
        writers.append(writer)
    if mutate:
        db.close()
        for writer in writers:writer.close()
        mutate(root, stack, env)
        (root / "backups").mkdir(mode=0o700, exist_ok=True)
        previous = root / "backups/pangolin-backup_20000101_000000.tar.gz"
        previous.write_bytes(b"previous verified fixture")
        os.utime(previous, (0, 0))
        env["RETAIN_DAYS"] = "7"
    result = subprocess.run(["bash", str(stack / "backup.sh"), "backup"], env=env, capture_output=True, text=True, timeout=20)
    if not mutate:
        assert result.returncode == 0, result.stderr + result.stdout[-1000:]
        archives = list((root / "backups").glob("*.tar.gz"))
        assert len(archives) == 1
        archive = archives[0]
        assert stat.S_IMODE(archive.stat().st_mode) == 0o600
        assert stat.S_IMODE((root / "backups/backup.log").stat().st_mode) == 0o600
        assert stat.S_IMODE((root / "backups").stat().st_mode) == 0o700
        with tarfile.open(archive) as tar:
            members = tar.getmembers()
            by_name = {m.name.split("/", 1)[-1]: m for m in members}
            for required in ["docs/wiki/runbooks/backup-recovery.md", "tests/test_backup.py", "scripts/offsite-backup.py", "host-configs/cloudnode/systemd/user/homelab-offsite-vps.timer", "host-configs/cloudnode/user-backup/offsite.env", "sites/index.html", "qbit-proxy/index.js", "config/crowdsec/scenarios/custom.yaml", "config/crowdsec/parsers/custom.yaml", "config/crowdsec/collections/test.yaml", "config/crowdsec/hub/collections/test.yaml", "config/db/db.sqlite", "homarr/test.txt", "AGENTS.md", "config/config.yml", "config/crowdsec-web-ui/config.json", "data/.hidden-key", "runtime/services.json", "host-configs/cloudnode/root/.config/olm-client/config.json", "host-configs/cloudnode/etc/systemd/system/olm.service", "traefik-plugins/sources/plugin/main.go"]:
                assert required in by_name, required
            assert by_name["config/crowdsec/collections/test.yaml"].issym()
            assert by_name["runtime/services.json"].mode & 0o777 == 0o600
            private = json.loads(tar.extractfile(by_name["runtime/services.json"]).read())
            assert len(private["databases"]) == 6 and len(private["services"]) == 13
            assert private["services"]["pangolin"]["config"]["Env"] == ["FIXTURE_SECRET=not-a-real-secret"]
            assert "not-a-real-secret" not in result.stdout + result.stderr
            local_image = private["local_images"][0]
            assert by_name[local_image["archive_path"]].mode & 0o777 == 0o600
            assert len(local_image["sha256"]) == 64
            database_paths = ["config/db/db.sqlite", "config/crowdsec/db/crowdsec.db", "config/crowdsec-web-ui/crowdsec.db", "data/pocket-id/pocket-id.db", "data/dockhand/db/dockhand.db", "homarr/db/db.sqlite"]
            for number, name in enumerate(database_paths):
                assert all(name + suffix not in by_name for suffix in ["-wal", "-shm", "-journal"])
                saved_db = root / f"restored-{number}.sqlite"
                saved_db.write_bytes(tar.extractfile(by_name[name]).read())
                with sqlite3.connect(saved_db) as snapshot:
                    assert snapshot.execute("SELECT value FROM proof").fetchall() == [("committed-in-wal",)]
                    assert snapshot.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        assert not list((root / "backups").glob("*.partial"))
        db.close()
        for writer in writers:writer.close()
    else:
        assert result.returncode != 0, case
        assert [p.name for p in (root / "backups").glob("*.tar.gz")] == [previous.name], case
        assert previous.read_bytes() == b"previous verified fixture"
    print(json.dumps({"case": case, "passed": True}))

if __name__ == "__main__":
    run("wal-and-inventory")
    run("existing-log-permissions")
    run("missing-required-AGENTS", lambda root, stack, env: (stack / "AGENTS.md").unlink())
    run("missing-required-site", lambda root, stack, env: shutil.rmtree(stack / "sites"))
    run("invalid-database", lambda root, stack, env: (stack / "config/db/db.sqlite").write_text("not a sqlite database"))
    run("crowdsec-export-failure", lambda root, stack, env: env.update(FAIL_CROWDSEC="1"))
    run("archive-validation-failure", lambda root, stack, env: env.update(CORRUPT_ARCHIVE="1"))

    run("missing-active-Pangolin-config", lambda root, stack, env: (stack / "config/config.yml").unlink())
    run("private-data-export-failure", lambda root, stack, env: env.update(FAIL_PRIVATE_EXPORT="1"))
    run("invalid-webui-database", lambda root, stack, env: (stack / "config/crowdsec-web-ui/crowdsec.db").write_text("invalid sqlite"))

    run("runtime-capture-failure", lambda root, stack, env: env.update(FAIL_RUNTIME_CAPTURE="1"))
    run("host-recovery-export-failure", lambda root, stack, env: env.update(FAIL_HOST_EXPORT="1"))
    run("plugin-cache-export-failure", lambda root, stack, env: env.update(FAIL_PLUGIN_EXPORT="1"))
    run("local-image-export-failure", lambda root, stack, env: env.update(FAIL_LOCAL_IMAGE="1"))
