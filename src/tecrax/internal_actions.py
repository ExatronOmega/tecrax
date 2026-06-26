from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tecrax.normalizers.diagnostics import aggregate_monitoring_host_diagnosis
from tecrax.normalizers.host import (
    normalize_basic_host_inventory,
    normalize_host_security_posture,
    normalize_ntp_server_observation,
)
from tecrax.normalizers.network import (
    assess_network_device_management_posture,
    normalize_network_device_inventory,
)
from tecrax.normalizers.services import (
    normalize_adguard_health,
    normalize_docker_services_health,
    normalize_ntp_health,
    normalize_portainer_health,
    normalize_zabbix_host_availability_summary,
    normalize_zabbix_health,
    normalize_zabbix_problem_summary,
)


def register_handlers() -> Mapping[str, Any]:
    return {
        "normalize_basic_host_inventory": normalize_basic_host_inventory,
        "normalize_ntp_health": normalize_ntp_health,
        "normalize_docker_services_health": normalize_docker_services_health,
        "normalize_zabbix_health": normalize_zabbix_health,
        "normalize_zabbix_problem_summary": normalize_zabbix_problem_summary,
        "normalize_zabbix_host_availability_summary": (
            normalize_zabbix_host_availability_summary
        ),
        "normalize_adguard_health": normalize_adguard_health,
        "normalize_portainer_health": normalize_portainer_health,
        "normalize_network_device_inventory": normalize_network_device_inventory,
        "normalize_host_security_posture": normalize_host_security_posture,
        "normalize_ntp_server_observation": normalize_ntp_server_observation,
        "assess_network_device_management_posture": assess_network_device_management_posture,
        "aggregate_monitoring_host_diagnosis": aggregate_monitoring_host_diagnosis,
    }
