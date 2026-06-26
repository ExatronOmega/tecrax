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
BASIC_HOST_INVENTORY_CONTRACT_ID = "tecrax.basic_host_inventory"
BASIC_HOST_INVENTORY_CONTRACT_VERSION = "1.0"
BASIC_HOST_INVENTORY_SCHEMA_REF = "schemas/basic_host_inventory.v1.schema.json"
BASIC_HOST_INVENTORY_REQUESTED = [
    "os",
    "kernel",
    "hostname",
    "uptime",
    "load",
    "root_filesystem",
    "memory",
]
NTP_LOCAL_HEALTH_CONTRACT_ID = "tecrax.ntp_local_health"
NTP_LOCAL_HEALTH_CONTRACT_VERSION = "1.0"
NTP_LOCAL_HEALTH_SCHEMA_REF = "schemas/ntp_local_health.v1.schema.json"
NTP_LOCAL_HEALTH_REQUESTED = ["local_synchronization", "daemon_state"]
DOCKER_SERVICE_HEALTH_CONTRACT_ID = "tecrax.docker_service_health"
DOCKER_SERVICE_HEALTH_CONTRACT_VERSION = "1.0"
DOCKER_SERVICE_HEALTH_SCHEMA_REF = "schemas/docker_service_health.v1.schema.json"
DOCKER_SERVICE_HEALTH_REQUESTED = ["docker.service", "docker.socket"]
HOST_SECURITY_POSTURE_CONTRACT_ID = "tecrax.host_security_posture"
HOST_SECURITY_POSTURE_CONTRACT_VERSION = "1.0"
HOST_SECURITY_POSTURE_SCHEMA_REF = "schemas/host_security_posture.v1.schema.json"
HOST_SECURITY_POSTURE_REQUESTED = [
    "unattended_upgrades",
    "aslr",
    "dmesg_restrict",
    "reboot_required",
]
NTP_SERVER_OBSERVATION_CONTRACT_ID = "tecrax.ntp_server_observation"
NTP_SERVER_OBSERVATION_CONTRACT_VERSION = "1.0"
NTP_SERVER_OBSERVATION_SCHEMA_REF = "schemas/ntp_server_observation.v1.schema.json"
NTP_SERVER_OBSERVATION_REQUESTED = [
    "daemon_state",
    "stratum",
    "leap",
    "offset",
    "root_delay",
    "root_dispersion",
]


@dataclass(frozen=True)
class OsReleaseV1:
    pretty_name: str
    id: str
    version_id: str

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "OsReleaseV1":
        return cls(
            pretty_name=_bounded_text(value.get("pretty_name"), limit=256),
            id=_bounded_text(value.get("id"), limit=64),
            version_id=_bounded_text(value.get("version_id"), limit=64),
        )

    def as_dict(self) -> dict[str, str]:
        return {
            "pretty_name": self.pretty_name,
            "id": self.id,
            "version_id": self.version_id,
        }


@dataclass(frozen=True)
class LoadAverageV1:
    one_minute: float | None
    five_minutes: float | None
    fifteen_minutes: float | None
    runnable_processes: int | None
    total_processes: int | None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "LoadAverageV1":
        return cls(
            one_minute=_optional_float(value.get("one_minute")),
            five_minutes=_optional_float(value.get("five_minutes")),
            fifteen_minutes=_optional_float(value.get("fifteen_minutes")),
            runnable_processes=_optional_non_negative_int(value.get("runnable_processes")),
            total_processes=_optional_non_negative_int(value.get("total_processes")),
        )

    def as_dict(self) -> dict[str, float | int | None]:
        return {
            "one_minute": self.one_minute,
            "five_minutes": self.five_minutes,
            "fifteen_minutes": self.fifteen_minutes,
            "runnable_processes": self.runnable_processes,
            "total_processes": self.total_processes,
        }


