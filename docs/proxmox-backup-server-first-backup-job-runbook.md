# Proxmox Backup Server first backup job runbook

This runbook covers the first PBS backup job after PBS deployment and
post-deploy hardening.

It is not an active Tecrax profile intent and does not add a backup connector.
It is an operator-owned procedure for producing a bounded first-backup sign-off.

## Scope

The first backup pass covers:

- selecting a disposable or low-risk initial VM/CT;
- defining initial retention;
- creating a backup job in Proxmox;
- running or waiting for one successful backup;
- validating backup presence in PBS;
- public-safe first-backup sign-off.

It does not prove restore, define long-term compliance retention, configure
off-host replication, or claim all workloads are protected.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic source workload role, such as `disposable-test-vm`;
- backup job class and schedule class;
- retention summary;
- bounded success/failure result;
- PBS datastore alias if non-sensitive;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- real VM/CT ids, names and addresses if private;
- repository URLs, namespaces and exact backup paths;
- raw backup logs and task output;
- backup contents, file names and guest data;
- credentials, API tokens and encryption keys.

## Prerequisites

- PBS deployment sign-off exists.
- PBS post-deploy hardening is complete or explicitly risk-accepted.
- PBS datastore is mounted and listed.
- A disposable or low-risk first workload exists.
- Restore proof plan is known before the backup is treated as useful.

## Procedure

### 1. Select the first workload

Prefer a disposable test VM/CT. If a real workload is used, record only its
generic role in public evidence.

Do not use a domain controller, vault, security system or sole critical service
as the first proof target unless restore procedure and rollback are already
planned.

### 2. Define initial retention

Define a conservative initial retention policy before creating the job. The
policy should be explicit enough to prevent unbounded growth, but it does not
need to be final.

Record public-safe retention shape only, for example:

- daily/weekly/monthly class;
- prune enabled or deferred;
- garbage collection planned or deferred.

### 3. Create the backup job

Create the job through Proxmox/PBS tooling, not by hand-editing job files unless
the operator has a separate rollback plan.

Keep exact endpoint, credential and workload details outside Git.

### 4. Run and validate the first backup

A first-backup gate passes only when:

- the job completes successfully;
- PBS lists the resulting snapshot or backup group;
- datastore remains mounted;
- PBS services remain active;
- failure notification path is at least identified, even if not final.

If the job fails, record only the bounded failure class and next action. Do not
paste raw logs into public sign-off.

## Stop Conditions

Stop before sign-off if any of these are true:

- PBS hardening is incomplete and not explicitly risk-accepted;
- retention is undefined;
- no disposable or low-risk workload is available;
- backup job cannot be validated in PBS;
- backup success would require exposing raw job logs or guest contents;
- restore proof has no planned target.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- generic PBS target alias;
- generic source workload role;
- run class: `pbs-first-backup-job`;
- retention summary;
- job result summary;
- datastore listing summary;
- explicit non-claims.

Non-claims:

- no restore readiness until restore proof passes;
- no protection for all workloads unless each is covered by policy;
- no external disaster recovery until off-host copy exists and is tested.

## Next Gate

After the first successful backup, perform restore proof. Backup-job success is
not enough to unblock critical service dependency on PBS.
