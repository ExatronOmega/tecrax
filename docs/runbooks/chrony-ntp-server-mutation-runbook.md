# Chrony NTP server mutation

This runbook covers `configure_chrony_ntp_server`, the first bounded Tecrax
mutation. It configures one host to serve NTP through chrony for one declared
IPv4 LAN subnet.

The operation is deterministic. An LLM may propose or explain the change, but
the execution path is only:

```text
Tecrax intent -> RExecOp plan -> GovEngine admission -> Tecrax connector backend
-> RExecOp lifecycle -> SCLite evidence
```

## Scope

The active contract is limited to:

- one managed file: `/etc/chrony/conf.d/tecrax-ntp-server.conf`;
- one strict IPv4 CIDR with prefix `/24` or narrower;
- chrony config parse validation by the operator wrapper in live mode;
- chrony service restart by the operator wrapper in live mode;
- post-state confirmation that the desired server state is applied.

The operation does not configure clients, firewall policy, upstream server
identity, DNS, DHCP, VM settings, storage, Proxmox cluster state or any generic
shell command.

## Operator prerequisites

- the access handoff in `../proxmox-access-handoff.md` is complete;
- target access uses the `rexecop` account;
- real target binding, SSH keys and known-hosts files stay outside Git;
- live execution uses an operator-owned wrapper outside Git;
- GovEngine admission is required before `apply`;
- no unattended apply is allowed.

The public example uses `fixture_only: true`. A live environment must replace it
with an operator-owned wrapper command. The wrapper is not a Tecrax public API;
it is local operator infrastructure that must implement only the fixed actions
declared by the `chrony_ntp_server` connector.

## Deterministic action contract

Connector: `chrony_ntp_server`

Backend: `tecrax_chrony_ntp`

Actions:

- `read_chrony_ntp_server_state`;
- `apply_chrony_ntp_server`;
- `rollback_chrony_ntp_server`.

The backend validates `allowed_subnet` as a strict IPv4 CIDR and rejects networks
broader than `/24`. In live mode it invokes the wrapper with fixed argv, never a
rendered shell command.

## Run

Use the sanitized fixture environment to prove planning, admission and evidence
shape without touching infrastructure:

```bash
rexecop plan --profile tecrax \
  --env examples/environments/chrony-ntp-server.apply.example.yaml \
  --intent configure_chrony_ntp_server \
  --target chrony-host-01 \
  --mode apply
```

In production, keep the real environment file outside Git and use a private
target alias. Do not commit real host addresses, wrapper paths, SSH paths,
known-hosts paths or operation identifiers.

## Validation

The profile validation checks:

- mutation state exists for `apply_chrony_ntp_server`;
- post-state reports `desired_state_applied=true`;
- SCLite receipt generation is part of the workflow.

The evidence intentionally carries bounded state only. It does not preserve raw
SSH output, private hostnames, fingerprints, key paths, local wrapper paths,
upstream identities or client lists.
