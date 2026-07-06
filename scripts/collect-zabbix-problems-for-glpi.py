#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from tecrax.zabbix_glpi_events import (
    ZabbixProblemQuery,
    alert_event_to_mapping,
    fetch_zabbix_problems,
    filter_zabbix_live_candidate_events,
    load_infrastructure_hosts_file,
    zabbix_live_routing_decision,
    zabbix_problems_to_alert_events,
)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect bounded Zabbix active problems as normalized GLPI alert events."
    )
    parser.add_argument("--api-url", required=True, help="Zabbix API URL ending with api_jsonrpc.php.")
    parser.add_argument(
        "--token-env",
        default="ZABBIX_API_TOKEN",
        help="Environment variable containing the Zabbix API token.",
    )
    parser.add_argument(
        "--min-severity",
        type=int,
        default=2,
        choices=range(0, 6),
        help="Minimum Zabbix severity to collect. Default: 2 (Warning).",
    )
    parser.add_argument("--limit", type=int, default=50, help="Maximum active problems to collect.")
    parser.add_argument(
        "--include-suppressed",
        action="store_true",
        help="Include suppressed Zabbix problems. Default: false.",
    )
    parser.add_argument("--source-url-base", default="", help="Optional Zabbix web base URL.")
    parser.add_argument(
        "--infra-host",
        action="append",
        default=[],
        help="Infrastructure host alias allowed for initial host-down live candidates.",
    )
    parser.add_argument(
        "--infra-host-file",
        type=Path,
        help="JSON or simple YAML file containing alert_routing.zabbix.infrastructure_hosts.",
    )
    parser.add_argument(
        "--live-candidates-only",
        action="store_true",
        help="Output only conservative live-candidate events. Default: output all shadow events.",
    )
    parser.add_argument(
        "--include-routing-decision",
        action="store_true",
        help="Include route/reason metadata in output mappings.",
    )
    parser.add_argument("--json", action="store_true", help="Print a JSON array instead of NDJSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    api_token = os.environ.get(args.token_env, "")
    if not api_token:
        raise SystemExit(f"missing Zabbix API token in {args.token_env}")
    query = ZabbixProblemQuery(
        min_severity=args.min_severity,
        limit=max(args.limit, 0),
        include_suppressed=args.include_suppressed,
    )
    infrastructure_hosts = [*args.infra_host, *_load_infra_hosts(args.infra_host_file)]
    problems = fetch_zabbix_problems(api_url=args.api_url, api_token=api_token, query=query)
    events = zabbix_problems_to_alert_events(problems, source_url_base=args.source_url_base)
    if args.live_candidates_only:
        events = filter_zabbix_live_candidate_events(
            events,
            infrastructure_hosts=infrastructure_hosts,
        )
    output_events = []
    for event in events:
        mapping = alert_event_to_mapping(event)
        if args.include_routing_decision:
            decision = zabbix_live_routing_decision(
                event,
                infrastructure_hosts=infrastructure_hosts,
            )
            mapping["route"] = decision.route
            mapping["route_reason"] = decision.reason
        output_events.append(mapping)
    if args.json:
        print(json.dumps(output_events, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        for event in output_events:
            print(json.dumps(event, ensure_ascii=False, sort_keys=True))
    return 0


def _load_infra_hosts(path: Path | None) -> list[str]:
    if path is None:
        return []
    try:
        return load_infrastructure_hosts_file(path)
    except ValueError as exc:
        raise SystemExit("infra host file must contain a list of infrastructure host aliases") from exc


if __name__ == "__main__":
    raise SystemExit(main())
