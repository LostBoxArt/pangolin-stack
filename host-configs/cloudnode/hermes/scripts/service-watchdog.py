#!/usr/bin/env python3
"""Service watchdog — checks all critical services, alerts on state changes, triggers diagnostics after persistent failures.

State file (~/.hermes/scripts/.watchdog-state.json) tracks:
  - current failures
  - last alert timestamp per failure set
  - consecutive failure count per service

Trigger file (~/.hermes/scripts/.watchdog-trigger.json):
  - Written when any service hits 3 consecutive failures (scheduler cadence determines elapsed time)
  - Read and cleared by the bounded, read-only watchdog-diagnostics cron job

Alert logic:
  - New failure or recovery → alert immediately
  - Same failures persisting → re-alert only every 2 hours
  - All clear after previous failures → alert (recovery)
  - All clear, was already clear → silent (no output)
"""

import argparse
import ipaddress
import shlex
import subprocess
from concurrent.futures import ThreadPoolExecutor
import urllib.request
import urllib.error
import ssl
import socket
import json
import os
import time
import tempfile
from datetime import datetime, timezone

STATE_FILE = os.path.expanduser("~/.hermes/scripts/.watchdog-state.json")
TRIGGER_FILE = os.path.expanduser("~/.hermes/scripts/.watchdog-trigger.json")
RE_ALERT_SECONDS = 2 * 60 * 60  # re-alert for persistent failures every 2 hours
ALERT_THRESHOLD = 2  # don't alert until a service fails this many consecutive checks
CONSECUTIVE_THRESHOLD = 3  # trigger diagnostics after this many consecutive failures

# Services that are monitored but never alert standalone.
# They still participate in mass-failure diagnostics and state tracking.
SILENT_CHECKS = {"Tailscale router"}

# ── Ping checks ────────────────────────────────────────────────────

PING = [
    {"name": "NASUS", "host": "192.168.1.10"},
    {"name": "Tailscale router", "host": "100.64.0.1"},
]

# ── CloudNode local (Docker bridge / localhost) ────────────────────

CLOUDNODE = [
    {"name": "Traefik",         "url": "http://127.0.0.1:80/",               "expect": [200, 404]},
    {"name": "SearXNG",         "url": "http://127.0.0.1:8889/",             "expect": [200]},
    {"name": "Homarr",          "url": "http://127.0.0.1:7575/",             "expect": [200, 301, 302]},
    {"name": "Dashdot",         "url": "http://127.0.0.1:3001/",             "expect": [200, 301, 302]},
    {"name": "CrowdSec",        "url": "http://127.0.0.1:8080/",             "expect": [200, 401, 404]},
    {"name": "CrowdSec Web UI", "url": "http://127.0.0.1:3458/",             "expect": [200, 301, 302]},
    {"name": "arr-mcp tunnel",  "url": "http://127.0.0.1:16060/healthz",       "expect": [200]},
    {"name": "Olm data path", "url": "http://192.168.1.10:2375/_hawser/health",
     "expect": [200], "interface": "olm"},
]

# A running container without a healthcheck only proves process availability.
CLOUDNODE_DOCKER = [
    {"name": "Pangolin container", "container": "pangolin"},
    {"name": "Gerbil container", "container": "gerbil"},
    {"name": "Traefik container", "container": "traefik"},
    {"name": "Pocket ID container", "container": "pocket-id"},
    {"name": "Dockhand container", "container": "dockhand"},
    {"name": "CrowdSec container", "container": "crowdsec"},
    {"name": "qBit proxy", "container": "qbit-proxy"},
]

# ── NASUS via SSH (services on Docker bridge, not host-mapped) ────

NASUS_SSH = [
    {"name": "Newt",        "container": "newt"},
    {"name": "NAS Traefik", "container": "traefik"},
    {"name": "Hawser",      "container": "hawser"},
    {"name": "arr-mcp",     "container": "arr-mcp"},
    {"name": "FlareSolverr", "container": "flaresolverr"},
    {"name": "Sonarr",      "container": "sonarr"},
    {"name": "Radarr",      "container": "radarr"},
    {"name": "qBit",        "container": "qbittorrent"},
    {"name": "Prowlarr",    "container": "prowlarr"},
    {"name": "Seerr",       "container": "seerr"},
    {"name": "Bazarr",      "container": "bazarr"},
    {"name": "Plex",        "container": "plex"},
    # Auxiliary media services. These currently have no container healthcheck,
    # so this verifies that they remain running rather than application health.
    {"name": "Recyclarr",   "container": "recyclarr"},
    {"name": "Profilarr",   "container": "profilarr"},

]

# ── NASUS host-mapped services (ports exposed on the NAS IP) ────────

NASUS_DIRECT = []

# ── Public URLs (Cloudflare → CloudNode → tunnel → NASUS) ─────────

