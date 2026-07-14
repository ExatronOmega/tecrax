from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from tecrax.alert_routing import AlertEvent


ZABBIX_SEVERITY_NAMES = {
    0: "not_classified",
    1: "information",
    2: "warning",
    3: "average",
    4: "high",
    5: "disaster",
}


@dataclass(frozen=True)
class ZabbixProblemQuery:
    min_severity: int = 2
    limit: int = 50
    include_suppressed: bool = False


@dataclass(frozen=True)
class ZabbixRoutingDecision:
    route: str
    reason: str


def zabbix_problem_get_payload(query: ZabbixProblemQuery) -> dict[str, Any]:
    severities = [level for level in sorted(ZABBIX_SEVERITY_NAMES) if level >= query.min_severity]
    return {
        "jsonrpc": "2.0",
        "method": "problem.get",
        "params": {
            "output": ["eventid", "objectid", "name", "severity", "clock", "suppressed"],
            "severities": severities,
            "suppressed": query.include_suppressed,
            "sortfield": "eventid",
            "sortorder": "DESC",
            "limit": query.limit,
        },
        "id": 1,
    }


def zabbix_trigger_host_payload(trigger_ids: Iterable[str]) -> dict[str, Any]:
    ids = sorted({_bounded_text(trigger_id, 64) for trigger_id in trigger_ids if str(trigger_id)})
    return {
        "jsonrpc": "2.0",
        "method": "trigger.get",
        "params": {
            "output": ["triggerid"],
            "triggerids": ids,
            "selectHosts": ["host", "name"],
        },
        "id": 2,
    }


def fetch_zabbix_problems(
    *,
    api_url: str,
    api_token: str,
    query: ZabbixProblemQuery,
    timeout_seconds: int = 15,
) -> list[dict[str, Any]]:
    problems = _zabbix_request(
        api_url=api_url,
        api_token=api_token,
        payload=zabbix_problem_get_payload(query),
        timeout_seconds=timeout_seconds,
        result_name="problem",
    )
    trigger_ids = [str(problem.get("objectid") or "") for problem in problems]
    if not trigger_ids:
        return problems
    triggers = _zabbix_request(
        api_url=api_url,
        api_token=api_token,
        payload=zabbix_trigger_host_payload(trigger_ids),
        timeout_seconds=timeout_seconds,
        result_name="trigger",
    )
    hosts_by_trigger = _hosts_by_trigger_id(triggers)
    return [
        {**problem, "hosts": hosts_by_trigger.get(str(problem.get("objectid") or ""), [])}
        for problem in problems
    ]


