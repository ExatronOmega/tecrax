# Changelog

All notable Tecrax profile changes are documented here.

## Unreleased

- No changes after the `0.3.5a0` release.

## 0.3.5a0 - 2026-06-24

- Published the profile after GovEngine `0.16.0` and RExecOp `0.2.6a0` passed
  their public-index install gates.
- Raised the GovEngine/RExecOp floors to the coordinated B2 release lines.
- Removed the obsolete `fixture` extra that required RExecOp `<0.2` while the
  package itself required RExecOp `>=0.2.5a0`.

### B2 policy enforcement vector

- The sanitized Ubuntu `collect_basic_host_inventory` example now declares
  profile-owned receipt, output-digest, timeout, step-count, and output-size
  policy controls.
- Cross-repository tests verify that GovEngine projects those controls into a
  digest-bound admission consumed by RExecOp.
- Tecrax still owns only the intent, workflow, connector shapes, validation, and
  policy-pack semantics. Runtime enforcement remains in RExecOp, governance in
  GovEngine, and canonical evidence/receipt truth in SCLite.

## 0.3.4a0 - 2026-06-23

- Added profile-owned target/operation catalog metadata and sanitized operator
  catalog examples.
- Added bounded read-only Ubuntu monitoring-host and legacy network-device
  inventory/health slices with private runtime configuration kept outside Git.
- Added deterministic profile-owned reaction vectors over existing read-only
  intents.
