# Proxmox access handoff checkpoint

This checkpoint is the required first step before Tecrax can activate any
Proxmox mutation, including the planned chrony/NTP server slice.

It is not an active profile operation. It defines the operator-owned trust
handoff needed before RExecOp can safely plan or execute a mutating operation
against a freshly installed Proxmox host.

## Why this exists

The target host may reuse the address of an older server. Existing SSH host keys,
known-hosts entries, accounts, keys and automation assumptions must be treated as
stale until the new host identity is verified.

Tecrax must not create a live mutation path from an unverified transport. The
first reusable mutation can only start after an operator has established:

- the host is the intended freshly installed Proxmox node;
- the SSH host key was verified through an independent channel;
- the operator account exists;
- the private key and known-hosts files live outside this repository;
- the target binding in the operator environment is explicit and private.

## Required account rule

When a user account is created for Tecrax/RExecOp access on this Proxmox
environment, the username must be:

```text
rexecop
```

Do not add a second default username to public docs, examples, fixtures or
profile metadata for this environment.

## Public and private boundary

Safe in this repository:

- generic account name `rexecop`;
- generic target aliases, such as `proxmox-node-01`;
- placeholders like `/path/outside/repo/known_hosts`;
- high-level storage role names such as system pool and data pool;
- bounded command shapes and validation expectations.

Must remain outside this repository:

- real addresses and hostnames;
- SSH private keys;
- known-hosts files and raw fingerprints;
- passwords, tokens, cookies or API tickets;
- local inventory paths;
- shell history and one-off bootstrap transcripts;
- private Proxmox node names if they reveal topology.

## Operator handoff sequence

Perform this sequence from the Proxmox console, Web UI, or another trusted
out-of-band path before using RExecOp against the host.

1. Verify the fresh host identity and record the fingerprint in operator-owned
   notes outside Git.
2. Remove or isolate stale known-hosts entries for the reused address in the
   operator-owned known-hosts file.
3. Create the `rexecop` user on the Proxmox host.
4. Install only the public key intended for Tecrax/RExecOp access.
5. Grant no broad shell or sudo mutation authority by default. Any future
   mutation privilege must be scoped to an explicit Tecrax connector contract.
6. Write the real target binding into an operator-owned environment file outside
   Git.
7. Run a strict SSH probe with `StrictHostKeyChecking=yes` and an explicit
   `UserKnownHostsFile` outside Git.
8. Run the existing read-only host/NTP observations before activating the first
   mutating NTP slice.

## Access readiness evidence

The operator sign-off for this checkpoint may record only sanitized evidence:

- repository commit hash;
- generic target alias;
- account name `rexecop`;
- whether strict known-hosts verification passed;
- whether the read-only Proxmox host observation passed;
- whether the planned mutation remains blocked or ready for GovEngine admission.

Do not record the real host address, hostname, fingerprint, key path, operation
identifier, raw SSH output or private environment file path in public artifacts.

## Gate for the chrony/NTP mutation

The first Proxmox mutation may be designed only after this checkpoint is complete.
That mutation must still satisfy `docs/mutation-entry-criteria.md`:

- stable pre-state;
- one exact chrony/NTP server action contract;
- GovEngine admission before backend execution;
- post-state validation;
- rollback or compensation;
- target lock and idempotency;
- SCLite evidence chain;
- no unattended apply and no direct LLM execution.

The expected first mutating shape is a bounded chrony configuration operation
that makes the Proxmox node serve NTP for an operator-declared network scope. The
network scope, upstream servers and any local policy details stay outside Git
until they can be represented as sanitized placeholders and fixed validation
rules.
