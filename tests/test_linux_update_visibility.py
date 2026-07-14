from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml


SCRIPT = Path(__file__).parents[1] / "scripts/collect-linux-update-status.py"
SPEC = importlib.util.spec_from_file_location("collect_linux_update_status", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_parse_simulated_upgrade_counts_without_exposing_packages() -> None:
    output = """\
Inst ordinary [1] (2 Debian:13.0/stable [amd64])
Inst urgent [1] (2 Debian-Security:13/stable-security [amd64])
Remv obsolete [1]
"""

    assert MODULE.parse_simulated_upgrade(output) == (2, 1)


def test_cache_age_uses_newest_regular_file(tmp_path: Path) -> None:
    older = tmp_path / "older"
    newer = tmp_path / "newer"
    older.write_text("x", encoding="utf-8")
    newer.write_text("x", encoding="utf-8")
    older.touch()
    newer.touch()
    older_mtime = 1_000.0
    newer_mtime = 1_500.0
    older.chmod(0o644)
    newer.chmod(0o644)
    import os

    os.utime(older, (older_mtime, older_mtime))
    os.utime(newer, (newer_mtime, newer_mtime))

    assert MODULE.apt_cache_age_seconds(tmp_path, now=2_000.0) == 500


def test_missing_cache_is_explicit_unknown(tmp_path: Path) -> None:
    assert MODULE.apt_cache_age_seconds(tmp_path / "missing", now=2_000.0) == -1


def test_monitoring_profile_uses_bounded_update_collector() -> None:
    root = Path(__file__).parents[1]
    connector = yaml.safe_load(
        (root / "src/tecrax/profile/connectors/monitoring_host.yaml").read_text(
            encoding="utf-8"
        )
    )
    example = yaml.safe_load(
        (root / "examples/environments/ubuntu-host.readonly.example.yaml").read_text(
            encoding="utf-8"
        )
    )

    command_shape = connector["connector"]["command_shapes"][
        "read_available_updates_summary"
    ]
    example_action = next(
        action
        for action in example["environment"]["connectors"]["monitoring_host"][
            "allowlist"
        ]
        if action["action"] == "read_available_updates_summary"
    )

    assert command_shape == {
        "command": "/usr/local/libexec/tecrax-update-status",
        "args": [],
    }
    assert example_action["command"] == command_shape["command"]
