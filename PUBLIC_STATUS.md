# Tecrax Public Status

- **Package version:** `0.3.3a0` (`0.3.2-alpha`)
- **Dependencies:** `govengine>=0.15.0,<0.16`, `sclite-core>=1.0.1,<1.1`, `rexecop>=0.2.4a0,<0.3`
- **RExecOp profile:** bundled at `src/tecrax/profile/` via `rexecop.profiles:tecrax`
- **Local fixture:** `tecrax fixture-review` — dry-run GovEngine/SCLite proof only
- **R1 profile slice:** `collect_basic_host_inventory` defines fixed read-only Ubuntu
  command shapes, bounded normalization, validation and a sanitized environment template
- **Execution boundary:** RExecOp owns operator-configured SSH execution; Tecrax does not
  manage credentials or embed target infrastructure data
- **Not claimed:** infrastructure mutation, credential management, carrier adapters,
  scheduler/storage, or production readiness
