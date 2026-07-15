from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate_secret_topology.py"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_secret_topology", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_private_deployment_markers_are_rejected() -> None:
    validator = _load_validator()
    examples = (
        "service.mbp.infra.lan",
        "GG_MBP_Staff",
        "GPO_MBP_Baseline_User",
        "OU=Workstations,OU=MBP,DC=mbp",
        r"\\nas01\home",
        "ODDZIAL-1",
        "SOWA client",
        "Bitdefender GravityZone",
    )

    for example in examples:
        assert validator.PRIVATE_DEPLOYMENT_MARKER.search(example), example


def test_generic_contract_markers_and_supported_products_are_allowed() -> None:
    validator = _load_validator()
    examples = (
        "<service>.<internal-domain>",
        "GG_<ORG>_Staff",
        "<supported-user-home-UNC>",
        "library-management application",
        "endpoint protection platform",
        "Wazuh agent",
        "Zabbix agent",
    )

    for example in examples:
        assert validator.PRIVATE_DEPLOYMENT_MARKER.search(example) is None, example
