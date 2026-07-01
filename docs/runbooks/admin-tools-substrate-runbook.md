# Admin-tools substrate runbook

This runbook defines the operator-owned substrate used to keep live Tecrax
environments, wrappers, runtime evidence, private sign-offs and administrative
notes outside the public Tecrax repository.

It is not an active Tecrax profile intent. It is an operator-owned preparation
step for later governed runs.

## Scope

The substrate covers:

- private directory layout for live environments and wrappers;
- runtime storage location for RExecOp evidence and SCLite bundles;
- public-safe sign-off conventions;
- target alias conventions;
- backup expectation for the private admin material.

It does not deploy PBS, Samba, AdGuard, Zabbix, Grafana, Wazuh, Vaultwarden,
Ansible automation or a CMDB. It does not create a generic shell runner.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic target aliases, such as `proxmox-node-01`;
- generic role names, such as `host_chrony_ntp_server`;
- operation ids and artifact digests when they do not reveal topology;
- pass/fail status summaries;
- non-claims and next gates.

Must remain outside Git:

- real host addresses and private DNS names;
- SSH key paths, known-hosts paths and host fingerprints;
- wrapper implementation paths;
- live environment files with real connector bindings;
- target catalogs with real topology;
- serial inventories and physical bay mapping;
- raw command output and logs;
- passwords, tokens, API keys, recovery codes, certificate private keys and vault exports.

## Recommended Private Layout

Use an operator-owned root outside the public repository with subdirectories for:

- `bin/` - bounded wrappers with fixed argv and JSON output;
- `environments/` - live RExecOp environment YAML files;
- `runtime/` - RExecOp operation state, receipts and SCLite bundles;
- `signoffs/` - private or public-safe operator sign-offs;
- `docs/` - private topology notes and physical mapping;
- `scripts/` - deterministic operator scripts that are not profile APIs;
- `inventory/` - target catalogs and Ansible inventory, if introduced later;
- `backups/` - exported private admin material or backup manifests.

The exact path is private and must not be copied into public docs.

## Wrapper Rules

Every live wrapper must:

- accept only fixed actions declared by the Tecrax connector;
- reject unknown arguments;
- validate the target alias before connecting;
- validate bounded input, such as CIDR values, before mutation;
- emit one JSON object on stdout;
- write diagnostic errors to stderr;
- avoid generic shell passthrough;
- run through a narrow privilege boundary, not broad unattended admin access.

If root privileges are needed on a target, prefer a root-owned target-side script
with a narrow sudoers rule for `rexecop`. The script must validate its own
inputs and must not expose arbitrary command execution.

## Sign-Off Rules

Public-safe sign-offs should include:

- date;
- target alias and role;
- run class: manual/operator-owned or governed;
- operation id when applicable;
- validation result;
- receipt and SCLite artifact digests when applicable;
- bounded observed state;
- explicit non-claims;
- statement that private topology and secrets were omitted.

Do not include private paths, raw outputs, host addresses, CIDRs, fingerprints,
serial dumps or secret material.

## Validation

The substrate is ready when:

- private live wrappers and environments are outside Git;
- RExecOp runtime evidence is outside the public repository;
- public sign-offs can be written without private topology;
- current public artifacts pass a secret/topology scan;
- there is a selected backup target or a documented blocker for private admin material;
- the next service run can reference only aliases and roles in public docs.

## Non-Claims

This runbook does not prove external backup coverage, restore readiness, service
health, monitoring coverage, DNS correctness or compliance readiness. Those are
separate work packages.

## Next Gate

After this substrate exists, continue to PBS readiness. PBS must still be
treated as local operational backup only until a second copy outside the server
is implemented and tested.
