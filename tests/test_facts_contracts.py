from __future__ import annotations

from tecrax.contracts import FACTS_CONTRACTS, finalize_facts, validate_facts


def test_all_active_results_have_static_contract_specs() -> None:
    assert set(FACTS_CONTRACTS) == {
        "tecrax.basic_host_inventory",
        "tecrax.ntp_local_health",
        "tecrax.docker_service_health",
        "tecrax.zabbix_api_reachability",
        "tecrax.adguard_reachability",
        "tecrax.portainer_reachability",
        "tecrax.network_device_inventory",
        "tecrax.monitoring_host_diagnosis",
        "tecrax.host_security_posture",
        "tecrax.ntp_server_observation",
        "tecrax.network_management_posture",
    }


def test_negative_health_is_valid_observation() -> None:
    facts = finalize_facts(
        {"synchronized": False, "service_state": "inactive"},
        contract_id="tecrax.ntp_local_health",
        requested=["local_synchronization", "daemon_state"],
        observed=["local_synchronization", "daemon_state"],
        assessment="unhealthy",
    )

    assert validate_facts(facts) == []
    assert facts["coverage"]["state"] == "complete"
    assert facts["assessment"]["state"] == "unhealthy"


def test_partial_and_unknown_are_distinct_from_unhealthy() -> None:
    facts = finalize_facts(
        {"target": "fixture", "os": {}, "kernel": ""},
        contract_id="tecrax.basic_host_inventory",
        requested=["os", "kernel"],
        observed=[],
        not_observed=["os", "kernel"],
        assessment="unknown",
    )

    assert validate_facts(facts) == []
    assert facts["coverage"]["state"] == "partial"
    assert facts["assessment"]["state"] == "unknown"


def test_raw_connector_output_is_rejected() -> None:
    facts = finalize_facts(
        {"synchronized": True, "service_state": "active"},
        contract_id="tecrax.ntp_local_health",
        requested=["local_synchronization"],
        observed=["local_synchronization"],
        assessment="healthy",
    )
    facts["stdout"] = "unbounded"

    assert "raw_output_forbidden" in validate_facts(facts)