def _zabbix_request(
    *,
    api_url: str,
    api_token: str,
    payload: dict[str, Any],
    timeout_seconds: int,
    result_name: str,
) -> list[dict[str, Any]]:
    request = urllib.request.Request(
        api_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Content-Type": "application/json-rpc",
            "Authorization": f"Bearer {api_token}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            data = response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"zabbix_http_error:{exc.code}:{_bounded_text(message, 200)}") from exc
    decoded = json.loads(data or "{}")
    if not isinstance(decoded, dict):
        raise RuntimeError("zabbix_response_not_object")
    if decoded.get("error"):
        raise RuntimeError(f"zabbix_api_error:{_bounded_text(decoded['error'], 240)}")
    result = decoded.get("result")
    if not isinstance(result, list):
        raise RuntimeError(f"zabbix_{result_name}_result_not_list")
    return [item for item in result if isinstance(item, dict)]


def zabbix_problem_to_alert_event(
    problem: dict[str, Any],
    *,
    source_url_base: str = "",
) -> AlertEvent:
    event_id = _bounded_text(problem.get("eventid") or "unknown", 120)
    name = _bounded_text(problem.get("name") or "Zabbix problem", 180)
    severity = _int(problem.get("severity"))
    host = _problem_host(problem)
    started_at = _zabbix_clock_to_iso(problem.get("clock"))
    source_url = _source_url(source_url_base, event_id)
    return AlertEvent(
        source="Zabbix",
        event_id=event_id,
        host=host,
        summary=name,
        raw_severity=str(severity),
        raw_trigger=name,
        started_at=started_at,
        source_url=source_url,
        category="",
    )


def zabbix_problems_to_alert_events(
    problems: Iterable[dict[str, Any]],
    *,
    source_url_base: str = "",
) -> list[AlertEvent]:
    return [
        zabbix_problem_to_alert_event(problem, source_url_base=source_url_base)
        for problem in problems
    ]


def alert_event_to_mapping(event: AlertEvent) -> dict[str, str]:
    return {
        "source": event.source,
        "event_id": event.event_id,
        "host": event.host,
        "summary": event.summary,
        "raw_severity": event.raw_severity,
        "raw_trigger": event.raw_trigger,
        "started_at": event.started_at,
        "source_url": event.source_url,
        "category": event.category,
    }


def zabbix_live_routing_decision(
    event: AlertEvent,
    *,
    infrastructure_hosts: Iterable[str] = (),
    shadow_only_hosts: Iterable[str] = (),
) -> ZabbixRoutingDecision:
    infra_hosts = {host.strip().lower() for host in infrastructure_hosts if host.strip()}
    shadow_only = {host.strip().lower() for host in shadow_only_hosts if host.strip()}
    host = event.host.strip().lower()
    if _is_host_unavailable(event):
        if host in shadow_only:
            return ZabbixRoutingDecision(
                route="shadow_only",
                reason="host-down policy routes this host to shadow-only",
            )
        if host in infra_hosts:
            return ZabbixRoutingDecision(
                route="live_candidate",
                reason="infrastructure host unavailable",
            )
        return ZabbixRoutingDecision(
            route="shadow_only",
            reason="host unavailable outside infrastructure allowlist",
        )
    if host not in infra_hosts:
        return ZabbixRoutingDecision(
            route="shadow_only",
            reason="host outside infrastructure allowlist",
        )
    if _is_known_expected_storage_pressure(event):
        return ZabbixRoutingDecision(
            route="shadow_only",
            reason="known expected storage pressure requires source tuning before ticketing",
        )
    if _is_critical_disk_pressure(event):
        return ZabbixRoutingDecision(
            route="live_candidate",
            reason="infrastructure critical disk pressure",
        )
    if _is_backup_failure(event):
        return ZabbixRoutingDecision(
            route="live_candidate",
            reason="backup failure on infrastructure host",
        )
    if _is_ad_dns_unavailable(event):
        return ZabbixRoutingDecision(
            route="live_candidate",
            reason="AD/DNS service unavailable",
        )
    if _is_core_service_unavailable(event):
        return ZabbixRoutingDecision(
            route="live_candidate",
            reason="core infrastructure service unavailable",
        )
    return ZabbixRoutingDecision(
        route="shadow_only",
        reason="not in initial live Zabbix allowlist",
    )


def filter_zabbix_live_candidate_events(
    events: Iterable[AlertEvent],
    *,
    infrastructure_hosts: Iterable[str] = (),
    shadow_only_hosts: Iterable[str] = (),
) -> list[AlertEvent]:
    return [
        event
        for event in events
        if zabbix_live_routing_decision(
            event,
            infrastructure_hosts=infrastructure_hosts,
            shadow_only_hosts=shadow_only_hosts,
        ).route
        == "live_candidate"
    ]


def load_infrastructure_hosts_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        value = json.loads(text)
    else:
        value = _parse_simple_yaml(text)
    hosts = _lookup(value, ("alert_routing", "zabbix", "infrastructure_hosts"))
    if hosts is None:
        hosts = _lookup(value, ("zabbix", "infrastructure_hosts"))
    if hosts is None:
        hosts = value.get("infrastructure_hosts") if isinstance(value, dict) else None
    if not isinstance(hosts, list) or not all(isinstance(host, str) for host in hosts):
        raise ValueError("infra host file must contain a list of infrastructure host aliases")
    return hosts


def load_host_down_shadow_only_hosts_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        value = json.loads(text)
    else:
        value = _parse_simple_yaml(text)
    hosts = _lookup(value, ("alert_routing", "zabbix", "host_down_policy", "shadow_only_hosts"))
    if hosts is None:
        hosts = _lookup(value, ("zabbix", "host_down_policy", "shadow_only_hosts"))
    if hosts is None:
        hosts = _lookup(value, ("host_down_policy", "shadow_only_hosts"))
    if hosts is None:
        # Backward-compatible read path for operator contexts created before the
        # host-down routing policy was split from power-state terminology.
        hosts = _lookup(value, ("alert_routing", "zabbix", "expected_off_hosts"))
    if hosts is None:
        hosts = _lookup(value, ("zabbix", "expected_off_hosts"))
    if hosts is None:
        hosts = value.get("expected_off_hosts") if isinstance(value, dict) else None
    if not isinstance(hosts, list) or not all(isinstance(host, str) for host in hosts):
        raise ValueError("host-down shadow-only policy file must contain a list of host aliases")
    return hosts


def load_expected_off_hosts_file(path: Path) -> list[str]:
    return load_host_down_shadow_only_hosts_file(path)


def _problem_host(problem: dict[str, Any]) -> str:
    hosts = problem.get("hosts")
    if isinstance(hosts, list) and hosts:
        first = hosts[0]
        if isinstance(first, dict):
            return _bounded_text(first.get("host") or first.get("name") or "unknown", 128)
    return "unknown"


def _is_host_unavailable(event: AlertEvent) -> bool:
    text = f"{event.summary} {event.raw_trigger}".lower()
    return any(
        phrase in text
        for phrase in (
            "unavailable by icmp",
            "host unavailable",
            "host is unavailable",
            "is unavailable",
            "not available",
        )
    )


def _is_known_expected_storage_pressure(event: AlertEvent) -> bool:
    text = f"{event.host} {event.summary} {event.raw_trigger}".lower()
    return "frigate01" in text and "/mnt/monitoring" in text


def _is_critical_disk_pressure(event: AlertEvent) -> bool:
    text = f"{event.summary} {event.raw_trigger}".lower()
    return any(
        phrase in text
        for phrase in (
            "space is critically low",
            "filesystem is full",
            "disk is full",
            "free disk space is less than",
            "vfs.fs.size",
        )
    )


def _is_backup_failure(event: AlertEvent) -> bool:
    text = f"{event.summary} {event.raw_trigger}".lower()
    return "backup" in text and any(
        phrase in text
        for phrase in (
            "failed",
            "failure",
            "error",
            "not completed",
            "missed",
        )
    )


def _is_ad_dns_unavailable(event: AlertEvent) -> bool:
    text = f"{event.host} {event.summary} {event.raw_trigger}".lower()
    return any(token in text for token in ("dc01", "adguard-01", "dns", "samba", "domain")) and any(
        phrase in text
        for phrase in (
            "unavailable",
            "not responding",
            "service is down",
            "failed",
        )
    )


def _is_core_service_unavailable(event: AlertEvent) -> bool:
    text = f"{event.host} {event.summary} {event.raw_trigger}".lower()
    return any(
        token in text
        for token in (
            "zabbix",
            "grafana",
            "wazuh",
            "pbs",
            "proxmox",
            "pve",
            "glpi",
            "bookstack",
        )
    ) and any(
        phrase in text
        for phrase in (
            "service is down",
            "service unavailable",
            "not running",
            "failed",
            "unavailable",
            "not responding",
        )
    )


def _hosts_by_trigger_id(triggers: Iterable[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = {}
    for trigger in triggers:
        trigger_id = str(trigger.get("triggerid") or "")
        hosts = trigger.get("hosts")
        if trigger_id and isinstance(hosts, list):
            result[trigger_id] = [host for host in hosts if isinstance(host, dict)]
    return result


def _zabbix_clock_to_iso(value: object) -> str:
    try:
        timestamp = int(str(value))
    except (TypeError, ValueError):
        return ""
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()


def _source_url(base: str, event_id: str) -> str:
    if not base:
        return ""
    return f"{base.rstrip('/')}/zabbix.php?action=problem.view&filter_eventids%5B0%5D={event_id}"


def _bounded_text(value: object, limit: int) -> str:
    text = "" if value is None else str(value)
    text = " ".join(text.replace("\r", " ").splitlines()).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _int(value: object) -> int:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return 0


def _lookup(value: object, path: tuple[str, ...]) -> object:
    current = value
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _parse_simple_yaml(text: str) -> dict[str, Any]:
    try:
        import yaml  # type: ignore[import-untyped]
    except ModuleNotFoundError as exc:
        raise ValueError("YAML infra host files require PyYAML; use JSON instead") from exc
    value = yaml.safe_load(text) or {}
    if not isinstance(value, dict):
        raise ValueError("infra host file must contain a mapping")
    return value
