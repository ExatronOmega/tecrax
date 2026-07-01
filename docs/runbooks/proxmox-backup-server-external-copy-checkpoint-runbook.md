# Proxmox Backup Server external copy checkpoint runbook

This runbook covers the decision checkpoint for an external/off-host backup copy
after local PBS deployment, backup job success and restore proof.

It is not an active Tecrax profile intent and does not add a backup connector.
It is an operator-owned decision and validation procedure for avoiding the false
claim that local PBS on the same physical server is disaster recovery.

## Scope

The checkpoint covers:

- selecting an external target class;
- defining copy cadence and custody;
- documenting restore expectations;
- validating the first external-copy proof when implemented;
- public-safe sign-off.

It does not mandate a specific storage product, expose repository credentials,
or replace workload-level restore tests.

## Public and Private Boundary

Safe in public docs and sign-offs:

- target class, such as NAS, offline disk, second server or remote PBS;
- whether the checkpoint is selected, implemented, tested or deferred;
- cadence class;
- explicit risk acceptance if deferred;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- target addresses, repository URLs and share paths;
- credentials, tokens, encryption keys and recovery phrases;
- raw sync logs and backup contents;
- device serials or inventory mapping if private;
- schedules that reveal sensitive operational windows.

## Prerequisites

- Local PBS deployment exists.
- First backup job is complete or planned.
- Restore proof is complete or planned.
- Operator understands that same-host PBS is local operational backup only.

## Target Classes

Valid external-copy classes include:

- NAS or file server outside the Proxmox host;
- offline USB disk rotation;
- second server;
- remote PBS datastore;
- other operator-approved storage repository.

The target class is public-safe. Exact endpoint and credentials are private.

## Decision Procedure

### 1. Select or defer target class

Choose one:

- selected and ready for implementation;
- selected but blocked;
- deferred with explicit risk acceptance.

If deferred, record why and when the decision must be revisited.

### 2. Define copy model

Define privately:

- cadence;
- encryption and key custody;
- retention interaction with local PBS;
- failure notification path;
- restore-test expectation.

Public sign-off records only bounded status and target class.

### 3. Validate first external copy

When implemented, validate:

- copy completed successfully;
- copied artifact or repository is visible at target;
- restore or verification method exists;
- credentials and keys did not enter Git, chat or LLM/tooling.

### 4. Restore from external copy

External-copy coverage is not complete until at least one restore or equivalent
verification from the external target succeeds.

## Stop Conditions

Stop before claiming off-host coverage if any of these are true:

- target class is not selected;
- copy has not completed;
- encryption keys or credentials would be exposed;
- copied data cannot be verified;
- no external restore or verification method exists;
- target is physically or logically the same failure domain as the Proxmox host.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- generic PBS target alias;
- run class: `pbs-external-copy-checkpoint`;
- selected target class or deferred status;
- copy cadence class;
- first-copy status;
- external verification/restore status;
- explicit non-claims.

Non-claims:

- no disaster recovery until external copy and verification exist;
- no secret custody proof in public docs;
- no replacement for workload restore proof;
- no all-service coverage without explicit job inventory.

## Next Gate

After external copy is selected and tested, update the operational roadmap with
which critical services may depend on PBS and which still need their own backup
and restore proof.
