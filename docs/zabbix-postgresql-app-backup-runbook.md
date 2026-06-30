# Zabbix PostgreSQL application backup runbook

This runbook covers the operator-owned application-level backup gate for the
Zabbix PostgreSQL database.

It complements PBS VM-level backup. It does not replace PBS, does not prove a
full application restore and does not store database credentials in Tecrax.

## Scope

The backup pass covers:

- creating a root-owned logical dump location on the Zabbix VM;
- creating a root-owned dump script;
- scheduling the dump through a systemd timer;
- validating the dump with `pg_restore -l`;
- retaining a small local rolling window;
- recording public-safe sign-off evidence.

It does not create an off-host copy, restore into a separate database, rotate
Zabbix credentials, configure Zabbix API tokens, or add monitored hosts.

## Public and Private Boundary

Safe in public docs and sign-offs:

- target alias and service role;
- timer/service names if generic;
- dump format;
- retention class;
- validation summary;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- database passwords and `.env` contents;
- backup files;
- complete backup paths if they expose private layout;
- raw dump output;
- Zabbix web credentials and API tokens.

## Prerequisites

- Zabbix VM deployment gate is complete.
- Docker Compose stack is healthy.
- PostgreSQL container is healthy.
- PBS VM-level backup already exists or an explicit exception is recorded.
- Operator account follows the environment hard rule: `rexecop`.

## Procedure

### 1. Inspect Existing Scheduling

Before adding a timer, inspect existing timers and local systemd units so the
new schedule does not replace or collide with existing operator-owned jobs.

### 2. Create Backup Location

Create a root-owned directory with restrictive permissions for logical dumps.
Do not make it world-readable.

Recommended retention for the initial baseline is a short local rolling window,
for example 14 days. Longer retention belongs in the backup policy after
storage growth is known.

### 3. Create Dump Script

Create a root-owned script that:

- runs `pg_dump` against the Zabbix PostgreSQL database from the database
  container;
- writes a PostgreSQL custom-format dump;
- validates the dump with `pg_restore -l`;
- moves the dump into place only after validation succeeds;
- removes old dumps according to the selected local retention.

The script must not print database credentials. It should use the running
container context and operator-owned secret material already present on the VM.

### 4. Create systemd Timer

Create a oneshot service and daily timer. Use `Persistent=true` so a missed run
executes after boot.

Do not use user crontabs for this baseline. A system timer is easier to inspect,
enable, disable and audit.

### 5. Run and Validate

Run the service once immediately. Validate:

- service exit status is success;
- timer is enabled and active;
- a dump file exists;
- dump is restrictive-permission only;
- `pg_restore -l` can read the latest dump;
- Zabbix web and server remain healthy.

## Stop Conditions

Stop before sign-off if any of these are true:

- PostgreSQL container is not healthy;
- dump requires exposing database credentials to LLM/tooling;
- dump validation fails;
- timer cannot be enabled;
- backup path is world-readable;
- Zabbix web/server health regresses after the backup job.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- run class: `zabbix-postgresql-app-backup`;
- target alias: `zbx01`;
- dump format;
- retention class;
- timer/service status;
- first dump validation summary;
- Zabbix health summary;
- explicit non-claims.

Non-claims:

- no off-host copy;
- no full application restore proof;
- no Zabbix API credential custody;
- no host monitoring adoption;
- no change to PBS VM-level backup.

## Next Gate

After logical dumps are stable, perform a restore proof into an isolated target
or disposable database, then decide whether the dump should be copied off-host
with the broader backup strategy.
