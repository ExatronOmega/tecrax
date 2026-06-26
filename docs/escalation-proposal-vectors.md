# Escalation proposal vectors

Tecrax can project a bounded `tecrax.monitoring_host_diagnosis@1.0` result into
an SCLite `escalation_proposal.v0.1` advisory artifact. This is a profile-owned
domain projection for operator review, not an execution path.

The proposal contains only:

- SCLite escalation proposal metadata;
- a deterministic proposal id;
- the source reaction id;
- one suggested outcome;
- an optional read-only Tecrax intent ref for `run_intent` or `retry_intent`;
- bounded reason-code summaries from diagnosis findings and continued failures;
- relative evidence artifact refs;
- authority flags proving `trusted=false` and `may_execute=false`.

It must not contain target addresses, credentials, HTTP URLs, shell commands,
connector payloads, raw stdout/stderr, full logs, package names, Zabbix object
identifiers, Portainer objects, Docker socket data, remediation steps or policy
decisions.

## Boundary

```text
Tecrax diagnosis facts
  -> Tecrax bounded proposal vector
  -> RExecOp reaction-proposal-validate
  -> operator/GovEngine decision before any follow-up operation
```

Tecrax owns the infrastructure vocabulary and validates that the suggested
follow-up, if present, is an existing read-only Tecrax intent. RExecOp owns the
generic untrusted proposal validator and still returns `may_execute=false`.
GovEngine owns any future admission decision. SCLite owns the canonical artifact
schema.

## Build and validate

Use the Python API from automation that already has a bounded diagnosis artifact:

```python
from tecrax import build_monitoring_host_escalation_proposal

proposal = build_monitoring_host_escalation_proposal(
    operation_id="op-source",
    reaction_id="reaction-source",
    diagnosis=diagnosis,
)
```

Then validate through RExecOp before presenting or carrying it forward:

```bash
rexecop reaction-proposal-validate \
  --profile tecrax \
  --proposal proposal.json
```

Validation success means only that the artifact is a bounded untrusted proposal
and references a compatible read-only intent. It does not authorize execution.

## Rejections

Tecrax rejects proposal vectors that include unsupported fields, unknown or
non-read-only intents, intent refs on plain escalation/no-op outcomes, absolute
or escaping evidence paths, raw command payloads, URLs, token/password markers or
oversized explanations.