@dataclass(frozen=True)
class RootFilesystemV1:
    filesystem: str
    blocks_1024: int | None
    used_1024: int | None
    available_1024: int | None
    capacity: str
    mounted_on: str

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "RootFilesystemV1":
        return cls(
            filesystem=_bounded_text(value.get("filesystem"), limit=128),
            blocks_1024=_optional_non_negative_int(value.get("blocks_1024")),
            used_1024=_optional_non_negative_int(value.get("used_1024")),
            available_1024=_optional_non_negative_int(value.get("available_1024")),
            capacity=_bounded_text(value.get("capacity"), limit=16),
            mounted_on=_bounded_text(value.get("mounted_on"), limit=128),
        )

    def as_dict(self) -> dict[str, str | int | None]:
        return {
            "filesystem": self.filesystem,
            "blocks_1024": self.blocks_1024,
            "used_1024": self.used_1024,
            "available_1024": self.available_1024,
            "capacity": self.capacity,
            "mounted_on": self.mounted_on,
        }


@dataclass(frozen=True)
class MemoryMiBV1:
    total: int | None
    used: int | None
    free: int | None
    shared: int | None
    buff_cache: int | None
    available: int | None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "MemoryMiBV1":
        return cls(
            total=_optional_non_negative_int(value.get("total")),
            used=_optional_non_negative_int(value.get("used")),
            free=_optional_non_negative_int(value.get("free")),
            shared=_optional_non_negative_int(value.get("shared")),
            buff_cache=_optional_non_negative_int(value.get("buff_cache")),
            available=_optional_non_negative_int(value.get("available")),
        )

    def as_dict(self) -> dict[str, int | None]:
        return {
            "total": self.total,
            "used": self.used,
            "free": self.free,
            "shared": self.shared,
            "buff_cache": self.buff_cache,
            "available": self.available,
        }


@dataclass(frozen=True)
class BasicHostInventoryV1:
    target: str
    os: OsReleaseV1
    kernel: str
    hostname: str
    uptime: str
    load_average: LoadAverageV1
    root_filesystem: RootFilesystemV1
    memory_mib: MemoryMiBV1

    @classmethod
    def from_parts(
        cls,
        *,
        target: str,
        os: dict[str, Any],
        kernel: str,
        hostname: str,
        uptime: str,
        load_average: dict[str, Any],
        root_filesystem: dict[str, Any],
        memory_mib: dict[str, Any],
    ) -> "BasicHostInventoryV1":
        return cls(
            target=_bounded_text(target, limit=128),
            os=OsReleaseV1.from_mapping(os),
            kernel=_bounded_text(kernel, limit=256),
            hostname=_bounded_text(hostname, limit=128),
            uptime=_bounded_text(uptime, limit=256),
            load_average=LoadAverageV1.from_mapping(load_average),
            root_filesystem=RootFilesystemV1.from_mapping(root_filesystem),
            memory_mib=MemoryMiBV1.from_mapping(memory_mib),
        )

    @property
    def complete(self) -> bool:
        return all(
            (
                self.target,
                self.os.id,
                self.kernel,
                self.hostname,
                self.uptime,
                self.load_average.one_minute is not None,
                self.root_filesystem.mounted_on == "/",
                self.memory_mib.total is not None,
            )
        )

    def payload(self) -> dict[str, Any]:
        return {
            "schema_ref": BASIC_HOST_INVENTORY_SCHEMA_REF,
            "target": self.target,
            "os": self.os.as_dict(),
            "kernel": self.kernel,
            "hostname": self.hostname,
            "uptime": self.uptime,
            "load_average": self.load_average.as_dict(),
            "root_filesystem": self.root_filesystem.as_dict(),
            "memory_mib": self.memory_mib.as_dict(),
            "complete": self.complete,
        }


@dataclass(frozen=True)
class NtpLocalHealthV1:
    synchronized: bool
    systemd_ntp_enabled: bool
    service: str
    service_state: str

    @classmethod
    def from_parts(
        cls,
        *,
        synchronized: bool,
        systemd_ntp_enabled: bool,
        service: str,
        service_state: str,
    ) -> "NtpLocalHealthV1":
        return cls(
            synchronized=bool(synchronized),
            systemd_ntp_enabled=bool(systemd_ntp_enabled),
            service=_bounded_text(service, limit=32),
            service_state=_bounded_text(service_state, limit=32),
        )

    @property
    def healthy(self) -> bool:
        return self.synchronized and self.service_state == "active"

    def payload(self) -> dict[str, Any]:
        return {
            "schema_ref": NTP_LOCAL_HEALTH_SCHEMA_REF,
            "synchronized": self.synchronized,
            "systemd_ntp_enabled": self.systemd_ntp_enabled,
            "service": self.service,
            "service_state": self.service_state,
            "healthy": self.healthy,
        }


