from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from rexecop.adapters.govengine_port.contracts import GovEngineDecisionType
from rexecop.adapters.govengine_port.static_adapter import StaticGovEngineAdapter
from rexecop.connectors.base import ConnectorRequest
from rexecop.errors import RExecOpValidationError
from rexecop.operation.controller import OperationController
from rexecop.operation.state import OperationState
from rexecop.storage.file_store import FileStore
from tecrax import profile_root
from tecrax.connectors.chrony import build_chrony_ntp_backend

REPO_ROOT = Path(__file__).resolve().parents[1]
ENVIRONMENT = REPO_ROOT / "examples/environments/chrony-ntp-server.apply.example.yaml"


class _ChronyEntryPoint:
    name = "tecrax_chrony_ntp"

    def load(self):
        return build_chrony_ntp_backend


def _entry_points(**_: object) -> list[_ChronyEntryPoint]:
    return [_ChronyEntryPoint()]


def test_chrony_backend_refuses_apply_without_admission() -> None:
    backend = build_chrony_ntp_backend(
        connector_name="chrony_ntp_server",
        config={"fixture_only": True, "allowed_subnet": "192.0.2.0/24"},
        mutating_allowed=False,
    )

    response = backend.invoke(
        ConnectorRequest(
            connector="chrony_ntp_server",
            action="apply_chrony_ntp_server",
            target="chrony-host-01",
            mode="apply",
        )
    )

    assert not response.success
    assert response.data["error_class"] == "policy_denied"


def test_chrony_backend_validates_allowed_subnet() -> None:
    backend = build_chrony_ntp_backend(
        connector_name="chrony_ntp_server",
        config={"fixture_only": True, "allowed_subnet": "192.0.2.0/16"},
        mutating_allowed=True,
    )

    response = backend.invoke(
        ConnectorRequest(
            connector="chrony_ntp_server",
            action="read_chrony_ntp_server_state",
            target="chrony-host-01",
            mode="apply",
        )
    )

    assert not response.success
    assert response.data["error_class"] == "validation_failed"


@patch("rexecop.connectors.fixture_loader.entry_points", side_effect=_entry_points)
def test_chrony_apply_blocked_before_backend(_entry_points_mock, tmp_path: Path) -> None:
    controller = OperationController(
        store=FileStore(tmp_path / ".rexecop"),
        govengine_adapter=StaticGovEngineAdapter(GovEngineDecisionType.BLOCKED),
    )

    operation = controller.plan(
        profile_path=Path(profile_root()),
        environment_path=ENVIRONMENT,
        intent="configure_chrony_ntp_server",
        target="chrony-host-01",
        mode="apply",
    )

    assert operation.state == OperationState.BLOCKED.value
    with pytest.raises(RExecOpValidationError):
        controller.start(operation.id)


@patch("rexecop.connectors.fixture_loader.entry_points", side_effect=_entry_points)
def test_chrony_apply_allowed_records_before_after_state(
    _entry_points_mock,
    tmp_path: Path,
) -> None:
    controller = OperationController(
        store=FileStore(tmp_path / ".rexecop"),
        govengine_adapter=StaticGovEngineAdapter(GovEngineDecisionType.ALLOWED),
    )

    operation = controller.plan(
        profile_path=Path(profile_root()),
        environment_path=ENVIRONMENT,
        intent="configure_chrony_ntp_server",
        target="chrony-host-01",
        mode="apply",
    )
    completed = controller.start(operation.id)

    assert completed.state == OperationState.COMPLETED.value
    shared = completed.metadata["shared_state"]
    mutation = shared["mutation_states"]["apply_chrony_ntp_server"]
    assert mutation["before_state"]["desired_state_applied"] is False
    assert mutation["after_state"]["desired_state_applied"] is True
    assert mutation["after_state"]["contract"] == {
        "id": "tecrax.chrony_ntp_server_mutation",
        "version": "1.0",
    }
    assert (
        mutation["after_state"]["schema_ref"]
        == "schemas/chrony_ntp_server_mutation.v1.schema.json"
    )
    assert mutation["after_state"]["coverage"]["state"] == "complete"
    assert "post_chrony_ntp_state" in shared["connector_results"]
