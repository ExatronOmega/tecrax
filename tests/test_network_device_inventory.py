from __future__ import annotations

from rexecop.execution.backend import StepExecutionContext

from tecrax.internal_actions import normalize_network_device_inventory


def test_normalize_network_device_inventory_bounds_legacy_cli_output() -> None:
    context = StepExecutionContext(
        operation_id="op-test",
        target="network-device-01",
        mode="dry_run",
        step={"id": "normalize_network_device_inventory"},
        shared_state={
            "connector_results": {
                "read_network_device_system_info": {
                    "stdout": (
                        " System Description      : 48-Port Gigabit Smart Switch with 4 SFP Slots\n"
                        " System Name             : TL-SG2452\n"
                        " Hardware Version        : TL-SG2452 1.0\n"
                        " Software Version        : 1.0.4 Build 20151127 Rel.67331(s)\n"
                        " Ignored Extra Field     : omitted value\n"
                    )
                },
                "read_network_device_ssh_status": {
                    "stdout": (
                        " SSH Server              : Enabled\n"
                        " SSH Server Protocol V1  : Enabled\n"
                        " SSH Server Protocol V2  : Enabled\n"
                        " SSH Idle Timeout        : 120\n"
                        " SSH MAX Client          : 5\n"
                        " AES128-CBC              : Enabled\n"
                    )
                },
            }
        },
    )

    result = normalize_network_device_inventory(context)

    assert result == {
        "target": "network-device-01",
        "scope": "network_cli_readonly",
        "device": {
            "system_name": "TL-SG2452",
            "system_description": "48-Port Gigabit Smart Switch with 4 SFP Slots",
            "hardware_version": "TL-SG2452 1.0",
            "software_version": "1.0.4 Build 20151127 Rel.67331(s)",
        },
        "management_access": {
            "ssh_server_enabled": True,
            "ssh_protocol_v1_enabled": True,
            "ssh_protocol_v2_enabled": True,
            "idle_timeout_seconds": 120,
            "max_clients": 5,
        },
        "hardening_observations": {
            "legacy_ssh_v1_enabled": True,
            "legacy_crypto_observed": True,
            "mutations_observed": False,
        },
        "complete": True,
    }
    assert "omitted value" not in str(result)
    assert context.shared_state["network_device_inventory"] == result


def test_normalize_network_device_inventory_marks_missing_data_incomplete() -> None:
    context = StepExecutionContext(
        operation_id="op-test",
        target="network-device-01",
        mode="dry_run",
        step={"id": "normalize_network_device_inventory"},
        shared_state={"connector_results": {}},
    )

    result = normalize_network_device_inventory(context)

    assert result["complete"] is False
    assert result["hardening_observations"]["mutations_observed"] is False