@dataclass(frozen=True)
class DockerServiceHealthV1:
    observation_scope: str
    service: str
    service_load_state: str
    service_active_state: str
    service_sub_state: str
    service_unit_file_state: str
    socket: str
    socket_load_state: str
    socket_active_state: str
    socket_sub_state: str
    socket_unit_file_state: str
    container_runtime_state: str

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "DockerServiceHealthV1":
        return cls(
            observation_scope=_bounded_text(value.get("observation_scope"), limit=64),
            service=_bounded_text(value.get("service"), limit=64),
            service_load_state=_bounded_text(value.get("service_load_state"), limit=64),
            service_active_state=_bounded_text(value.get("service_active_state"), limit=64),
            service_sub_state=_bounded_text(value.get("service_sub_state"), limit=64),
            service_unit_file_state=_bounded_text(
                value.get("service_unit_file_state"), limit=64
            ),
            socket=_bounded_text(value.get("socket"), limit=64),
            socket_load_state=_bounded_text(value.get("socket_load_state"), limit=64),
            socket_active_state=_bounded_text(value.get("socket_active_state"), limit=64),
            socket_sub_state=_bounded_text(value.get("socket_sub_state"), limit=64),
            socket_unit_file_state=_bounded_text(
                value.get("socket_unit_file_state"), limit=64
            ),
            container_runtime_state=_bounded_text(
                value.get("container_runtime_state"), limit=64
            ),
        )

    @property
    def healthy(self) -> bool:
        return self.service_load_state == "loaded" and self.service_active_state == "active"

    def payload(self) -> dict[str, Any]:
        return {
            "schema_ref": DOCKER_SERVICE_HEALTH_SCHEMA_REF,
            "observation_scope": self.observation_scope,
            "service": self.service,
            "service_load_state": self.service_load_state,
            "service_active_state": self.service_active_state,
            "service_sub_state": self.service_sub_state,
            "service_unit_file_state": self.service_unit_file_state,
            "socket": self.socket,
            "socket_load_state": self.socket_load_state,
            "socket_active_state": self.socket_active_state,
            "socket_sub_state": self.socket_sub_state,
            "socket_unit_file_state": self.socket_unit_file_state,
            "container_runtime_state": self.container_runtime_state,
            "healthy": self.healthy,
        }


@dataclass(frozen=True)
class HostSecurityPostureV1:
    signals: dict[str, bool | int | None]
    complete: bool
    healthy: bool

    @classmethod
    def from_parts(
        cls,
        *,
        signals: dict[str, Any],
        complete: bool,
        healthy: bool,
    ) -> "HostSecurityPostureV1":
        return cls(
            signals={
                "unattended_upgrades_enabled": bool(
                    signals.get("unattended_upgrades_enabled")
                ),
                "aslr_mode": _optional_non_negative_int(signals.get("aslr_mode")),
                "dmesg_restrict": _optional_non_negative_int(
                    signals.get("dmesg_restrict")
                ),
                "reboot_required": bool(signals.get("reboot_required")),
            },
            complete=bool(complete),
            healthy=bool(healthy),
        )

    def payload(self) -> dict[str, Any]:
        return {
            "schema_ref": HOST_SECURITY_POSTURE_SCHEMA_REF,
            "signals": dict(self.signals),
            "complete": self.complete,
            "healthy": self.healthy,
        }


@dataclass(frozen=True)
class NtpServerVariablesV1:
    stratum: int | None
    leap: int | None
    offset_ms: float | None
    root_delay_ms: float | None
    root_dispersion_ms: float | None

    @classmethod
    def from_mapping(cls, value: dict[str, Any]) -> "NtpServerVariablesV1":
        return cls(
            stratum=_optional_non_negative_int(value.get("stratum")),
            leap=_optional_non_negative_int(value.get("leap")),
            offset_ms=_optional_signed_float(value.get("offset_ms")),
            root_delay_ms=_optional_signed_float(value.get("root_delay_ms")),
            root_dispersion_ms=_optional_signed_float(value.get("root_dispersion_ms")),
        )

    def as_dict(self) -> dict[str, float | int | None]:
        return {
            "stratum": self.stratum,
            "leap": self.leap,
            "offset_ms": self.offset_ms,
            "root_delay_ms": self.root_delay_ms,
            "root_dispersion_ms": self.root_dispersion_ms,
        }