PUBLIC = [
    {"name": "Public landing", "url": "https://example.com/", "expect": [200]},
    {"name": "request.example.com", "url": "https://request.example.com/", "expect": [200, 301, 302, 307]},
    {"name": "plex.example.com", "url": "https://plex.example.com/", "expect": [200, 301, 302, 307, 401]},
    # This checks the authentication boundary, not Homarr's application health.
    {"name": "Home auth boundary", "url": "https://home.example.com/", "expect": [302, 401],
     "redirect_prefix": "https://pangolin.example.com/auth/resource/"},
    {"name": "dash.example.com", "url": "https://dash.example.com/", "expect": [200, 301, 302, 307]},
    {"name": "dockhand.example.com", "url": "https://dockhand.example.com/", "expect": [200, 301, 302, 307, 401]},
]

TIMEOUT = 8

# ── Helpers ────────────────────────────────────────────────────────

def ping(host):
    try:
        r = subprocess.run(["ping", "-c", "1", "-W", "3", host], capture_output=True, timeout=10)
        return r.returncode == 0
    except Exception:
        return False

def _resolve_via_upstream(host):
    """Resolve a hostname using a known-working upstream DNS (bypass system resolver)."""
    import subprocess
    try:
        r = subprocess.run(
            ["dig", "+short", "A", "@213.186.33.99", host],
            capture_output=True, text=True, timeout=8
        )
        for line in r.stdout.splitlines():
            try:
                return str(ipaddress.IPv4Address(line.strip()))
            except ValueError:
                continue
        return None
    except Exception:
        return None

def response_matches(status, headers, expect, redirect_prefix=None):
    return status in expect and (
        not redirect_prefix or status == 401 or headers.get("Location", "").startswith(redirect_prefix)
    )


def curl_check(url, expect, timeout, ssl_verify, redirect_prefix, resolved_ip=None, interface=None):
    # curl's total deadline also bounds DNS, unlike urlopen's socket timeout.
    cmd = ["curl", "-s", "-D", "-", "-o", "/dev/null", "-w", "\n%{http_code}",
           "--connect-timeout", str(timeout), "--max-time", str(timeout)]
    if interface:
        cmd += ["--noproxy", "*", "--interface", interface]
    if resolved_ip:
        from urllib.parse import urlparse
        parsed = urlparse(url)
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        cmd += ["--resolve", f"{parsed.hostname}:{port}:{resolved_ip}"]
    if not ssl_verify:
        cmd.append("-k")
    cmd.append(url)
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 3)
        if r.returncode:
            return None  # Transport failure may be repaired with the fallback resolver.
        lines = r.stdout.strip().splitlines()
        headers = {"Location": next((line.split(":", 1)[1].strip() for line in lines
                                    if line.lower().startswith("location:")), "")}
        return response_matches(int(lines[-1]), headers, expect, redirect_prefix)
    except Exception:
        return None


def http_check(url, expect, timeout=TIMEOUT, ssl_verify=True, redirect_prefix=None, interface=None):
    result = curl_check(url, expect, timeout, ssl_verify, redirect_prefix, interface=interface)
    if result is not None:
        return result
    from urllib.parse import urlparse
    parsed = urlparse(url)
    if not parsed.hostname:
        return False
    try:
        ipaddress.ip_address(parsed.hostname)
        return False  # A literal address cannot be repaired with another DNS resolver.
    except ValueError:
        pass
    ip = _resolve_via_upstream(parsed.hostname)
    return bool(ip and curl_check(url, expect, timeout, ssl_verify, redirect_prefix, ip, interface))


