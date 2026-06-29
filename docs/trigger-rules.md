# Tecrax trigger rules

Tecrax owns only the domain meaning of infrastructure trigger events. RExecOp owns
event intake, dedupe, cooldown, queueing and operation planning mechanics. GovEngine
still owns admission, and SCLite owns the evidence/receipt chain.

The active trigger rule pack is
`src/tecrax/profile/triggers/trigger_rules.yaml`.

## Active source-line rules

`network.host_observed` is the first bounded event family:

- known host, `payload.known=true`, `payload.target_kind=host`:
  plan `collect_basic_host_inventory` in `dry_run` mode for the catalog target id
  carried in event `subject`;
- unknown host, `payload.known=false`:
  escalate only; do not plan an operation and do not scan, isolate, monitor or mutate
  the host.

The `subject` value must be an operator-owned target catalog id, not an IP address,
hostname, username, path or secret. Real catalog entries remain outside Git. The
sanitized example catalog uses `monitoring-host-01` only as a public placeholder.

This rule family is part of the current coordinated stack line. It requires the
RExecOp trigger event intake with `catalog_target_from` support and remains
bounded to dry-run planning or escalation only.

## Non-goals

- no discovery engine;
- no network scanner;
- no scheduler ownership in Tecrax;
- no auto-start;
- no mutation;
- no remediation;
- no direct command execution from trigger rules;
- no policy decisions in Tecrax.