@dataclass(frozen=True)
class NtpServerObservationV1:
    daemon_state: str
    serving_state: str
    system_variables: NtpServerVariablesV1
    healthy: bool

    @classmethod
    def from_parts(
        cls,
        *,
        daemon_state: str,
        serving_state: str,
        system_variables: dict[str, Any],
        healthy: bool,
    ) -> "NtpServerObservationV1":
        return cls(
            daemon_state=_bounded_text(daemon_state, limit=32),
            serving_state=_bounded_text(serving_state, limit=64),
            system_variables=NtpServerVariablesV1.from_mapping(system_variables),
            healthy=bool(healthy),
        )

    @property
    def complete(self) -> bool:
        return (
            self.daemon_state == "active"
            and self.system_variables.stratum is not None
            and self.system_variables.leap is not None
        )

    def payload(self) -> dict[str, Any]:
        return {
            "schema_ref": NTP_SERVER_OBSERVATION_SCHEMA_REF,
            "daemon_state": self.daemon_state,
            "serving_state": self.serving_state,
            "system_variables": self.system_variables.as_dict(),
            "healthy": self.healthy,
        }


@dataclass(frozen=True)
class FactsContractSpec:
    contract_id: str
    version: str
    required_payload_keys: tuple[str, ...]


FACTS_CONTRACTS = {
    spec.contract_id: spec
    for spec in (
        FactsContractSpec(
            BASIC_HOST_INVENTORY_CONTRACT_ID,
            BASIC_HOST_INVENTORY_CONTRACT_VERSION,
            ("target", "os", "kernel"),
        ),
        FactsContractSpec(
            NTP_LOCAL_HEALTH_CONTRACT_ID,
            NTP_LOCAL_HEALTH_CONTRACT_VERSION,
            ("synchronized", "service_state"),
        ),
        FactsContractSpec(
            DOCKER_SERVICE_HEALTH_CONTRACT_ID,
            DOCKER_SERVICE_HEALTH_CONTRACT_VERSION,
            ("service_active_state",),
        ),
        FactsContractSpec(
            "tecrax.zabbix_api_reachability",
            "1.0",
            ("application_reachable",),
        ),
        FactsContractSpec(
            "tecrax.adguard_reachability",
            "1.0",
            ("dns_resolves", "web_login_reachable"),
        ),
        FactsContractSpec("tecrax.portainer_reachability", "1.0", ("api_reachable",)),
        FactsContractSpec(
            "tecrax.network_device_inventory",
            "1.0",
            ("target", "device", "management_access"),
        ),
        FactsContractSpec("tecrax.monitoring_host_diagnosis", "1.0", ("components",)),
        FactsContractSpec(
            HOST_SECURITY_POSTURE_CONTRACT_ID,
            HOST_SECURITY_POSTURE_CONTRACT_VERSION,
            ("signals",),
        ),
        FactsContractSpec(
            NTP_SERVER_OBSERVATION_CONTRACT_ID,
            NTP_SERVER_OBSERVATION_CONTRACT_VERSION,
            ("daemon_state", "system_variables"),
        ),
        FactsContractSpec(
            "tecrax.network_management_posture",
            "1.0",
            ("findings", "source_inventory_contract"),
        ),
    )
}


def build_basic_host_inventory_v1(
    *,
    target: str,
    os: dict[str, Any],
    kernel: str,
    hostname: str,
    uptime: str,
    load_average: dict[str, Any],
    root_filesystem: dict[str, Any],
    memory_mib: dict[str, Any],
) -> dict[str, Any]:
    model = BasicHostInventoryV1.from_parts(
        target=target,
        os=os,
        kernel=kernel,
        hostname=hostname,
        uptime=uptime,
        load_average=load_average,
        root_filesystem=root_filesystem,
        memory_mib=memory_mib,
    )
    complete = model.complete
    return finalize_facts(
        model.payload(),
        contract_id=BASIC_HOST_INVENTORY_CONTRACT_ID,
        requested=BASIC_HOST_INVENTORY_REQUESTED,
        observed=BASIC_HOST_INVENTORY_REQUESTED if complete else [],
        not_observed=[] if complete else ["one_or_more_inventory_fields"],
        assessment="healthy" if complete else "unknown",
        non_claims=["packages", "users", "processes", "network_listeners"],
    )


