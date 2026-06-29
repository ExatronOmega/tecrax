# Proxmox Backup Server post-deploy hardening runbook

This runbook covers the first hardening pass after PBS is deployed as a local
operational backup VM.

It is not an active Tecrax profile intent and does not add a backup connector.
It is an operator-owned procedure for closing bootstrap gaps before backup jobs
or restore proof are treated as meaningful operational evidence.

## Scope

The hardening pass covers:

- temporary bootstrap credential rotation;
- operator access validation;
- package and repository sanity checks;
- service health checks;
- locale and package-configuration cleanup if the installer left them pending;
- reboot validation after hardening;
- public-safe hardening sign-off.

It does not create backup jobs, prove restore, configure external replication,
store secrets, or activate a Tecrax backup-status intent.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic target alias and role;
- whether credential rotation was operator-confirmed;
- bounded service status;
- package/repository status summarized without URLs that reveal topology;
- reboot proof summary;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- passwords, password hashes, recovery codes and API tokens;
- private addresses, host fingerprints and key paths;
- raw package logs, SSH logs and full service output;
- exact command transcripts containing topology;
- private backup repository or datastore capacity details.

## Prerequisites

- PBS deployment sign-off exists.
- Break-glass console access exists.
- `rexecop` SSH and sudo are working.
- PBS services and datastore were verified at deployment time.

## Procedure

### 1. Rotate bootstrap credential

The operator rotates any temporary bootstrap root credential manually, outside
LLM/tooling. Do not paste the old or new password into chat, files, shell logs or
public sign-offs.

The public sign-off may record only:

- rotation confirmed by operator;
- rotation deferred with a clear risk acceptance;
- rotation blocked with a non-secret blocker.

### 2. Validate operator access

Confirm:

- key-based SSH as `rexecop`;
- passwordless sudo for `rexecop`;
- root console access remains available as break-glass only;
- no private key material or known-hosts details are copied into Git.

### 3. Validate repositories and package state

Confirm:

- enterprise repositories are disabled if no subscription exists;
- no-subscription repository is configured for PBS;
- `dpkg --audit` reports no pending package configuration;
- package update check is clean or pending updates are explicitly recorded;
- no interactive debconf prompt is left unresolved.

Do not claim a full upgrade unless it actually completed and reboot validation
was repeated afterwards.

### 4. Validate services

Confirm:

- `ssh` is active;
- QEMU guest agent is active and reachable from Proxmox;
- `proxmox-backup` is active;
- `proxmox-backup-proxy` is active;
- PBS web/API listener is active;
- datastore remains mounted and listed through PBS tooling.

### 5. Reboot proof

Reboot the PBS VM after hardening if any package, boot, repository, service or
credential state changed.

After reboot, validate:

- boot completes without manual intervention;
- SSH as `rexecop` works;
- sudo works;
- guest agent works;
- PBS services are active;
- datastore is mounted and listed.

## Stop Conditions

Stop before sign-off if any of these are true:

- temporary bootstrap credential still exists without explicit risk acceptance;
- `rexecop` SSH or sudo fails;
- package manager state is interrupted;
- PBS service status is unknown;
- datastore is not mounted or not listed;
- reboot proof was skipped after a material change;
- evidence would require exposing secrets or private topology.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- generic target alias;
- run class: `pbs-post-deploy-hardening`;
- credential-rotation status without secret values;
- operator access summary;
- repository/package summary;
- service status summary;
- reboot proof summary;
- explicit non-claims.

Non-claims:

- no backup coverage until a backup job completes;
- no restore readiness until restore proof passes;
- no off-host protection until an external copy target exists and is tested.

## Next Gate

After hardening, define retention and create the first backup job. Do not proceed
to critical service deployment on the assumption that PBS is protective until a
backup job and restore proof exist.
