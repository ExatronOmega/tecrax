# BookStack application-aware backup runbook

This public-safe runbook defines the bounded infrastructure semantics for a
recurring BookStack application backup. It complements VM/CT backups by
capturing the BookStack database, local uploads, themes and protected
application environment as one recovery set.

It does not contain real hosts, addresses, paths, certificate fingerprints,
credentials, backup contents or private retention inventory.

## Ownership boundary

- Tecrax owns the BookStack-specific backup meaning, safety gates and this
  runbook.
- Private operator context owns real targets, schedules, storage mappings and
  the environment-bound helper.
- Runtime custody owns SSH identities and any application credentials.
- RExecOp would own generic lifecycle and retry coordination if this operation
  is later promoted into a governed cross-environment workflow.
- GovEngine owns admission and approval policy.
- SCLite owns canonical evidence and receipts through existing contracts.

The private helper is not a generic backup framework or an RExecOp
replacement.

## Required recovery set

The backup must contain:

- a consistent logical dump of the connected BookStack database;
- local uploaded files and images;
- local theme data;
- the BookStack environment file under encrypted custody;
- the exact BookStack system CLI included by the supported upstream backup
  mechanism.

A VM or CT snapshot does not replace this application-consistent set.

## Encryption and custody

The plaintext backup archive may exist only as a short-lived root-owned file
on the BookStack host while the supported CLI creates and validates it. The
runtime operator reads it into process memory and encrypts it before durable
off-host storage.

The current mechanism uses CMS EnvelopedData with AES-256-CBC and a dedicated
RSA recipient certificate. Only the public recipient certificate is available
on the runtime host. The recovery private key remains in separate custody.

The operator plane must not retain the plaintext or encrypted backup payload.
It may retain only bounded non-secret state such as timestamps, sizes, hashes
and pass/fail results.

## Schedule and relation to VM backups

The application backup should complete before the daily VM/CT backup window so
the workload snapshot also contains a recent logical recovery set. A bounded
random delay is acceptable provided the worst-case start still leaves
sufficient time before the VM backup.

The exact time remains private operator configuration.

## Retention and NAS deletion boundary

Encrypted backup runs are append-only by default. Automatic pruning, overwrite
or deletion on NAS-hosted storage is forbidden unless a separate retention
decision and immediate operation-specific NAS authorization exist.

Where backup size is small, retaining all encrypted runs until that decision is
safer than introducing an implicit deletion policy. Capacity and artifact age
must still be monitored.

## Required helper behavior

The environment-bound helper must:

- default to a non-mutating plan and require `--apply`;
- fail closed on runtime, source and off-host host identity;
- verify the upstream BookStack system CLI and required services;
- verify the exact recipient certificate fingerprint;
- refuse to overwrite an existing run identifier or artifact;
- validate the created ZIP before reading it;
- keep payloads in memory on the operator plane;
- encrypt before durable off-host storage;
- verify off-host checksums for the encrypted artifact and manifest;
- remove the source plaintext in a `finally` path;
- write only non-secret latest/history state;
- perform no NAS inspection, pruning or deletion.

## Validation

For every scheduled run require:

- successful upstream BookStack backup;
- readable ZIP archive;
- expected non-zero size;
- successful encryption;
- off-host artifact and manifest;
- checksum equality;
- confirmed removal of the plaintext source;
- no service restart;
- active BookStack web and database services after the run.

An initial isolated restore/read proof is required before the recurring
schedule is trusted. Repeat the restore proof after material storage changes
and after the first real attachment exists.

## Stop conditions

Stop when:

- any host identity or storage target is ambiguous;
- the BookStack services or supported CLI are unavailable;
- the recipient certificate differs from private context;
- the destination run identifier already exists;
- the off-host storage is unavailable or read-only;
- ZIP validation, encryption or checksum comparison fails;
- the plaintext source cannot be removed;
- success would require NAS pruning, overwrite or management-plane access.

## Rollback

Disable the timer and restore the prior systemd units from the exact pre-state
backup. Do not delete already-created encrypted artifacts as part of rollback.

If a run fails before off-host validation, treat it as failed and preserve
non-secret diagnostics. The helper must still remove the short-lived plaintext
archive.

## Non-claims

This mechanism does not prove:

- full BookStack disaster recovery without a separate restore test;
- recovery of remote object storage not included by the upstream CLI;
- NAS recovery or internal NAS ACL correctness;
- an approved deletion-based retention policy;
- automatic remediation or autonomous restore.