def validate_basic_host_inventory_v1(facts: dict[str, Any]) -> list[str]:
    return validate_facts(
        facts,
        expected_contract_id=BASIC_HOST_INVENTORY_CONTRACT_ID,
    )


def build_ntp_local_health_v1(
    *,
    synchronized: bool,
    systemd_ntp_enabled: bool,
    service: str,
    service_state: str,
) -> dict[str, Any]:
    model = NtpLocalHealthV1.from_parts(
        synchronized=synchronized,
        systemd_ntp_enabled=systemd_ntp_enabled,
        service=service,
        service_state=service_state,
    )
    return finalize_facts(
        model.payload(),
        contract_id=NTP_LOCAL_HEALTH_CONTRACT_ID,
        requested=NTP_LOCAL_HEALTH_REQUESTED,
        observed=NTP_LOCAL_HEALTH_REQUESTED,
        assessment="healthy" if model.healthy else "unhealthy",
        non_claims=["server_serving_state", "peer_identity", "offset", "stratum"],
    )


def validate_ntp_local_health_v1(facts: dict[str, Any]) -> list[str]:
    return validate_facts(facts, expected_contract_id=NTP_LOCAL_HEALTH_CONTRACT_ID)


def build_docker_service_health_v1(payload: dict[str, Any]) -> dict[str, Any]:
    model = DockerServiceHealthV1.from_mapping(payload)
    return finalize_facts(
        model.payload(),
        contract_id=DOCKER_SERVICE_HEALTH_CONTRACT_ID,
        requested=DOCKER_SERVICE_HEALTH_REQUESTED,
        observed=DOCKER_SERVICE_HEALTH_REQUESTED,
        not_observed=["containers", "images", "stacks"],
        assessment="healthy" if model.healthy else "unhealthy",
        non_claims=["container_health", "docker_socket", "container_logs"],
    )


def validate_docker_service_health_v1(facts: dict[str, Any]) -> list[str]:
    return validate_facts(facts, expected_contract_id=DOCKER_SERVICE_HEALTH_CONTRACT_ID)


def build_host_security_posture_v1(
    *,
    signals: dict[str, Any],
    complete: bool,
    healthy: bool,
) -> dict[str, Any]:
    model = HostSecurityPostureV1.from_parts(
        signals=signals,
        complete=complete,
        healthy=healthy,
    )
    return finalize_facts(
        model.payload(),
        contract_id=HOST_SECURITY_POSTURE_CONTRACT_ID,
        requested=HOST_SECURITY_POSTURE_REQUESTED,
        observed=HOST_SECURITY_POSTURE_REQUESTED if model.complete else [],
        not_observed=[] if model.complete else ["one_or_more_security_signals"],
        assessment="healthy" if model.healthy else ("degraded" if model.complete else "unknown"),
        non_claims=["cis_compliance", "users", "packages", "ports", "ssh_configuration"],
    )


def validate_host_security_posture_v1(facts: dict[str, Any]) -> list[str]:
    return validate_facts(facts, expected_contract_id=HOST_SECURITY_POSTURE_CONTRACT_ID)


def build_ntp_server_observation_v1(
    *,
    daemon_state: str,
    serving_state: str,
    system_variables: dict[str, Any],
    healthy: bool,
) -> dict[str, Any]:
    model = NtpServerObservationV1.from_parts(
        daemon_state=daemon_state,
        serving_state=serving_state,
        system_variables=system_variables,
        healthy=healthy,
    )
    return finalize_facts(
        model.payload(),
        contract_id=NTP_SERVER_OBSERVATION_CONTRACT_ID,
        requested=NTP_SERVER_OBSERVATION_REQUESTED,
        observed=NTP_SERVER_OBSERVATION_REQUESTED if model.complete else [],
        not_observed=[] if model.complete else ["one_or_more_ntp_server_fields"],
        assessment="healthy" if model.healthy else ("degraded" if model.complete else "unknown"),
        non_claims=[
            "peer_identity",
            "peer_address",
            "remote_client_reachability",
            "firewall_state",
        ],
    )


