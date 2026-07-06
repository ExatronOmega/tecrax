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
- target model for the dedicated admin-tools runtime node;
- the rule that new runtime artifacts must be recorded for admin-tools adoption,
  not left only on an operator workstation.

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

## Runtime Node Model

The dedicated admin-tools host is the target runtime/operator node for Tecrax
and RExecOp operations. It should run bounded operator wrappers, hold runtime
policy files, keep private state, collect sign-offs and eventually host the
controlled Tecrax/RExecOp runtime.

The operator workstation remains the development workstation. Use it for repo
editing, tests, commits, experiments and multi-repository development. Do not
turn the production admin-tools host into an uncontrolled development
environment.

From the point this model is adopted, new runtime artifacts should not be
created only on the operator workstation without either:

- writing the equivalent artifact into the admin-tools substrate; or
- recording an explicit migration task, blocker and validation gate.

This applies to wrapper scripts, operator policy files, target context,
credential references, private state directories, sign-off locations and smoke
commands. It does not mean copying credential values blindly.

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
- `context/` - host/service/network-device context and credential references
  without credential values;
- `state/` - private runtime state such as duplicate suppression files, with
  restrictive permissions.

The exact path is private and must not be copied into public docs.

On the admin-tools runtime node, choose one stable root and treat it as the
canonical operator substrate root. Keep a compatibility wrapper or documented
environment variable if the workstation still uses a different local root during
the transition.

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

## Admin-Tools Bootstrap Checklist

Bootstrap the admin-tools runtime node in a small, auditable sequence:

1. Create the substrate root with restrictive ownership and permissions.
2. Copy or reconstruct public-safe context files: host aliases, service aliases,
   network-device aliases, guardrails and credential references.
3. Install bounded wrappers only after reviewing fixed argv and failure modes.
4. Create private state directories with restrictive permissions before running
   any duplicate-suppression or routing helper.
5. Configure credential provider references, not raw secret values in Git,
   runbooks, sign-offs or shell history.
6. Install the Tecrax package or checkout needed for runtime use from the
   intended branch/tag; keep development experiments on the workstation.
7. Run read-only smoke tests before any mutation.

## Smoke Tests

The first admin-tools substrate smoke should prove only that the runtime node can
read its context and execute bounded read-only/operator helpers:

- list host and service aliases;
- list credential references without showing values;
- run the narrow access check accepted for the current deployment phase;
- run the Zabbix-to-GLPI shadow pipeline in dry-run mode;
- verify that private outputs and state files are not world-readable;
- write a public-safe sign-off omitting private topology and secrets.

Do not enable live ticket creation, key rotation, SNMP credential rotation,
endpoint rollout or CA operations during this bootstrap smoke.

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
- admin-tools has a working runtime substrate root or a documented migration
  blocker;
- runtime artifacts created on the workstation are mirrored to admin-tools or
  tracked as migration tasks;
- public sign-offs can be written without private topology;
- current public artifacts pass a secret/topology scan;
- there is a selected backup target or a documented blocker for private admin material;
- the next service run can reference only aliases and roles in public docs.

## Non-Claims

This runbook does not prove external backup coverage, restore readiness, service
health, monitoring coverage, DNS correctness or compliance readiness. Those are
separate work packages.

## Next Gate

After the original private substrate exists, continue to PBS readiness. After the
dedicated admin-tools runtime node exists, migrate current operator wrappers and
run read-only smoke tests before expanding live automation.