def container_health(containers, host=None):
    """Inspect a host's requested containers in one process; never read their environment."""
    result = {c["container"]: False for c in containers}
    fmt = "{{.Name}}|{{.State.Status}}|{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}"
    cmd = ["docker", "inspect", "--format", fmt, *result]
    if host:
        # The NAS wrapper performs its approved sudo call internally.
        cmd = ["ssh", "-o", "ConnectTimeout=5", "-o", "BatchMode=yes",
               "-o", "StrictHostKeyChecking=yes", f"admin@{host}", shlex.join(cmd)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        # A missing container makes inspect return nonzero while still reporting others.
        for line in r.stdout.splitlines():
            parts = line.split("|")
            if len(parts) == 3 and parts[0].lstrip("/") in result:
                name, state, health = parts
                result[name.lstrip("/")] = state == "running" and health in ("healthy", "none")
    except Exception:
        pass
    return result


def collect_checks():
    results = {c["name"]: ping(c["host"]) for c in PING}
    local = container_health(CLOUDNODE_DOCKER)
    results.update({c["name"]: local[c["container"]] for c in CLOUDNODE_DOCKER})
    nasus_up = results.get("NASUS", False)
    if nasus_up:
        remote = container_health(NASUS_SSH, "192.168.1.10")
        results.update({c["name"]: remote[c["container"]] for c in NASUS_SSH})
    checks = CLOUDNODE + PUBLIC + (NASUS_DIRECT if nasus_up else [])
    def check(c):
        return http_check(c["url"], c["expect"], redirect_prefix=c.get("redirect_prefix"),
                          interface=c.get("interface"))
    with ThreadPoolExecutor(max_workers=6) as executor:
        results.update(zip((c["name"] for c in checks), executor.map(check, checks)))
    try:
        results["Olm service"] = subprocess.run(
            ["systemctl", "is-active", "--quiet", "olm.service"], capture_output=True, timeout=5
        ).returncode == 0
    except Exception:
        results["Olm service"] = False
    return results


def load_state():
    try:
        with open(STATE_FILE) as f:
            state = json.load(f)
        # Sanitize last_alert: 0 or anything before Jan 2024 is bogus
        if state.get("last_alert", 0) < 1700000000:
            state["last_alert"] = time.time()
        return state
    except Exception:
        return {"failures": [], "last_alert": time.time(), "consecutive": {}}

def save_json(path, data):
    fd, temporary = tempfile.mkstemp(prefix=".watchdog-", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def save_state(state):
    save_json(STATE_FILE, state)


def write_trigger(services):
    """Publish a complete trigger for the bounded diagnostic consumer."""
    save_json(TRIGGER_FILE, {
        "services": services,
        "triggered_at": datetime.now(timezone.utc).isoformat(),
    })


def load_trigger():
    """Load existing trigger file, return empty dict if none."""
    try:
        with open(TRIGGER_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

# ── Main ───────────────────────────────────────────────────────────

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Check without writing state or producing alerts")
    args = parser.parse_args(argv)
    started = time.monotonic()
    checks = collect_checks()
    failures = [name for name, ok in checks.items() if not ok]
    if args.dry_run:
        print(json.dumps({"ok": not failures, "failures": sorted(failures), "checks": checks,
                          "runtime_seconds": round(time.monotonic() - started, 2)}))
        return 0 if not failures else 1

    # ── State-based alerting ───────────────────────────────────────
    prev = load_state()
    now = time.time()
    failure_key = sorted(failures)
    prev_key = sorted(prev.get("failures", []))
    last_alert = prev.get("last_alert", 0)
    consecutive = prev.get("consecutive", {})

    # Update consecutive failure counts
    new_consecutive = {}
    for f in failures:
        new_consecutive[f] = consecutive.get(f, 0) + 1
    # Carry over counts for services that recovered (for reference)
    for f in prev_key:
        if f not in new_consecutive:
            new_consecutive[f] = 0  # reset on recovery

    # Check for services hitting the threshold
    newly_triggered = []
    existing_trigger = load_trigger()
    already_triggered = set(existing_trigger.get("services", []))
    for f in failures:
        if new_consecutive[f] == CONSECUTIVE_THRESHOLD and f not in already_triggered:
            newly_triggered.append({"name": f, "consecutive": new_consecutive[f]})

    # Write trigger file if new diagnostics needed
    if newly_triggered:
        merged = list(already_triggered) + [s["name"] for s in newly_triggered]
        write_trigger(sorted(set(merged)))

    state_changed = failure_key != prev_key
    re_alert_due = (not state_changed) and failures and (now - last_alert >= RE_ALERT_SECONDS)

    # Filter to services that have hit the alert threshold (exclude silent checks)
    alertable = [f for f in failures if new_consecutive.get(f, 0) >= ALERT_THRESHOLD and f not in SILENT_CHECKS]
    had_alertable = [f for f in prev_key if consecutive.get(f, 0) >= ALERT_THRESHOLD and f not in SILENT_CHECKS]

    # Determine if we should alert
    should_alert = False
    if alertable and re_alert_due:
        should_alert = True  # re-alert for persistent failures
    elif alertable and (set(alertable) != set(had_alertable)):
        should_alert = True  # new service hit threshold, or set changed
    elif not alertable and had_alertable:
        should_alert = True  # recovery from something that was alertable

    if should_alert:
        # Save new state
        save_state({"failures": failure_key, "last_alert": now, "consecutive": new_consecutive})

        if not alertable:
            # Silent checks must not suppress recovery of previously alerted services.
            if not failures and os.path.exists(TRIGGER_FILE):
                os.remove(TRIGGER_FILE)
            print("✅ All alerted services recovered.")
        elif re_alert_due:
            # Persistent failure re-alert
            minutes_since = max(0, int((now - last_alert) / 60))
            print(f"⚠️ Still down ({len(alertable)} services, last alert {minutes_since}min ago):")
            for f in alertable:
                count = new_consecutive.get(f, 0)
                print(f"  • {f} ({count} consecutive checks)")
        else:
            # New service hit threshold or set changed
            print(f"⚠️ Service alerts ({len(alertable)} down):")
            for f in alertable:
                count = new_consecutive.get(f, 0)
                marker = " 🔧" if count >= CONSECUTIVE_THRESHOLD else ""
                print(f"  • {f} ({count} consecutive checks){marker}")
    else:
        # No change, no re-alert due → silent
        # Update state file timestamp even when silent
        if failures:
            save_state({"failures": failure_key, "last_alert": last_alert, "consecutive": new_consecutive})
        else:
            save_state({"failures": [], "last_alert": now, "consecutive": {}})

if __name__ == "__main__":
    raise SystemExit(main())
