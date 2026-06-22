# Ubuntu host read-only inventory

This runbook covers only `collect_basic_host_inventory` over `ssh_readonly`.

## Operator prerequisites

- dedicated target account without sudo or Docker/admin groups;
- SSH private key outside the repository;
- target fingerprint verified through an independent channel;
- operator-managed `known_hosts` outside the repository with strict checking;
- `REXECOP_SECRETS_FILE` outside the repository and mode `0600`;
- environment copy outside the repository with the real host address;
- explicit operator approval before the real SSH run.

Do not use `accept-new`. Do not add sudo, service management, Docker commands,
configuration changes, arbitrary `cat`, arbitrary command arguments, or log collection.

## Run

Copy `examples/environments/ubuntu-host.readonly.example.yaml` outside the repository,
replace only the target host and operator-owned paths, then run from an isolated runtime
directory:

```bash
export REXECOP_SECRETS_FILE=/path/outside/repo/secrets.yaml
rexecop plan --profile tecrax --env environment.yaml \
  --intent collect_basic_host_inventory --target monitoring-host-01 --mode dry_run
rexecop start --operation OPERATION_ID
rexecop validate --operation OPERATION_ID
rexecop status --operation OPERATION_ID
rexecop history --operation OPERATION_ID
```

The `produce_receipt` workflow step emits the SCLite bundle during `start`.

The environment allowlist must exactly match the profile command shapes. Any changed
command, argument, backend, unknown action, mutating action, or unmatched policy rule
must fail closed before connector execution.
