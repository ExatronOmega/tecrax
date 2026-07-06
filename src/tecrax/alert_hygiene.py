from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


ROUTING_CLASSES = frozenset(
    {"observe_only", "backlog", "ticket_grouped", "ticket_now"}
)


@dataclass(frozen=True)
class WazuhRuleEvent:
    rule_id: str
    level: int
    description: str
    groups: tuple[str, ...]
    agent: str
    timestamp: str
    location: str


def load_wazuh_events(path: Path, *, limit: int | None = None) -> list[WazuhRuleEvent]:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    if limit is not None and limit >= 0:
        lines = lines[-limit:]
    events: list[WazuhRuleEvent] = []
    for line in lines:
        if not line.strip():
            continue
        events.append(wazuh_event_from_mapping(json.loads(line)))
    return events


def wazuh_event_from_mapping(value: dict[str, Any]) -> WazuhRuleEvent:
    rule = value.get("rule") if isinstance(value.get("rule"), dict) else {}
    agent = value.get("agent") if isinstance(value.get("agent"), dict) else {}
    return WazuhRuleEvent(
        rule_id=_bounded_text(rule.get("id") or "unknown", 64),
        level=_int(rule.get("level")),
        description=_bounded_text(rule.get("description"), 240),
        groups=tuple(_bounded_text(item, 80) for item in rule.get("groups") or []),
        agent=_bounded_text(agent.get("name") or agent.get("id") or "unknown", 128),
        timestamp=_bounded_text(value.get("timestamp"), 80),
        location=_bounded_text(value.get("location"), 160),
    )


def classify_wazuh_event(event: WazuhRuleEvent) -> tuple[str, str]:
    groups = set(event.groups)
    desc = event.description.lower()
    if "authentication_failed" in groups or event.rule_id in {"5760"}:
        return "ticket_grouped", "auth failures need threshold grouping"
    if "low_diskspace" in groups or "partition usage reached" in desc:
        return "ticket_now", "disk pressure is directly actionable"
    if "vulnerability-detector" in groups:
        if event.level >= 10:
            return "ticket_grouped", "high vulnerability findings should be grouped by CVE/host/package"
        return "backlog", "lower vulnerability findings belong to patch/hardening backlog"
    if "sca" in groups or "rootcheck" in groups:
        return "backlog", "SCA/rootcheck findings belong to hardening backlog before incident routing"
    if "syscheck" in groups:
        return "backlog", "syscheck changes need review/tuning before ticket routing"
    if "dpkg" in groups or "config_changed" in groups:
        return "observe_only", "package/config changes are expected during operator work unless correlated"
    if "authentication_success" in groups or "pam" in groups:
        return "observe_only", "successful login/session events are telemetry, not tickets"
    if "sudo" in groups and event.level <= 4:
        return "observe_only", "successful sudo is operator telemetry unless anomalous"
    if event.level >= 12:
        return "ticket_now", "unclassified high-level alert"
    if event.level >= 10:
        return "ticket_grouped", "unclassified level 10+ alert"
    if event.level >= 7:
        return "backlog", "medium alert needs review before live routing"
    return "observe_only", "low-level telemetry"


def summarize_wazuh_events(events: Iterable[WazuhRuleEvent]) -> dict[str, Any]:
    event_list = list(events)
    by_level: Counter[int] = Counter()
    by_agent: Counter[str] = Counter()
    by_rule: Counter[str] = Counter()
    by_class: Counter[str] = Counter()
    rule_meta: dict[str, dict[str, str | int]] = {}
    class_reasons: Counter[tuple[str, str]] = Counter()
    agent_rule: Counter[tuple[str, str]] = Counter()
    first_ts = ""
    last_ts = ""

    for event in event_list:
        by_level[event.level] += 1
        by_agent[event.agent] += 1
        by_rule[event.rule_id] += 1
        agent_rule[(event.agent, event.rule_id)] += 1
        routing_class, reason = classify_wazuh_event(event)
        by_class[routing_class] += 1
        class_reasons[(routing_class, reason)] += 1
        rule_meta.setdefault(
            event.rule_id,
            {
                "level": event.level,
                "description": event.description,
                "groups": ",".join(event.groups),
            },
        )
        if event.timestamp:
            first_ts = event.timestamp if not first_ts or event.timestamp < first_ts else first_ts
            last_ts = event.timestamp if not last_ts or event.timestamp > last_ts else last_ts

    return {
        "total": len(event_list),
        "time_range": {"first": first_ts, "last": last_ts},
        "by_level": dict(sorted(by_level.items())),
        "by_agent": _top_counter(by_agent, 20),
        "by_rule": [
            {
                "rule_id": rule_id,
                "count": count,
                **rule_meta.get(rule_id, {}),
            }
            for rule_id, count in by_rule.most_common(30)
        ],
        "by_routing_class": {key: by_class.get(key, 0) for key in sorted(ROUTING_CLASSES)},
        "routing_reasons": [
            {"class": key[0], "reason": key[1], "count": count}
            for key, count in class_reasons.most_common(20)
        ],
        "top_agent_rules": [
            {
                "agent": key[0],
                "rule_id": key[1],
                "count": count,
                **rule_meta.get(key[1], {}),
            }
            for key, count in agent_rule.most_common(30)
        ],
    }


def _top_counter(counter: Counter[str], limit: int) -> list[dict[str, str | int]]:
    return [{"value": key, "count": count} for key, count in counter.most_common(limit)]


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
