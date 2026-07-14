#!/usr/bin/env python3
"""Emit bounded, read-only APT update visibility for Zabbix.

The collector never refreshes package metadata and never prints package names.
It only simulates an upgrade against the existing local APT cache.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import time
from pathlib import Path


APT_LISTS = Path("/var/lib/apt/lists")
REBOOT_MARKER = Path("/var/run/reboot-required")
INSTALL_LINE = re.compile(r"^Inst\s+")


def parse_simulated_upgrade(output: str) -> tuple[int, int]:
    pending = 0
    security = 0
    for line in output.splitlines():
        if not INSTALL_LINE.match(line):
            continue
        pending += 1
        origin = line.partition(" (")[2].lower()
        if "security" in origin:
            security += 1
    return pending, security


def apt_cache_age_seconds(path: Path = APT_LISTS, *, now: float | None = None) -> int:
    try:
        mtimes = [entry.stat().st_mtime for entry in path.iterdir() if entry.is_file()]
    except OSError:
        return -1
    if not mtimes:
        return -1
    current = time.time() if now is None else now
    return max(0, int(current - max(mtimes)))


def collect() -> dict[str, object]:
    env = os.environ.copy()
    env["LC_ALL"] = "C"
    try:
        result = subprocess.run(
            ["apt-get", "-s", "-o", "Debug::NoLocking=1", "upgrade"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=60,
            env=env,
        )
    except (OSError, subprocess.TimeoutExpired):
        result = None

    pending, security = parse_simulated_upgrade(result.stdout if result else "")
    cache_age = apt_cache_age_seconds()
    complete = result is not None and result.returncode == 0 and cache_age >= 0
    return {
        "cache_age_seconds": cache_age,
        "collector_complete": int(complete),
        "pending_reboot": int(REBOOT_MARKER.exists()),
        "pending_security": security,
        "pending_total": pending,
        "schema_version": 1,
        "source": "apt-get-simulated-upgrade-local-cache",
    }


def main() -> int:
    print(json.dumps(collect(), separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
