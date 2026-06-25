from __future__ import annotations

from typing import Any

from rexecop.execution.backend import StepExecutionContext

from tecrax.contracts import build_basic_host_inventory_v1
from tecrax.normalizers.common import (
    bounded_float,
    connector_results,
    finalize_and_store,
    float_value,
    integer,
    single_line,
    store_facts,
    stdout,
)


def normalize_basic_host_inventory(context: StepExecutionContext) -> dict[str, Any]:
    results = connector_results(context)

    os_release = _parse_os_release(stdout(results, "read_os_release"))
    filesystem = _parse_df(stdout(results, "read_filesystem_usage"))
    memory = _parse_free(stdout(results, "read_memory_summary"))
    load_average = _parse_loadavg(stdout(results, "read_load_average"))
    inventory = build_basic_host_inventory_v1(
        target=context.target,
        os=os_release,
        kernel=single_line(stdout(results, "read_kernel_identity")),
        hostname=single_line(stdout(results, "read_hostname")),
        uptime=single_line(stdout(results, "read_uptime")),
        load_average=load_average,
        root_filesystem=filesystem,
        memory_mib=memory,
    )
    return store_facts(context, "basic_host_inventory", inventory)


def normalize_host_security_posture(context: StepExecutionContext) -> dict[str, Any]:
    results = connector_results(context)
    unattended = single_line(stdout(results, "read_unattended_upgrades_state"), limit=32)
    aslr = integer(single_line(stdout(results, "read_aslr_state"), limit=8))
    dmesg = integer(single_line(stdout(results, "read_dmesg_restrict_state"), limit=8))
    reboot_marker = single_line(stdout(results, "read_reboot_required_marker"), limit=32)
    signals = {
        "unattended_upgrades_enabled": unattended == "enabled",
        "aslr_mode": aslr,
        "dmesg_restrict": dmesg,
        "reboot_required": reboot_marker == "reboot-required",
    }
    complete = (
        unattended in {"enabled", "disabled", "static", "masked"}
        and aslr is not None
        and dmesg is not None
    )
    healthy = complete and signals["unattended_upgrades_enabled"] and aslr == 2 and dmesg == 1
    return finalize_and_store(
        context,
        "host_security_posture",
        {"signals": signals, "complete": complete, "healthy": healthy},
        contract_id="tecrax.host_security_posture",
        requested=["unattended_upgrades", "aslr", "dmesg_restrict", "reboot_required"],
        observed=[
            "unattended_upgrades",
            "aslr",
            "dmesg_restrict",
            "reboot_required",
        ]
        if complete
        else [],
        not_observed=[] if complete else ["one_or_more_security_signals"],
        assessment="healthy" if healthy else ("degraded" if complete else "unknown"),
        non_claims=["cis_compliance", "users", "packages", "ports", "ssh_configuration"],
    )


def normalize_ntp_server_observation(context: StepExecutionContext) -> dict[str, Any]:
    results = connector_results(context)
    daemon_state = single_line(stdout(results, "read_ntp_service_state"), limit=32)
    variables = _parse_ntp_variables(stdout(results, "read_ntp_server_variables"))
    stratum = integer(variables.get("stratum", ""))
    leap = integer(variables.get("leap", ""))
    complete = daemon_state == "active" and stratum is not None and leap is not None
    healthy = complete and 1 <= int(stratum) <= 15 and leap != 3
    return finalize_and_store(
        context,
        "ntp_server_observation",
        {
            "daemon_state": daemon_state,
            "serving_state": "local_daemon_query_available" if variables else "unknown",
            "system_variables": {
                "stratum": stratum,
                "leap": leap,
                "offset_ms": bounded_float(variables.get("offset")),
                "root_delay_ms": bounded_float(variables.get("rootdelay")),
                "root_dispersion_ms": bounded_float(variables.get("rootdisp")),
            },
            "healthy": healthy,
        },
        contract_id="tecrax.ntp_server_observation",
        requested=[
            "daemon_state",
            "stratum",
            "leap",
            "offset",
            "root_delay",
            "root_dispersion",
        ],
        observed=[
            "daemon_state",
            "stratum",
            "leap",
            "offset",
            "root_delay",
            "root_dispersion",
        ]
        if complete
        else [],
        not_observed=[] if complete else ["one_or_more_ntp_server_fields"],
        assessment="healthy" if healthy else ("degraded" if complete else "unknown"),
        non_claims=[
            "peer_identity",
            "peer_address",
            "remote_client_reachability",
            "firewall_state",
        ],
    )


def _parse_os_release(value: str) -> dict[str, str]:
    allowed = {"ID", "VERSION_ID", "PRETTY_NAME"}
    parsed: dict[str, str] = {}
    for line in value.splitlines():
        key, separator, raw = line.partition("=")
        if not separator or key not in allowed:
            continue
        parsed[key.lower()] = raw.strip().strip('"')[:256]
    return parsed


def _parse_ntp_variables(value: str) -> dict[str, str]:
    allowed = {"stratum", "offset", "rootdelay", "rootdisp", "leap"}
    parsed: dict[str, str] = {}
    for part in value.replace("\n", " ").split(","):
        key, separator, raw = part.strip().partition("=")
        if separator and key in allowed:
            parsed[key] = raw.strip()[:32]
    return parsed


def _parse_df(value: str) -> dict[str, Any]:
    lines = [line.split() for line in value.splitlines() if line.strip()]
    if len(lines) < 2 or len(lines[-1]) < 6:
        return {}
    row = lines[-1]
    return {
        "filesystem": row[0][:256],
        "blocks_1024": integer(row[1]),
        "used": integer(row[2]),
        "available": integer(row[3]),
        "capacity": row[4][:16],
        "mounted_on": row[5][:256],
    }


def _parse_free(value: str) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for line in value.splitlines():
        parts = line.split()
        if len(parts) < 4 or parts[0] != "Mem:":
            continue
        result = {
            "total": integer(parts[1]),
            "used": integer(parts[2]),
            "free": integer(parts[3]),
        }
        if len(parts) >= 7:
            result["available"] = integer(parts[6])
        break
    return result


def _parse_loadavg(value: str) -> dict[str, Any]:
    parts = value.split()
    if len(parts) < 5:
        return {}
    process_counts = parts[3].split("/", 1)
    return {
        "one_minute": float_value(parts[0]),
        "five_minutes": float_value(parts[1]),
        "fifteen_minutes": float_value(parts[2]),
        "runnable_processes": integer(process_counts[0]) if process_counts else None,
        "total_processes": integer(process_counts[1])
        if len(process_counts) == 2
        else None,
    }
