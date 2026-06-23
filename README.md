# Tecrax

Tecrax is a governed infrastructure-operations runtime/profile built on GovEngine and SCLite.

Current published baseline: `tecrax==0.3.4a0` ([PyPI](https://pypi.org/project/tecrax/0.3.4a0/)), depending on
`govengine>=0.15.0,<0.16`, `sclite-core>=1.0.4,<1.1`, and `rexecop>=0.2.5a0,<0.3`.

This package provides:

- **RExecOp domain profile** — bundled YAML profile with intents, workflows, connectors,
  and validation rules (entry point `rexecop.profiles:tecrax`).
- **Local fixture review** — dry-run proof slice without live infrastructure.
- **Read-only host inventory profile** — fixed SSH command shapes and bounded
  normalization for operator-configured Ubuntu inventory.
- **Verified read-only service slices** — NTP synchronization and Docker systemd service
  health over fixed SSH commands, plus bounded Zabbix API version health through RExecOp
  `http_api`.
- **Monitoring-host reaction pack** — deterministic domain findings map only to
  existing read-only intents; unknown states escalate without a free-form action.

It does not execute infrastructure changes or manage credentials. Live SSH execution
is performed by RExecOp only from explicit operator configuration outside this package.

Planned foundation:

```text
Tecrax -> GovEngine -> SCLite
```

- SCLite owns lifecycle/proof/review artifacts.
- GovEngine owns deterministic governed-runtime kernel mechanics.
- Tecrax owns the infrastructure-operations profile semantics, fixture review
  payloads, UX, and future host integrations when those boundaries are mature.

## RExecOp profile

Install `tecrax` alongside `rexecop` to register the domain profile:

```bash
pip install rexecop tecrax
rexecop profile list
```

The profile root is exposed via `tecrax:profile_root` (directory `src/tecrax/profile/`).

## Deterministic reactions

Tecrax owns the monitoring vocabulary and rules in
`src/tecrax/profile/reactions/reaction_pack.yaml`. Build a canonical observation
from a bounded `diagnose_monitoring_host` result, then pass it to RExecOp:

```bash
tecrax reaction-observation \
  --input diagnosis.json \
  --operation op-source \
  --target monitoring-host-01 > observation.json

rexecop reaction-plan \
  --profile tecrax \
  --env /path/outside/repo/environment.yaml \
  --observation observation.json \
  --target monitoring-host-01
```

The first release is deliberately read-only. It can re-run bounded host
inventory, NTP, Docker service, or Zabbix checks; a healthy observation is `no_op`, and an
unclassified state is `escalate`. RExecOp owns deterministic mechanics and
lifecycle, GovEngine owns admission, and SCLite owns the evidence chain.

## Local fixture proof

```bash
tecrax fixture-review --service demo-web
```

The command emits a public-safe fixture review payload. It uses GovEngine
profile/planning/supervision/runtime-review contracts and binds its fixture
receipt through an SCLite artifact descriptor. It has no live runner, host
inventory, credential path, or infrastructure adapter.

The `0.3.3-alpha` line adds the profile-owned read-only reaction pack over
RExecOp `0.2.5a0` and SCLite `1.0.4`. It does not add a second policy engine,
lifecycle runner, or truth layer.

## Validation

```bash
python scripts/validate_public_truth.py
python -m pytest -q
```

The validator keeps this package as a second-host proof surface only. Any future
infrastructure runner, inventory, credential, scheduler, or carrier-adapter
claim must be backed by code and tests before it becomes public truth.
