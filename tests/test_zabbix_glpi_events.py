from __future__ import annotations

from tecrax.zabbix_glpi_events import (
    ZabbixProblemQuery,
    alert_event_to_mapping,
    filter_zabbix_live_candidate_events,
    load_infrastructure_hosts_file,
    zabbix_problem_get_payload,
    zabbix_problem_to_alert_event,
    zabbix_trigger_host_payload,
    zabbix_live_routing_decision,
)


def test_zabbix_problem_payload_is_bounded_and_warning_plus_by_default() -> None:
    payload = zabbix_problem_get_payload(ZabbixProblemQuery())

    assert payload["method"] == "problem.get"
    assert payload["params"]["severities"] == [2, 3, 4, 5]
    assert payload["params"]["limit"] == 50
    assert payload["params"]["suppressed"] is False
    assert "selectHosts" not in payload["params"]


def test_zabbix_trigger_host_payload_maps_problem_objectids_to_hosts() -> None:
    payload = zabbix_trigger_host_payload(["1002", "1001", "1001"])

    assert payload["method"] == "trigger.get"
    assert payload["params"]["triggerids"] == ["1001", "1002"]
    assert payload["params"]["selectHosts"] == ["host", "name"]


def test_zabbix_problem_to_alert_event_maps_glpi_fields() -> None:
    event = zabbix_problem_to_alert_event(
        {
            "eventid": "123",
            "name": "High disk usage on /mnt/monitoring",
            "severity": "4",
            "clock": "1783339200",
            "hosts": [{"host": "frigate01", "name": "Monitoring wizyjny"}],
        },
        source_url_base="http://zabbix.local",
    )

    assert event.source == "Zabbix"
    assert event.event_id == "123"
    assert event.host == "frigate01"
    assert event.summary == "High disk usage on /mnt/monitoring"
    assert event.raw_severity == "4"
    assert event.raw_trigger == "High disk usage on /mnt/monitoring"
    assert event.started_at.startswith("2026-07-06T")
    assert "filter_eventids%5B0%5D=123" in event.source_url


def test_alert_event_to_mapping_matches_glpi_router_input_shape() -> None:
    event = zabbix_problem_to_alert_event(
        {
            "eventid": "321",
            "name": "Host unavailable by ICMP",
            "severity": 3,
            "clock": "1783339200",
            "hosts": [{"name": "pve01"}],
        }
    )

    assert alert_event_to_mapping(event) == {
        "source": "Zabbix",
        "event_id": "321",
        "host": "pve01",
        "summary": "Host unavailable by ICMP",
        "raw_severity": "3",
        "raw_trigger": "Host unavailable by ICMP",
        "started_at": event.started_at,
        "source_url": "",
        "category": "",
    }


def test_host_unavailable_is_live_candidate_only_for_infrastructure_hosts() -> None:
    infra_event = zabbix_problem_to_alert_event(
        {
            "eventid": "1",
            "name": "Host unavailable by ICMP",
            "severity": 3,
            "clock": "1783339200",
            "hosts": [{"host": "pve01"}],
        }
    )
    endpoint_event = zabbix_problem_to_alert_event(
        {
            "eventid": "2",
            "name": "Host unavailable by ICMP",
            "severity": 3,
            "clock": "1783339200",
            "hosts": [{"host": "mbp-lt-001"}],
        }
    )

    assert (
        zabbix_live_routing_decision(
            infra_event,
            infrastructure_hosts={"pve01", "zbx01"},
        ).route
        == "live_candidate"
    )
    endpoint_decision = zabbix_live_routing_decision(
        endpoint_event,
        infrastructure_hosts={"pve01", "zbx01"},
    )
    assert endpoint_decision.route == "shadow_only"
    assert "outside infrastructure allowlist" in endpoint_decision.reason


