from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import yaml
from rexecop.operation.controller import OperationController
from rexecop.operation.state import OperationState
from rexecop.storage.file_store import FileStore
from rexecop.triggers.service import TriggerService
from tecrax import profile_root

ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 6, 28, 12, 0, 0, tzinfo=UTC)


def _event(*, event_id: str, known: bool, subject: str = "monitoring-host-01") -> dict:
    return {
        "id": event_id,
        "source": "operator-fixture",
        "type": "network.host_observed",
        "subject": subject,
        "occurred_at": NOW.isoformat(),
        "payload": {
            "known": known,
            "target_kind": "host",
        },
        "rule_set": "tecrax.infrastructure-readonly-triggers",
    }


def test_trigger_rules_map_only_known_host_to_readonly_inventory() -> None:
    path = Path(profile_root()) / "triggers" / "trigger_rules.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    rules = data["trigger_rules"]["rules"]
    by_id = {rule["id"]: rule for rule in rules}

    known = by_id["network.known-host-observed.inventory"]
    assert known["decision"] == "plan_operation"
    assert known["operation"] == {
        "intent": "collect_basic_host_inventory",
        "catalog_target_from": "subject",
        "mode": "dry_run",
    }
    assert known["cooldown_seconds"] == 300

    unknown = by_id["network.unknown-host-observed.escalate"]
    assert unknown["decision"] == "escalate"
    assert "operation" not in unknown


def test_known_host_trigger_plans_catalog_inventory_without_autostart(tmp_path: Path) -> None:
    store = FileStore(tmp_path / ".rexecop")
    controller = OperationController(store=store)

    decision = TriggerService(controller).process_event(
        profile_path=Path(profile_root()),
        environment_path=None,
        catalog_path=ROOT / "examples" / "catalogs" / "targets.readonly.example.yaml",
        event_payload=_event(event_id="evt-known-1", known=True),
        now=NOW,
        source="test",
    )

    assert decision["decision"] == "plan_operation"
    operation = store.load_operation(decision["operation_id"])
    assert operation.state == OperationState.PLANNED.value
    assert operation.intent == "collect_basic_host_inventory"
    assert operation.target == "monitoring-host-01"
    assert operation.metadata["catalog_runtime"]["target_id"] == "monitoring-host-01"
    assert operation.metadata["trigger_decision"]["rule_id"] == (
        "network.known-host-observed.inventory"
    )


def test_unknown_host_trigger_escalates_without_operation(tmp_path: Path) -> None:
    store = FileStore(tmp_path / ".rexecop")
    controller = OperationController(store=store)

    decision = TriggerService(controller).process_event(
        profile_path=Path(profile_root()),
        environment_path=None,
        catalog_path=ROOT / "examples" / "catalogs" / "targets.readonly.example.yaml",
        event_payload=_event(event_id="evt-unknown-1", known=False, subject="unknown-host"),
        now=NOW,
        source="test",
    )

    assert decision["decision"] == "escalate"
    assert decision["operation_id"] is None
    assert store.list_operations() == []
