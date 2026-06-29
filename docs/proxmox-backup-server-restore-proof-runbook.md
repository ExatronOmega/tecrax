# Proxmox Backup Server restore proof runbook

This runbook covers the first restore proof after a PBS backup job succeeds.

It is not an active Tecrax profile intent and does not add a backup connector.
It is an operator-owned procedure for proving that at least one backup can be
restored and validated.

## Scope

The restore proof covers one of:

- disposable VM/CT restore;
- file-level restore of non-sensitive test content;
- operator-approved equivalent restore test.

It does not prove every workload is restorable, satisfy disaster recovery,
validate off-host copies, or certify long-term retention.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic restored workload role;
- restore method class;
- bounded validation outcome;
- time window summary if non-sensitive;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- restored guest contents and file names;
- exact backup paths, namespaces and VM/CT ids if private;
- raw restore logs;
- private addresses, fingerprints and credentials;
- screenshots containing topology or data.

## Prerequisites

- PBS deployment sign-off exists.
- First backup job sign-off exists or the job success is operator-confirmed.
- Restore target is disposable or isolated.
- Operator has rollback/removal plan for restored VM/CT or files.

## Procedure

### 1. Select restore method

Prefer disposable VM/CT restore when proving infrastructure recovery. Use
file-level restore only when VM/CT restore is not yet possible or when the first
backup target is intentionally minimal.

The restored object must not overwrite a production object unless a separate
operator-approved recovery plan exists.

### 2. Execute restore

Run restore through Proxmox/PBS tooling. Keep full task output and exact backup
path private unless explicitly classified as safe.

If restoring a VM/CT:

- restore to a new disposable target;
- keep networking isolated or safe by default;
- avoid conflicts with production identity, MAC, hostname or IP.

If restoring files:

- restore non-sensitive test content;
- verify integrity without exposing contents publicly.

### 3. Validate restored object

A restore proof passes only when at least one bounded validation succeeds:

- restored VM/CT boots to expected basic state;
- restored service starts in isolated test context;
- restored file checksum matches an operator-owned expected value;
- equivalent operator-defined validation passes.

### 4. Cleanup or quarantine

After proof:

- remove disposable restore artifacts, or;
- quarantine them with a clear owner and expiration;
- avoid leaving duplicate services on production networks.

## Stop Conditions

Stop before sign-off if any of these are true:

- restore would overwrite production state;
- restored VM/CT would conflict on identity or network;
- validation requires exposing guest data;
- backup job success is not established;
- cleanup/quarantine plan is missing.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- generic PBS target alias;
- generic restored workload role;
- run class: `pbs-restore-proof`;
- restore method class;
- validation result summary;
- cleanup/quarantine status;
- explicit non-claims.

Non-claims:

- no all-workload restore readiness;
- no off-host disaster recovery;
- no guarantee that critical services are protected until they have their own
  jobs and restore tests;
- no exposure of restored data.

## Next Gate

After restore proof, choose the external/off-host backup copy path before
treating critical services as resilient.
