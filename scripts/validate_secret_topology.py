#!/usr/bin/env python3
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {
    ".cfg",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
}
SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".rexecop",
    ".ruff_cache",
    ".venv",
    "__pycache__",
}
ALLOWLIST = {
    "examples/secrets/ubuntu-host.readonly.example.yaml",
}
DEPLOYMENT_MARKER_ALLOWLIST = {
    "scripts/validate_secret_topology.py",
    "tests/test_secret_topology_validator.py",
}

PRIVATE_IPV4 = re.compile(
    r"\b(?:10|192\.168|172\.(?:1[6-9]|2[0-9]|3[0-1]))(?:\.[0-9]{1,3}){2}\b"
)
MAC_ADDRESS = re.compile(r"(?i)\b[0-9a-f]{2}(?::[0-9a-f]{2}){5}\b")
KEY_MATERIAL = re.compile(
    r"-----BEGIN (?:OPENSSH|RSA|DSA|EC|PRIVATE|ENCRYPTED) PRIVATE KEY-----"
)
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(?:authorization|bearer|password|token)\b\s*[:=]\s*['\"]?[^'\"\s][^'\"\n]{7,}"
)
PRIVATE_PATH = re.compile(
    "|".join(
        (
            "/" + "home" + "/" + "probo" + "/",
            "/" + "home" + r"/[^/\s]+/\.ssh/",
            "~/" + ".ssh/",
        )
    )
)
PRIVATE_DEPLOYMENT_MARKER = re.compile(
    r"(?i)(?:"
    r"mbp\.infra\.lan|"
    r"GG_MBP_|"
    r"GPO_MBP_|"
    r"Tecrax/MBP|"
    r"(?:OU|DC)=MBP\b|"
    r"ODDZIAL-1|"
    r"\\\\nas01\\home|"
    r"\bSOWA\b|"
    r"\bBitdefender\b|"
    r"\bGravityZone\b"
    r")"
)


def _repository_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "--cached", "--others", "--exclude-standard"],
        cwd=ROOT,
        text=True,
    )
    return [ROOT / line for line in output.splitlines() if line.strip()]


def _is_scannable(path: Path) -> bool:
    relative = path.relative_to(ROOT)
    if any(part in SKIP_PARTS for part in relative.parts):
        return False
    if str(relative) in ALLOWLIST:
        return False
    return path.suffix.lower() in TEXT_SUFFIXES


def _scan_file(path: Path) -> list[str]:
    relative = path.relative_to(ROOT)
    text = path.read_text(encoding="utf-8")
    checks = [
        ("private_ipv4", PRIVATE_IPV4),
        ("mac_address", MAC_ADDRESS),
        ("key_material", KEY_MATERIAL),
        ("secret_assignment", SECRET_ASSIGNMENT),
        ("private_path", PRIVATE_PATH),
    ]
    if str(relative) not in DEPLOYMENT_MARKER_ALLOWLIST:
        checks.append(("private_deployment_marker", PRIVATE_DEPLOYMENT_MARKER))
    errors: list[str] = []
    for label, pattern in checks:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            errors.append(f"{relative}:{line}:{label}")
    return errors


def collect_errors() -> list[str]:
    errors: list[str] = []
    for path in _repository_files():
        if path.is_file() and _is_scannable(path):
            errors.extend(_scan_file(path))
    return sorted(set(errors))


def main() -> int:
    errors = collect_errors()
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print("secret_topology_ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
