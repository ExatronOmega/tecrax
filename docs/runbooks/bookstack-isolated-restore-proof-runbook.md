# BookStack isolated restore proof runbook

This runbook documents the operator-owned isolated restore proof for the
BookStack CT.

It proves that a BookStack backup can be restored into a temporary isolated CT
and that the application, database and uploaded-asset paths are queryable. It
does not claim final documentation migration, final HTTPS/PKI hardening, SSO or
one-command disaster recovery.

## Scope

The restore proof covers:

- selecting an existing BookStack CT backup;
- restoring it to a temporary CT ID;
- isolating the temporary CT from the production network before boot;
- validating local web, database and application data state;
- removing the temporary CT and its restored disk.

The production BookStack CT is not modified.

## Public and Private Boundary

Safe in public docs and sign-offs:

- target alias: `bookstack-01`;
- restore class: isolated temporary CT;
- broad validation counters;
- cleanup result;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- BookStack admin credentials;
- database credentials;
- application key;
- raw database dumps;
- uploaded files and private documentation contents;
- exact backup repository credentials or access paths.

## Procedure

### 1. Select Backup

Select an approved BookStack CT backup from the operator-owned backup storage.
Do not copy backup contents into Tecrax.

### 2. Restore To Temporary CT

Restore to a temporary CT ID that does not collide with production workloads.
Before boot, override the network configuration so the temporary CT cannot reuse
the production address or communicate on the production network.

### 3. Validate

Validate inside the temporary CT:

- local web endpoint returns a login/redirect response;
- database service is active;
- web service is active;
- BookStack application path exists;
- application environment file exists;
- database tables are present;
- current BookStack entity model is queryable;
- uploaded-asset directories exist.

For current BookStack releases, application content is represented through the
`entities` and related `entity_*` tables rather than older direct `books` or
`pages` tables.

### 4. Cleanup

Stop and destroy the temporary CT. Confirm there is no remaining temporary CT
configuration or restored disk.

## Stop Conditions

Stop before sign-off if any of these are true:

- temporary CT would boot with the production address;
- restore requires exposing credentials or content to Git/chat/public docs;
- web service or database service cannot be validated;
- BookStack application tables cannot be queried;
- temporary CT cannot be removed.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `bookstack-isolated-restore-proof`;
- target alias: `bookstack-01`;
- restore target class: temporary isolated CT;
- validation summary;
- cleanup summary;
- explicit non-claims.

Non-claims:

- no production mutation;
- no final documentation migration;
- no SSO/LDAP claim;
- no final HTTPS/PKI hardening claim;
- no one-command disaster recovery claim;
- no compliance documentation completion claim.

## 2026-07-01 Public-Safe Result

An isolated restore proof was completed from an existing BookStack CT backup to
a temporary CT target with production networking disabled.

Bounded validation result:

```text
bookstack_restore_proof=ok
web_code=302
db_service=mysql:active
web_service=nginx:active
db_tables=41
entities=14
entity_types=book:6,bookshelf:1,page:7
users=2
migrations=102
uploads=present
```

The temporary CT and restored disk were removed after validation.
