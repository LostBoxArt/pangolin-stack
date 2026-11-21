#!/usr/bin/env python3
"""Consume watchdog triggers into bounded, read-only local diagnostic reports."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
from datetime import datetime, timezone

spec = importlib.util.spec_from_file_location("service_watchdog", Path(__file__).with_name("service-watchdog.py"))
watchdog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(watchdog)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Check pending diagnostics without changing files")
    args = parser.parse_args(argv)
    trigger = Path(watchdog.TRIGGER_FILE)
    processing = trigger.with_name(trigger.name + ".processing")
    if not args.dry_run and not processing.exists():
        try:
            os.replace(trigger, processing)
        except FileNotFoundError:
            return 0
    source = processing if processing.exists() else trigger
    if not source.exists():
        if args.dry_run:
            print(json.dumps({"pending": False}))
        return 0
    raw = source.read_bytes()
    data = json.loads(raw)
    if not isinstance(data.get("services"), list):
        raise ValueError("Diagnostic trigger must contain a service list")
    directory = Path.home() / ".hermes" / "diagnostics" / "watchdog"
    report = directory / ("watchdog-" + hashlib.sha256(raw).hexdigest()[:16] + ".json")
    created = not report.exists()
    if created or args.dry_run:
        checks = watchdog.collect_checks()
        result = {"checked_at": datetime.now(timezone.utc).isoformat(), "trigger": data,
                  "checks": checks, "failures": sorted(name for name, ok in checks.items() if not ok)}
        if args.dry_run:
            print(json.dumps({"pending": True, **result}))
            return 0
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        watchdog.save_json(str(report), result)
    processing.unlink()
    if created:
        print("Read-only watchdog diagnostics saved: " + str(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
