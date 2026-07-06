#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tecrax.alert_hygiene import load_wazuh_events, summarize_wazuh_events


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Summarize Wazuh alerts into routing/hygiene classes."
    )
    parser.add_argument("alerts_json", type=Path, help="Path to Wazuh alerts.json or a bounded snapshot.")
    parser.add_argument(
        "--limit",
        type=int,
        default=5000,
        help="Use only the last N JSON lines. Use -1 for all lines.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    limit = None if args.limit < 0 else args.limit
    summary = summarize_wazuh_events(load_wazuh_events(args.alerts_json, limit=limit))
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
