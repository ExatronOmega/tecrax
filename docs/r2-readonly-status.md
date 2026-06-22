# R2 read-only status

R2 extends manual, evidence-producing diagnostics. It does not add polling, alerts,
scheduling, or a second monitoring system.

## Implemented and verified

- `check_ntp_health`: fixed `timedatectl show` properties plus `systemctl is-active ntp`
  over `ssh_readonly`; validates synchronization and the discovered daemon state.
- `check_zabbix_container_health`: bounded JSON-RPC `apiinfo.version` through `http_api`;
  validates application reachability and reports `container_runtime_state: not_observed`.

Both workflows use plain PolicyEngine `allow`, bounded evidence, deterministic validation,
receipt generation and an SCLite bundle.

`diagnose_monitoring_host` aggregates host inventory, NTP and Zabbix. Connector failures
are retained as bounded step IDs plus error classes while later diagnostics continue. Its
validation means the diagnostic completed; component health remains a separate field.

## Explicit blockers

- `check_docker_services_health`: the dedicated SSH account cannot access the Docker socket.
  This is intentional. Membership in the `docker` group would grant mutation capability and
  must not be used as a read-only solution. A separate bounded adapter must be designed and
  reviewed before this intent exists.
- Portainer API discovery confirmed that authenticated API access uses a user token with
  that user's permissions. No token is accepted as a read-only boundary until the
  installation can provide a genuinely non-mutating role or a separately constrained API.
- `check_adguard_health`: no operator-confirmed management or health endpoint is available.
  Do not infer one from common ports or product defaults.

No Docker inspect, logs, exec, lifecycle command, configuration change, service restart, or
NTP modification is part of R2.