def validate_ntp_server_observation_v1(facts: dict[str, Any]) -> list[str]:
    return validate_facts(facts, expected_contract_id=NTP_SERVER_OBSERVATION_CONTRACT_ID)


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
    encoded = json.dumps(facts, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(encoded) > MAX_FACTS_BYTES:
        errors.append("facts_too_large")
    if contract_id == BASIC_HOST_INVENTORY_CONTRACT_ID:
        errors.extend(_validate_basic_host_inventory_v1_shape(facts))
    if contract_id == NTP_LOCAL_HEALTH_CONTRACT_ID:
        errors.extend(_validate_ntp_local_health_v1_shape(facts))
    if contract_id == DOCKER_SERVICE_HEALTH_CONTRACT_ID:
        errors.extend(_validate_docker_service_health_v1_shape(facts))
    if contract_id == HOST_SECURITY_POSTURE_CONTRACT_ID:
        errors.extend(_validate_host_security_posture_v1_shape(facts))
    if contract_id == NTP_SERVER_OBSERVATION_CONTRACT_ID:
        errors.extend(_validate_ntp_server_observation_v1_shape(facts))
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


def _validate_basic_host_inventory_v1_shape(facts: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    complete = facts.get("complete") is True
    if facts.get("schema_ref") != BASIC_HOST_INVENTORY_SCHEMA_REF:
        errors.append("basic_host_inventory.schema_ref_mismatch")
    if not isinstance(facts.get("complete"), bool):
        errors.append("basic_host_inventory.invalid_complete")
    if not _bounded_string(facts.get("target"), max_length=128, required=True):
        errors.append("basic_host_inventory.invalid_target")

    os_value = facts.get("os")
    if not isinstance(os_value, dict):
        errors.append("basic_host_inventory.invalid_os")
    else:
        for key in ("pretty_name", "id", "version_id"):
            if not _bounded_string(
                os_value.get(key),
                max_length=256,
                required=complete and key == "id",
            ):
                errors.append(f"basic_host_inventory.invalid_os:{key}")

    for key, limit in (("kernel", 256), ("hostname", 128), ("uptime", 256)):
        if not _bounded_string(facts.get(key), max_length=limit, required=complete):
            errors.append(f"basic_host_inventory.invalid_{key}")

    load = facts.get("load_average")
    if not isinstance(load, dict):
        errors.append("basic_host_inventory.invalid_load_average")
    else:
        for key in ("one_minute", "five_minutes", "fifteen_minutes"):
            if not _optional_number(load.get(key)):
                errors.append(f"basic_host_inventory.invalid_load_average:{key}")
        for key in ("runnable_processes", "total_processes"):
            if not _optional_non_negative_int_value(load.get(key)):
                errors.append(f"basic_host_inventory.invalid_load_average:{key}")

    filesystem = facts.get("root_filesystem")
    if not isinstance(filesystem, dict):
        errors.append("basic_host_inventory.invalid_root_filesystem")
    else:
        if not _bounded_string(
            filesystem.get("mounted_on"),
            max_length=128,
            required=complete,
        ):
            errors.append("basic_host_inventory.invalid_root_filesystem:mounted_on")
        for key in ("blocks_1024", "used_1024", "available_1024"):
            if not _optional_non_negative_int_value(filesystem.get(key)):
                errors.append(f"basic_host_inventory.invalid_root_filesystem:{key}")

    memory = facts.get("memory_mib")
    if not isinstance(memory, dict):
        errors.append("basic_host_inventory.invalid_memory_mib")
    else:
        for key in ("total", "used", "free", "shared", "buff_cache", "available"):
            if not _optional_non_negative_int_value(memory.get(key)):
                errors.append(f"basic_host_inventory.invalid_memory_mib:{key}")

    if complete:
        if isinstance(filesystem, dict) and filesystem.get("mounted_on") != "/":
            errors.append("basic_host_inventory.complete_requires_root_mount")
        if isinstance(memory, dict) and memory.get("total") is None:
            errors.append("basic_host_inventory.complete_requires_memory_total")
    return errors


def _validate_ntp_local_health_v1_shape(facts: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if facts.get("schema_ref") != NTP_LOCAL_HEALTH_SCHEMA_REF:
        errors.append("ntp_local_health.schema_ref_mismatch")
    for key in ("synchronized", "systemd_ntp_enabled", "healthy"):
        if not isinstance(facts.get(key), bool):
            errors.append(f"ntp_local_health.invalid_{key}")
    for key in ("service", "service_state"):
        if not _bounded_string(facts.get(key), max_length=32, required=True):
            errors.append(f"ntp_local_health.invalid_{key}")
    return errors


def _validate_docker_service_health_v1_shape(facts: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if facts.get("schema_ref") != DOCKER_SERVICE_HEALTH_SCHEMA_REF:
        errors.append("docker_service_health.schema_ref_mismatch")
    for key in (
        "observation_scope",
        "service",
        "service_load_state",
        "service_active_state",
        "service_sub_state",
        "service_unit_file_state",
        "socket",
        "socket_load_state",
        "socket_active_state",
        "socket_sub_state",
        "socket_unit_file_state",
        "container_runtime_state",
    ):
        if not _bounded_string(facts.get(key), max_length=64, required=True):
            errors.append(f"docker_service_health.invalid_{key}")
    if not isinstance(facts.get("healthy"), bool):
        errors.append("docker_service_health.invalid_healthy")
    if facts.get("container_runtime_state") != "not_observed":
        errors.append("docker_service_health.container_runtime_must_be_not_observed")
    return errors


def _validate_host_security_posture_v1_shape(facts: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if facts.get("schema_ref") != HOST_SECURITY_POSTURE_SCHEMA_REF:
        errors.append("host_security_posture.schema_ref_mismatch")
    signals = facts.get("signals")
    if not isinstance(signals, dict):
        errors.append("host_security_posture.invalid_signals")
    else:
        for key in ("unattended_upgrades_enabled", "reboot_required"):
            if not isinstance(signals.get(key), bool):
                errors.append(f"host_security_posture.invalid_signals:{key}")
        for key in ("aslr_mode", "dmesg_restrict"):
            if not _optional_non_negative_int_value(signals.get(key)):
                errors.append(f"host_security_posture.invalid_signals:{key}")
    for key in ("complete", "healthy"):
        if not isinstance(facts.get(key), bool):
            errors.append(f"host_security_posture.invalid_{key}")
    return errors


def _validate_ntp_server_observation_v1_shape(facts: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if facts.get("schema_ref") != NTP_SERVER_OBSERVATION_SCHEMA_REF:
        errors.append("ntp_server_observation.schema_ref_mismatch")
    for key, limit in (("daemon_state", 32), ("serving_state", 64)):
        if not _bounded_string(facts.get(key), max_length=limit, required=True):
            errors.append(f"ntp_server_observation.invalid_{key}")
    variables = facts.get("system_variables")
    if not isinstance(variables, dict):
        errors.append("ntp_server_observation.invalid_system_variables")
    else:
        for key in ("stratum", "leap"):
            if not _optional_non_negative_int_value(variables.get(key)):
                errors.append(f"ntp_server_observation.invalid_system_variables:{key}")
        for key in ("offset_ms", "root_delay_ms", "root_dispersion_ms"):
            if not _optional_number(variables.get(key)):
                errors.append(f"ntp_server_observation.invalid_system_variables:{key}")
    if not isinstance(facts.get("healthy"), bool):
        errors.append("ntp_server_observation.invalid_healthy")
    return errors


def _bounded_text(value: Any, *, limit: int) -> str:
    return " ".join(str(value or "").split())[:limit]


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return round(max(0.0, min(result, 1_000_000.0)), 6)


def _optional_signed_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return round(max(-1_000_000.0, min(result, 1_000_000.0)), 6)


def _optional_non_negative_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        result = int(value)
    except (TypeError, ValueError):
        return None
    return max(0, min(result, 1_000_000_000_000))


def _bounded_string(value: Any, *, max_length: int, required: bool) -> bool:
    if not isinstance(value, str):
        return False
    if required and not value:
        return False
    return len(value) <= max_length


def _optional_number(value: Any) -> bool:
    return value is None or isinstance(value, (float, int))


def _optional_non_negative_int_value(value: Any) -> bool:
    return value is None or (isinstance(value, int) and value >= 0)
