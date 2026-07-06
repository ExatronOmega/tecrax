from __future__ import annotations

import json
from pathlib import Path

from tecrax.alert_hygiene import (
    WazuhRuleEvent,
    classify_wazuh_event,
    load_wazuh_events,
    summarize_wazuh_events,
)


def _event(rule_id: str, level: int, groups: tuple[str, ...], desc: str = "") -> WazuhRuleEvent:
    return WazuhRuleEvent(
        rule_id=rule_id,
        level=level,
        description=desc,
        groups=groups,
        agent="dc01",
        timestamp="2026-07-06T10:00:00.000+0000",
        location="/var/log/auth.log",
    )


def test_classifies_successful_auth_as_observe_only() -> None:
    routing_class, reason = classify_wazuh_event(
        _event("5501", 3, ("pam", "syslog", "authentication_success"), "PAM opened")
    )

    assert routing_class == "observe_only"
    assert "telemetry" in reason


def test_classifies_high_vulnerability_as_grouped_ticket() -> None:
    routing_class, reason = classify_wazuh_event(
        _event("23505", 10, ("vulnerability-detector",), "CVE affects package")
    )

    assert routing_class == "ticket_grouped"
    assert "grouped" in reason


def test_classifies_sca_as_backlog() -> None:
    routing_class, reason = classify_wazuh_event(
        _event("19007", 7, ("sca",), "CIS benchmark finding")
    )

    assert routing_class == "backlog"
    assert "hardening" in reason


def test_classifies_disk_pressure_as_ticket_now() -> None:
    routing_class, reason = classify_wazuh_event(
        _event("531", 7, ("ossec", "low_diskspace"), "Partition usage reached 100%")
    )

    assert routing_class == "ticket_now"
    assert "actionable" in reason


def test_summarizes_rules_and_routing_classes() -> None:
    summary = summarize_wazuh_events(
        [
            _event("5501", 3, ("pam", "authentication_success"), "PAM opened"),
            _event("23505", 10, ("vulnerability-detector",), "CVE affects package"),
            _event("531", 7, ("ossec", "low_diskspace"), "Partition usage reached 100%"),
        ]
    )

    assert summary["total"] == 3
    assert summary["by_level"] == {3: 1, 7: 1, 10: 1}
    assert summary["by_routing_class"]["observe_only"] == 1
    assert summary["by_routing_class"]["ticket_grouped"] == 1
    assert summary["by_routing_class"]["ticket_now"] == 1


def test_load_wazuh_events_accepts_tail_limit(tmp_path: Path) -> None:
    path = tmp_path / "alerts.json"
    rows = [
        {"timestamp": "1", "agent": {"name": "a"}, "rule": {"id": "1", "level": 3, "groups": ["pam"]}},
        {"timestamp": "2", "agent": {"name": "b"}, "rule": {"id": "2", "level": 10, "groups": ["vulnerability-detector"]}},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")

    events = load_wazuh_events(path, limit=1)

    assert len(events) == 1
    assert events[0].rule_id == "2"
