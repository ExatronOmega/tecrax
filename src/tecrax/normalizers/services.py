from __future__ import annotations

from typing import Any

from rexecop.execution.backend import StepExecutionContext

from tecrax.contracts import (
    build_docker_service_health_v1,
    build_ntp_local_health_v1,
)
from tecrax.normalizers.common import (
    connector_results,
    finalize_and_store,
    single_line,
    store_facts,
    stdout,
)


def normalize_ntp_health(context: StepExecutionContext) -> dict[str, Any]:
    results = connector_results(context)
    properties = _parse_properties(stdout(results, "read_ntp_sync_state"))
    service_state = single_line(stdout(results, "read_ntp_service_state"), limit=32)
    result = {
        "synchronized": properties.get("NTPSynchronized", "").lower() == "yes",
        "systemd_ntp_enabled": properties.get("NTP", "").lower() == "yes",
        "service": "ntp",
        "service_state": service_state,
    }
    facts = build_ntp_local_health_v1(
        synchronized=result["synchronized"],
        systemd_ntp_enabled=result["systemd_ntp_enabled"],
        service=result["service"],
        service_state=result["service_state"],
    )
    return store_facts(context, "ntp_health", facts)


def normalize_docker_services_health(context: StepExecutionContext) -> dict[str, Any]:
    results = connector_results(context)
    service = _parse_systemctl_show(stdout(results, "read_docker_service_state"))
    socket = _parse_systemctl_show(stdout(results, "read_docker_socket_state"))
    result = {
        "observation_scope": "systemd_service_only",
        "service": "docker",
        "service_load_state": service.get("LoadState", ""),
        "service_active_state": service.get("ActiveState", ""),
        "service_sub_state": service.get("SubState", ""),
        "service_unit_file_state": service.get("UnitFileState", ""),
        "socket": "docker.socket",
        "socket_load_state": socket.get("LoadState", ""),
        "socket_active_state": socket.get("ActiveState", ""),
        "socket_sub_state": socket.get("SubState", ""),
        "socket_unit_file_state": socket.get("UnitFileState", ""),
        "container_runtime_state": "not_observed",
    }
    facts = build_docker_service_health_v1(result)
    return store_facts(context, "docker_services_health", facts)


def normalize_zabbix_health(context: StepExecutionContext) -> dict[str, Any]:
    results = connector_results(context)
    payload = results.get("read_zabbix_api_version")
    if not isinstance(payload, dict):
        payload = {}
    version = str(payload.get("result") or "").strip()[:64]
    result = {
        "application_reachable": bool(version) and not payload.get("error"),
        "api_version": version,
        "container_runtime_state": "not_observed",
    }
    result["healthy"] = result["application_reachable"]
    return finalize_and_store(
        context,
        "zabbix_health",
        result,
        contract_id="tecrax.zabbix_api_reachability",
        requested=["api_reachability"],
        observed=["api_reachability"] if result["application_reachable"] else [],
        not_observed=["container_runtime", "problems", "hosts", "configuration"],
        assessment="healthy" if result["healthy"] else "unhealthy",
        non_claims=["container_health", "monitoring_health", "authenticated_api"],
    )


def normalize_adguard_health(context: StepExecutionContext) -> dict[str, Any]:
    results = connector_results(context)
    dns_stdout = stdout(results, "read_adguard_dns_resolution")
    login_status = single_line(stdout(results, "read_adguard_login_status"), limit=16)
    dns_answer_count = sum(
        1
        for line in dns_stdout.splitlines()
        if line.strip() and not line.lstrip().startswith(";")
    )
    result = {
        "observation_scope": "dns_and_web_login_only",
        "dns_resolves": dns_answer_count > 0,
        "dns_answer_count": min(dns_answer_count, 32),
        "web_login_http_status": login_status,
        "management_api_state": "not_observed",
        "container_runtime_state": "not_observed",
    }
    result["web_login_reachable"] = login_status in {"200", "302"}
    result["healthy"] = result["dns_resolves"] and result["web_login_reachable"]
    return finalize_and_store(
        context,
        "adguard_health",
        result,
        contract_id="tecrax.adguard_reachability",
        requested=["dns_resolution", "web_login_reachability"],
        observed=["dns_resolution", "web_login_reachability"],
        not_observed=["management_api", "configuration", "clients"],
        assessment="healthy" if result["healthy"] else "unhealthy",
        non_claims=["filter_effectiveness", "upstream_health", "container_health"],
    )


def normalize_portainer_health(context: StepExecutionContext) -> dict[str, Any]:
    results = connector_results(context)
    payload = results.get("read_portainer_status")
    if not isinstance(payload, dict):
        payload = {}
    version = str(payload.get("Version") or "").strip()[:64]
    result = {
        "observation_scope": "unauthenticated_status_only",
        "api_reachable": bool(version),
        "api_version": version,
        "instance_identity_state": "deliberately_not_collected",
        "management_objects_state": "not_observed",
        "container_runtime_state": "not_observed",
    }
    result["healthy"] = result["api_reachable"]
    return finalize_and_store(
        context,
        "portainer_health",
        result,
        contract_id="tecrax.portainer_reachability",
        requested=["unauthenticated_status"],
        observed=["unauthenticated_status"] if result["api_reachable"] else [],
        not_observed=["environments", "stacks", "containers", "users"],
        assessment="healthy" if result["healthy"] else "unhealthy",
        non_claims=["management_plane_health", "container_health", "authenticated_api"],
    )


def _parse_properties(value: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for line in value.splitlines():
        key, separator, raw = line.partition("=")
        if separator and key in {"NTP", "NTPSynchronized"}:
            parsed[key] = raw.strip()[:32]
    return parsed


def _parse_systemctl_show(value: str) -> dict[str, str]:
    allowed = {"LoadState", "ActiveState", "SubState", "UnitFileState"}
    parsed: dict[str, str] = {}
    for line in value.splitlines():
        key, separator, raw = line.partition("=")
        if separator and key in allowed:
            parsed[key] = raw.strip()[:64]
    return parsed
