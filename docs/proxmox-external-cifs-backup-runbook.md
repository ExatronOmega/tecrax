# Proxmox external CIFS backup runbook

This runbook covers the operator-owned external CIFS backup gate for the
Proxmox deployment.

It complements local PBS backup. It does not turn Tecrax into a backup
orchestration tool and does not claim full disaster recovery until restore or
verification from the external target is proven.

## Scope

This gate covers:

- adding an external CIFS storage target to Proxmox;
- scheduling VM/CT backups for selected base services;
- running the first external backup set;
- validating that Proxmox can list the external backup artifacts;
- recording public-safe sign-off evidence.

It does not configure the external storage appliance, expose share credentials,
replace PBS, prove full disaster recovery or cover every future workload.

## Public and Private Boundary

Safe in public docs and sign-offs:

- storage class: external CIFS/SMB target;
- Proxmox storage alias;
- VM/CT aliases or service roles;
- backup mode, compression and retention class;
- first-backup validation summary;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- CIFS endpoint address and share path;
- CIFS username, password and credential files;
- appliance SSH configuration and legacy cipher details;
- raw mount options if they expose credentials or topology;
- backup contents and full raw logs.

## Prerequisites

- Proxmox host readiness gate is complete.
- Local PBS backup exists for base workloads or is explicitly tracked.
- External CIFS target has an operator-created account.
- CIFS credentials are entered by the operator into a private root-owned or
  operator-owned secret path outside Git.
- The target is reachable from the Proxmox host over SMB.

## Procedure

### 1. Validate the CIFS target

Validate reachability and authentication without printing credentials.

Direct-share access is sufficient even if the share is not browseable.

### 2. Add Proxmox storage

Add a Proxmox CIFS storage entry with:

- content: backups only;
- SMB version pinned to an operator-approved version;
- a non-secret storage alias;
- credentials handled by Proxmox/private storage, not Git.

Validate the storage is active with the Proxmox storage layer.

### 3. Select backup inventory

Select a bounded first inventory of base services.

Do not include the local PBS VM in a generic external `vzdump` set unless there
is a specific design for PBS datastore export, sync or recovery. PBS requires a
separate backup and restore strategy.

### 4. Create a scheduled job

Create a scheduled Proxmox backup job for the selected base services.

Recommended first settings:

- mode: snapshot;
- compression: zstd;
- retention: daily, weekly and monthly keeps;
- notes template that names the class of backup without exposing private
  topology.

### 5. Run the first backup set

Run a manual first backup set after the scheduled job is present. This proves
the credentials, storage mount and workload backup path before relying on the
schedule.

### 6. Validate

Validate:

- Proxmox reports the CIFS storage as active;
- Proxmox lists one backup artifact for each selected first-pass workload;
- the CIFS mount contains the expected backup, note and log files;
- the job definition remains enabled with the intended inventory and retention;
- no credentials entered Git, chat, shell output or sign-off artifacts.

## Stop Conditions

Stop before sign-off if any of these are true:

- the storage target is not active in Proxmox;
- authentication only works by exposing credentials in public artifacts;
- the share is in the same failure domain as the Proxmox host;
- selected workloads are ambiguous or include PBS without a PBS-specific plan;
- first backup artifacts cannot be listed by Proxmox;
- external restore or verification is being claimed without a proof.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- run class: `proxmox-external-cifs-backup`;
- storage class and storage alias;
- selected workload aliases or service roles;
- schedule and retention class;
- first-backup validation summary;
- explicit non-claims.

Non-claims:

- no full disaster recovery proof;
- no external restore proof yet;
- no PBS datastore off-host sync proof;
- no all-workload coverage;
- no secret custody proof in public docs.

## Next Gate

Perform an external restore proof or equivalent verification from the CIFS
target, then document the recovery procedure and remaining workload gaps.
