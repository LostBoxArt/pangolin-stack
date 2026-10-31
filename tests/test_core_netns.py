"""Integration test: Docker and a cached alpine:latest image are required."""

import json
import pathlib
import shutil
import subprocess
import tempfile
import uuid


SOURCE = pathlib.Path(__file__).resolve().parents[1] / "scripts/ensure-traefik-netns.sh"


def run(args, check=True):
    result = subprocess.run(args, capture_output=True, text=True, timeout=45)
    if check:
        assert result.returncode == 0, result.stderr
    return result


image = run(["docker", "image", "inspect", "alpine:latest", "--format", "{{.Id}}"]).stdout.strip()
project = "codex-netns-" + uuid.uuid4().hex[:10]
with tempfile.TemporaryDirectory(prefix="core-netns-test-") as directory:
    root = pathlib.Path(directory)
    (root / "scripts").mkdir()
    (root / "stacks/core").mkdir(parents=True)
    (root / ".env").write_text("")
    script = root / "scripts/ensure-traefik-netns.sh"
    shutil.copyfile(SOURCE, script)
    compose_file = root / "stacks/core/docker-compose.yml"
    compose_file.write_text(f"""name: {project}
services:
  gerbil:
    image: {image}
    pull_policy: never
    command: ["sleep", "3600"]
    stop_grace_period: 1s
    network_mode: none
  traefik:
    image: {image}
    pull_policy: never
    command: ["sleep", "3600"]
    stop_grace_period: 1s
    network_mode: service:gerbil
""")
    compose = ["docker", "compose", "-f", str(compose_file), "--env-file", str(root / ".env")]

    def ids():
        return [run(compose + ["ps", "--all", "-q", service]).stdout.strip()
                for service in ("gerbil", "traefik")]

    try:
        run(["bash", "-n", str(script)])
        run(compose + ["up", "-d", "--pull", "never"])
        original = ids()
        run(["bash", str(script)])
        assert ids() == original, "Healthy containers must not be recreated"

        run(compose + ["up", "-d", "--no-deps", "--pull", "never", "--force-recreate", "gerbil"])
        drifted = ids()
        assert drifted[0] != original[0] and drifted[1] == original[1]
        run(["bash", str(script)])
        repaired = ids()
        assert repaired[0] == drifted[0] and repaired[1] != drifted[1]
        run(["bash", str(script)])
        assert ids() == repaired, "A second check must be a no-op"

        run(compose + ["restart", "gerbil"])
        run(["bash", str(script)])
        restarted = ids()
        assert restarted[0] == repaired[0]

        run(compose + ["stop", "traefik"])
        assert run(["bash", str(script)], check=False).returncode != 0
        assert ids() == restarted, "A stopped service must not be silently restarted"
    finally:
        run(compose + ["down", "--remove-orphans"])
        assert not run(compose + ["ps", "--all", "-q"]).stdout.strip()

print(json.dumps({"core_namespace_integration": "passed", "isolated_fixture_cleaned": True}))
