# Zabbix PostgreSQL restore proof runbook

This runbook documents the operator-owned isolated restore proof for a Zabbix
PostgreSQL logical dump.

It complements both PBS VM-level backup and the Zabbix PostgreSQL application
backup timer. It proves that the latest custom-format dump can be restored into
an isolated PostgreSQL target and queried for basic application consistency. It
does not replace full VM restore testing and does not store database credentials
or dump files in Tecrax.

## Scope

The restore proof covers:

- selecting the latest validated Zabbix PostgreSQL custom-format dump;
- starting a disposable PostgreSQL container with a private temporary data
  directory;
- restoring the dump into a temporary database with `pg_restore`;
- validating basic schema and data presence;
- removing the temporary container, temporary data directory and generated
  restore credential.

The production Zabbix PostgreSQL container and production database are not
modified.

## Public and Private Boundary

Safe in public docs and sign-offs:

- target alias: `<zabbix-host>`;
- restore class: isolated disposable PostgreSQL target;
- dump format: PostgreSQL custom format;
- bounded validation counters;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- dump files;
- database credentials;
- generated temporary restore passwords;
- raw SQL dump contents;
- complete private filesystem layouts if they expose operational details.

## Procedure

### 1. Select a Dump

Select the newest validated Zabbix PostgreSQL custom-format dump from the
operator-owned local backup directory.

Do not copy the dump into Tecrax. Do not print database credentials.

### 2. Start an Isolated Target

Start a disposable PostgreSQL container with:

- a temporary data directory;
- a temporary database name;
- a temporary generated password;
- the selected dump mounted read-only.

Do not attach this container to the production Compose stack as an application
dependency. Do not reuse the production PostgreSQL data directory.

### 3. Restore

Run `pg_restore` against the temporary database with ownership and privilege
rewrite options appropriate for the disposable restore user.

Stop if restore exits non-zero.

### 4. Validate

Run bounded validation queries such as:

- public table count;
- host count;
- item count;
- trigger count;
- user count;
- Zabbix mandatory schema version from `dbversion`.

The validation should confirm that representative Zabbix application tables are
present and queryable. It is not a full functional application boot test.

### 5. Cleanup

Remove:

- disposable PostgreSQL container;
- temporary data directory;
- generated restore password file.

## Stop Conditions

Stop before sign-off if any of these are true:

- no recent validated dump exists;
- restore target cannot become ready;
- `pg_restore` fails;
- validation queries fail;
- temporary credentials or dump contents would need to be copied into Tecrax;
- cleanup cannot remove the disposable restore target.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `zabbix-postgresql-restore-proof`;
- target alias: `<zabbix-host>`;
- dump timestamp or public-safe dump identifier;
- restore target class: disposable PostgreSQL container;
- bounded validation summary;
- cleanup summary;
- explicit non-claims.

Non-claims:

- no production database mutation;
- no full Zabbix application boot from the restored database;
- no off-host backup coverage claim;
- no disaster-recovery one-command restore claim;
- no credential custody claim.

## 2026-07-01 Public-Safe Result

An isolated restore proof was completed against the latest available
custom-format Zabbix PostgreSQL dump.

Bounded validation result:

```text
zabbix_postgresql_restore_proof=ok
tables=203
hosts=420
items=20346
triggers=7691
users=2
schema_mandatory=7000000
```

The disposable PostgreSQL container, temporary data directory and generated
restore credential were removed after validation.