def test_live_candidate_filter_excludes_user_endpoints_and_non_allowlisted_events() -> None:
    events = [
        zabbix_problem_to_alert_event(
            {
                "eventid": "1",
                "name": "Host unavailable by ICMP",
                "severity": 3,
                "clock": "1783339200",
                "hosts": [{"host": "pve01"}],
            }
        ),
        zabbix_problem_to_alert_event(
            {
                "eventid": "2",
                "name": "Host unavailable by ICMP",
                "severity": 3,
                "clock": "1783339200",
                "hosts": [{"host": "mbp-lt-001"}],
            }
        ),
        zabbix_problem_to_alert_event(
            {
                "eventid": "3",
                "name": "Number of installed packages has been changed",
                "severity": 2,
                "clock": "1783339200",
                "hosts": [{"host": "zbx01"}],
            }
        ),
    ]

    live_candidates = filter_zabbix_live_candidate_events(
        events,
        infrastructure_hosts={"pve01", "zbx01"},
    )

    assert [event.event_id for event in live_candidates] == ["1"]


def test_critical_disk_is_live_candidate_for_infrastructure_except_known_frigate_retention() -> None:
    zbx_disk = zabbix_problem_to_alert_event(
        {
            "eventid": "10",
            "name": "Linux: FS [/]: Space is critically low (used > 95%)",
            "severity": 4,
            "clock": "1783339200",
            "hosts": [{"host": "zbx01"}],
        }
    )
    frigate_retention = zabbix_problem_to_alert_event(
        {
            "eventid": "11",
            "name": "Linux: FS [/mnt/monitoring]: Space is critically low (used > 90%)",
            "severity": 3,
            "clock": "1783339200",
            "hosts": [{"host": "frigate01"}],
        }
    )

    assert (
        zabbix_live_routing_decision(
            zbx_disk,
            infrastructure_hosts={"zbx01", "frigate01"},
        ).route
        == "live_candidate"
    )
    retention_decision = zabbix_live_routing_decision(
        frigate_retention,
        infrastructure_hosts={"zbx01", "frigate01"},
    )
    assert retention_decision.route == "shadow_only"
    assert "known expected storage pressure" in retention_decision.reason


def test_backup_failure_and_ad_dns_service_failures_are_live_candidates_for_infrastructure() -> None:
    backup_failure = zabbix_problem_to_alert_event(
        {
            "eventid": "20",
            "name": "PBS backup job failed",
            "severity": 4,
            "clock": "1783339200",
            "hosts": [{"host": "pbs01"}],
        }
    )
    dns_failure = zabbix_problem_to_alert_event(
        {
            "eventid": "21",
            "name": "DNS service is down",
            "severity": 4,
            "clock": "1783339200",
            "hosts": [{"host": "dc01"}],
        }
    )
    core_failure = zabbix_problem_to_alert_event(
        {
            "eventid": "22",
            "name": "Grafana service is down",
            "severity": 4,
            "clock": "1783339200",
            "hosts": [{"host": "grafana-01"}],
        }
    )

    infra_hosts = {"pbs01", "dc01", "grafana-01"}

    assert (
        zabbix_live_routing_decision(backup_failure, infrastructure_hosts=infra_hosts).reason
        == "backup failure on infrastructure host"
    )
    assert (
        zabbix_live_routing_decision(dns_failure, infrastructure_hosts=infra_hosts).reason
        == "AD/DNS service unavailable"
    )
    assert (
        zabbix_live_routing_decision(core_failure, infrastructure_hosts=infra_hosts).reason
        == "core infrastructure service unavailable"
    )


def test_load_infra_hosts_from_operator_context_shape(tmp_path) -> None:  # noqa: ANN001
    path = tmp_path / "alert-routing.yaml"
    path.write_text(
        "\n".join(
            [
                "version: 1",
                "alert_routing:",
                "  zabbix:",
                "    infrastructure_hosts:",
                "      - pve01",
                "      - zbx01",
            ]
        ),
        encoding="utf-8",
    )

    assert load_infrastructure_hosts_file(path) == ["pve01", "zbx01"]
