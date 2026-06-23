# Network device read-only inventory

This runbook covers `collect_network_device_inventory_readonly` for one managed
network device exposed through an operator-managed local CLI wrapper.

Tecrax owns the domain meaning of the intent, workflow, validation and normalized
result. RExecOp owns lifecycle and connector execution. GovEngine owns admission.
SCLite owns evidence and receipts. The wrapper, target address, SSH key material,
legacy SSH compatibility settings and any device-specific login setup stay outside
the repository.

## Operator prerequisites

- a local command named `tecrax-network-cli-readonly` on the operator host `PATH`;
- wrapper arguments limited to `system-info` and `ssh-status`;
- no generic passthrough mode for arbitrary device CLI commands;
- no write commands, configuration mode, reload, restart, password, VLAN, firewall,
  DNS, NTP, port security or SNMP configuration changes;
- private keys, known-hosts data and legacy SSH settings outside the repository;
- environment YAML outside the repository for real targets.

## Profile shape

The bundled connector `network_device_cli` uses `local_shell_readonly` and fixed
command shapes:

```text
tecrax-network-cli-readonly system-info
tecrax-network-cli-readonly ssh-status
```

The normalizer keeps only bounded device identity and management SSH status. It
does not preserve operator contact/location fields or user-account listings in
the normalized result.

## Safety notes

This slice observes legacy management access. It may report weak or old SSH
settings as `hardening_observations`, but it does not remediate them. Hardening
actions must be separate future intents with explicit policy, validation and
operator approval.
