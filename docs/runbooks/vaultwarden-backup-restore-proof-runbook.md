# Vaultwarden backup and restore-proof runbook

This runbook covers the first public-safe backup and isolated restore proof for
the Tecrax-managed Vaultwarden bootstrap VM.

Vaultwarden remains in `bootstrap` status until restore proof, offline
break-glass, PKI restore proof and Proxmox root-of-trust hardening gates are
complete. A successful restore proof validates mechanics only; it does not
authorize full password migration by itself.

## Scope

The proof covers:

- VM-level backup coverage for the Vaultwarden VM;
- application data custody boundaries;
- an isolated restore target;
- bounded service validation without reading vault contents;
- cleanup of temporary restore infrastructure;
- a public-safe sign-off.

It does not expose, export, inspect, migrate or rotate real vault secrets.

## Public and Private Boundary

Safe in public docs and sign-offs:

- service alias and VM class;
- backup job existence;
- restore proof date and outcome;
- isolated target class;
- non-secret health checks;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- Vaultwarden database contents and attachments;
- admin token, user passwords, MFA recovery codes and emergency sheets;
- backup encryption keys and repository credentials;
- restored private files, config values and raw logs;
- temporary restore host addresses if they reveal private topology;
- operator browser sessions and invite links.

## Preconditions

Before running the proof:

- Vaultwarden bootstrap VM exists and is backed up;
- the service is not broadly exposed over plain HTTP;
- the operator has confirmed whether the current backup may contain sensitive
  material;
- restore target ID, network and storage are temporary and isolated;
- no user-facing production endpoint depends on the restore target;
- the operator has a cleanup plan for the temporary target.

## Backup Model

Minimum bootstrap model:

- VM-level backup for crash-consistent recovery;
- application directory included in the VM backup;
- backup job coverage recorded in private operator context;
- off-host copy strategy reviewed before important secrets are stored.

If application-level exports are added later, treat them as sensitive custody
artifacts. Do not place them in Tecrax, public sign-offs or chat output.

The first application-level backup and offline break-glass baseline is tracked
separately in `vaultwarden-app-backup-break-glass-runbook.md`. It uses a
root-owned Vaultwarden data archive with SQLite backup mechanics, not a user
vault export.

## Restore-Proof Procedure

### 1. Select Backup

Choose a recent backup snapshot and record only public-safe metadata:

- source service alias;
- backup class;
- approximate backup date;
- repository class.

Do not print repository secrets, encryption material or internal backup paths.

### 2. Restore Isolated Target

Restore to a temporary VM ID or equivalent isolated target.

The target must:

- not reuse the production service address;
- not register as the production service in DNS;
- not expose Vaultwarden to users;
- not send mail, invitations or external notifications;
- not become part of normal monitoring or backup schedules.

### 3. Validate Without Reading Secrets

Validate only bounded health:

- guest agent or OS responds;
- filesystem mounts are present;
- Vaultwarden service starts or can be inspected locally;
- localhost listener matches expected bootstrap exposure;
- database file exists and is readable by the service user;
- logs show no immediate startup failure.

Do not log in to restored user vaults, dump database rows, export vault data or
inspect credential values.

### 4. Cleanup

After validation:

- power off the temporary target;
- remove temporary restore artifacts according to operator-approved cleanup;
- confirm production VM is unchanged;
- record public-safe result.

Deletion-class cleanup on unrelated storage is outside this runbook and requires
its own operator confirmation.

## Validation

The proof passes only if:

- restore completed to an isolated target;
- bounded service health checks passed;
- no secret material was printed, committed or copied into public docs;
- production Vaultwarden remained unchanged;
- cleanup completed or an explicit retained-temporary-target decision was
  recorded;
- sign-off states the remaining gates before final trusted custody.

## Stop Conditions

Stop before sign-off if:

- the restored target would become reachable by users;
- backup material cannot be identified safely;
- validation would require reading vault contents;
- cleanup would risk deleting production data;
- backup contains important secrets and no off-host/offline custody decision
  exists;
- the operator expects this proof to imply final production trust by itself.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `vaultwarden-restore-proof`;
- source alias;
- isolated target class;
- backup class;
- bounded checks performed;
- cleanup status;
- explicit non-claims.

Non-claims:

- no vault content inspection;
- no full password migration approval;
- no PKI restore proof;
- no Proxmox root-of-trust hardening claim;
- no one-command disaster recovery claim;
- no secret values in sign-off.

## Tecrax Artifact Target

Current target: `L1` public-safe runbook.

Future candidates:

- `L3` read-only restore-proof status summary;
- `L3` backup freshness summary;
- no automation that reads or exports vault secret values.
