from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any


COVERAGE_STATES = frozenset({"complete", "partial", "blocked"})
ASSESSMENT_STATES = frozenset({"healthy", "degraded", "unhealthy", "unknown"})
MAX_FACTS_BYTES = 16_384
MAX_SCOPE_ITEMS = 32
MAX_BLOCKERS = 16
MAX_NON_CLAIMS = 16


@dataclass(frozen=True)
class FactsContractSpec:
    contract_id: str
    version: str
    required_payload_keys: tuple[str, ...]


FACTS_CONTRACTS = {
    spec.contract_id: spec
    for spec in (
        FactsContractSpec("tecrax.basic_host_inventory", "1.0", ("target", "os", "kernel")),
        FactsContractSpec("tecrax.ntp_local_health", "1.0", ("synchronized", "service_state")),
        FactsContractSpec("tecrax.docker_service_health", "1.0", ("service_active_state",)),
        FactsContractSpec("tecrax.zabbix_api_reachability", "1.0", ("application_reachable",)),
        FactsContractSpec("tecrax.adguard_reachability", "1.0", ("dns_resolves", "web_login_reachable")),
        FactsContractSpec("tecrax.portainer_reachability", "1.0", ("api_reachable",)),
        FactsContractSpec("tecrax.network_device_inventory", "1.0", ("target", "device", "management_access")),
        FactsContractSpec("tecrax.monitoring_host_diagnosis", "1.0", ("components",)),
        FactsContractSpec("tecrax.host_security_posture", "1.0", ("signals",)),
        FactsContractSpec(
            "tecrax.ntp_server_observation",
            "1.0",
            ("daemon_state", "system_variables"),
        ),
        FactsContractSpec(
            "tecrax.network_management_posture",
            "1.0",
            ("findings", "source_inventory_contract"),
        ),
    )
}


def finalize_facts(
    payload: dict[str, Any],
    *,
    contract_id: str,
    requested: list[str],
    observed: list[str],
    not_observed: list[str] | None = None,
    blockers: list[str] | None = None,
    assessment: str,
    non_claims: list[str] | None = None,
) -> dict[str, Any]:
    spec = FACTS_CONTRACTS[contract_id]
    result = dict(payload)
    blocker_values = list(blockers or [])[:MAX_BLOCKERS]
    missing = list(not_observed or [])[:MAX_SCOPE_ITEMS]
    if blocker_values:
        coverage = "blocked"
    elif missing:
        coverage = "partial"
    else:
        coverage = "complete"
    result.update(
        {
            "contract": {"id": spec.contract_id, "version": spec.version},
            "scope": {
                "requested": list(requested)[:MAX_SCOPE_ITEMS],
                "observed": list(observed)[:MAX_SCOPE_ITEMS],
                "not_observed": missing,
            },
            "coverage": {"state": coverage, "blockers": blocker_values},
            "assessment": {"state": assessment},
            "non_claims": list(non_claims or [])[:MAX_NON_CLAIMS],
        }
    )
    errors = validate_facts(result, expected_contract_id=contract_id)
    if errors:
        raise ValueError("invalid_tecrax_facts:" + ",".join(errors))
    return result


def validate_facts(
    facts: dict[str, Any], *, expected_contract_id: str | None = None
) -> list[str]:
    errors: list[str] = []
    contract = facts.get("contract")
    contract_id = str(contract.get("id") or "") if isinstance(contract, dict) else ""
    spec = FACTS_CONTRACTS.get(contract_id)
    if spec is None:
        errors.append("unknown_contract")
        return errors
    if expected_contract_id and contract_id != expected_contract_id:
        errors.append("contract_id_mismatch")
    if contract.get("version") != spec.version:
        errors.append("contract_version_mismatch")
    for key in spec.required_payload_keys:
        if key not in facts:
            errors.append(f"missing_payload_key:{key}")

    coverage = facts.get("coverage")
    if not isinstance(coverage, dict) or coverage.get("state") not in COVERAGE_STATES:
        errors.append("invalid_coverage_state")
    assessment = facts.get("assessment")
    if not isinstance(assessment, dict) or assessment.get("state") not in ASSESSMENT_STATES:
        errors.append("invalid_assessment_state")
    scope = facts.get("scope")
    if not isinstance(scope, dict):
        errors.append("invalid_scope")
    else:
        for key in ("requested", "observed", "not_observed"):
            value = scope.get(key)
            if not isinstance(value, list) or len(value) > MAX_SCOPE_ITEMS:
                errors.append(f"invalid_scope:{key}")
    if _contains_forbidden_key(facts):
        errors.append("raw_output_forbidden")
    if len(json.dumps(facts, sort_keys=True, separators=(",", ":")).encode("utf-8")) > MAX_FACTS_BYTES:
        errors.append("facts_too_large")
    return sorted(set(errors))


def _contains_forbidden_key(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            if str(key).lower() in {"stdout", "stderr", "raw_output", "secret", "token"}:
                return True
            if _contains_forbidden_key(nested):
                return True
    elif isinstance(value, list):
        return any(_contains_forbidden_key(item) for item in value)
    return False
