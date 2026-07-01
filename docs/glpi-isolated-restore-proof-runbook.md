# GLPI isolated restore proof runbook

This runbook covers the operator-owned restore proof for the GLPI VM.

It proves that a GLPI backup can be restored into an isolated temporary VM and
that the restored application reaches a bounded working state. It is not a
full disaster-recovery exercise and does not expose restored data or secrets.

## Scope

The restore proof covers:

- restore from an existing Proxmox backup object to a temporary VM;
- isolation from the production network before boot;
- guest-agent validation;
- local web validation inside the restored VM;
- database connectivity and schema presence validation;
- cleanup of the temporary VM after the proof.

It does not configure GLPI workflows, mail ingestion, LDAP/SSO, GLPI agents,
final HTTPS/TLS, compliance processes or a full infrastructure recovery.

## Public and Private Boundary

Safe in public docs and sign-offs:

- service alias: `glpi01`;
- restored service role: GLPI helpdesk/inventory VM;
- restore method class: isolated Proxmox VM restore;
- temporary target was destroyed after validation;
- bounded validation summary.

Must remain outside Git and public sign-offs:

- backup repository credentials;
- exact private backup task logs;
- GLPI credentials and database credentials;
- restored data contents;
- raw config files;
- private topology dumps.

## Prerequisites

- GLPI VM deployment is complete.
- A local PBS or operator-approved backup exists for the GLPI VM.
- The temporary restore target does not collide with a production VM/CT ID.
- The restored VM can be booted with production networking disabled.
- QEMU guest agent is available or an equivalent isolated validation path is
  operator-approved.

## Procedure

### 1. Select Restore Source

Select a current GLPI VM backup object from the approved backup storage.

Keep exact repository paths and credentials outside public documentation unless
the operator explicitly classifies them as safe.

### 2. Restore to Temporary Target

Restore the backup to a temporary VM ID, not over the production GLPI VM.

Immediately set the restored VM network link down or otherwise isolate it before
booting. The restored guest may contain the same static IP and hostname as
production, so network isolation is mandatory.

### 3. Boot and Validate

Start the temporary VM only after network isolation is confirmed.

Validate a bounded set of facts:

- QEMU guest agent responds;
- restored hostname is expected for the proof context;
- database service is active;
- web service is active;
- PHP runtime path is functional for GLPI;
- local HTTP request to the GLPI web root returns a successful response;
- GLPI database config exists;
- GLPI public directory exists;
- GLPI database connection succeeds;
- GLPI database has application tables.

Do not print database passwords, session cookies, restored records, uploaded
files or user data.

### 4. Cleanup

Stop and destroy the temporary VM after validation unless the operator
explicitly quarantines it for deeper analysis.

Confirm that the production GLPI VM remains running.

## Stop Conditions

Stop before sign-off if any of these are true:

- restore would overwrite the production GLPI VM;
- the temporary VM cannot be isolated from the production network;
- validation requires exposing restored records or credentials;
- cleanup cannot be completed;
- the production GLPI VM is affected by the proof.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- service alias;
- run class: `glpi-isolated-restore-proof`;
- restore method class;
- isolation state;
- bounded validation summary;
- cleanup status;
- explicit non-claims.

Non-claims:

- no full disaster-recovery readiness;
- no all-workload restore claim;
- no compliance readiness;
- no GLPI workflow, mail, LDAP/SSO or endpoint-agent rollout claim;
- no secret or restored-data exposure.

## Next Gate

After this proof, GLPI can be treated as having a first restore-tested baseline.
Final helpdesk/inventory durability still depends on workflow configuration,
operator account hygiene, future HTTPS/TLS hardening and periodic restore
testing.
