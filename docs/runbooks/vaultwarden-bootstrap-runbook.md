# Vaultwarden bootstrap runbook

This runbook covers the first Vaultwarden bootstrap for a Tecrax-managed
infrastructure stack.

Vaultwarden is introduced as a critical custody system for selected operational
secrets. This bootstrap does not make it a final production-trusted vault.

## Scope

The bootstrap covers:

- creating a dedicated Proxmox VM for Vaultwarden;
- placing the VM on the critical-light storage class;
- installing a minimal Debian OS;
- installing Vaultwarden through an operator-reviewed service model;
- keeping the bootstrap web endpoint restricted and HTTPS-only even before final
  PKI material is ready;
- adding monitoring and backup coverage;
- producing a public-safe sign-off.

It does not perform a full password migration, final HTTPS rollout, PKI
integration, organization-wide credential rotation, compliance readiness or
Proxmox root-of-trust hardening.

## Public and Private Boundary

Safe in public docs and sign-offs:

- service alias: `vault01`;
- deployment class and broad sizing;
- OS family;
- storage class;
- backup and restore-proof status;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- Vaultwarden admin token, user passwords, recovery codes and exports;
- database backups containing vault data;
- SSH key paths, fingerprints and private target catalog entries;
- real browser session cookies and invite links;
- private topology, firewall rules and raw service logs;
- offline break-glass material.

## Placement

Recommended public-safe shape:

- deployment class: Proxmox VM;
- service alias: `vault01`;
- OS family: Debian stable minimal;
- storage class: `rpool` / critical-light SSD mirror;
- initial disk: small critical-service class;
- CPU and memory: small always-on service, expandable after real usage;
- operator account follows the environment hard rule: `rexecop`.

Use a VM rather than a CT. Vaultwarden is a security-sensitive custody system,
and the VM boundary gives a cleaner operational model for backup, restore,
monitoring and later hardening.

## Bootstrap Security Model

Vaultwarden starts with status `bootstrap`, not `production trusted custody`.

The bootstrap may hold selected operational secrets needed for continued
deployment work. Do not migrate all passwords or recovery material until the
promotion gates are complete.

Required gates before `production trusted custody`:

- Vaultwarden backup and restore proof;
- offline break-glass recovery outside Vaultwarden;
- PKI restore proof after PKI Center exists;
- Proxmox root-of-trust hardening checkpoint;
- final HTTPS/PKI integration.

## Initial Network Model

Do not expose the web vault broadly over plain HTTP.

Preferred bootstrap pattern:

- bind the Vaultwarden backend only to the VM localhost interface;
- terminate temporary bootstrap TLS on a local-only reverse proxy;
- access the HTTPS endpoint through an operator SSH tunnel for first-account
  bootstrap;
- keep signups allowed only long enough to create the initial operator-owned
  account;
- disable signups after the first account is created.

The temporary bootstrap certificate may be self-signed or operator-issued, but
it must be treated as a bootstrap-only control. Replace it with PKI Center
material before final trusted custody.

## Procedure

### 1. Preflight

Validate before VM creation:

- selected VM ID and service address are unused;
- `rpool` has enough capacity;
- local DNS, NTP and AD DNS model are healthy;
- backup targets are available;
- operator has a plan for the first account, MFA and offline break-glass;
- no secret value needs to be pasted into Git, chat, roadmap or public sign-off.

### 2. Create VM

Create a dedicated VM with:

- static network configuration;
- QEMU guest agent;
- serial console;
- operator account;
- DNS following the infrastructure AD/DNS authority model;
- time synchronized to the local hierarchy.

Keep bootstrap credentials outside Git and public docs.

### 3. Install Vaultwarden

Install Vaultwarden through an operator-reviewed method. Container-based
deployment is acceptable when the service is pinned, documented and backed up.

For bootstrap:

- keep the service bound to localhost;
- require HTTPS for operator browser access, even if the certificate is only a
  temporary bootstrap certificate;
- keep persistent Vaultwarden data in a dedicated application directory;
- ensure data directory permissions are restrictive;
- do not print tokens, generated secrets or database contents;
- keep the admin interface disabled unless a separate operator decision enables
  it with a generated token held outside public docs.

### 4. First Account Bootstrap

Create the first operator-owned account through an SSH tunnel or another
operator-approved secure path.

Immediately after the first account exists:

- disable public signups;
- enable MFA for the account;
- record only a public-safe completion summary;
- store recovery material through the private custody model.

### 5. Monitoring

Add baseline monitoring:

- VM availability;
- guest agent;
- service process/container state;
- local web listener check from inside the VM;
- backup freshness after backup jobs exist.

Do not expose vault contents to monitoring systems.

### 6. Backup

Add local PBS VM backup coverage and include the VM in the external base-services
backup job if approved.

Before using Vaultwarden as a custody system for important secrets, perform an
isolated restore proof.

## Validation

Validate:

- VM runs;
- operator SSH works;
- QEMU guest agent responds;
- OS time and DNS are correct;
- Vaultwarden service is active;
- HTTPS listener is limited according to the bootstrap network model;
- plain HTTP is not exposed to the LAN;
- first account/MFA/signups state follows the operator-approved state;
- backup job exists and a first backup completed;
- no secret appears in public Tecrax docs or sign-offs.

## Stop Conditions

Stop before sign-off if any of these are true:

- service would be exposed broadly over HTTP;
- operator browser access would require plain HTTP instead of HTTPS;
- generated tokens, user passwords or recovery codes would be printed or
  committed;
- storage or backup target is not available;
- first-account bootstrap cannot be completed safely;
- MFA or signup restriction cannot be enforced;
- restore proof is skipped but the operator wants to migrate important secrets;
- deployment would require treating Vaultwarden as final trusted custody before
  the hardening gates.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `vaultwarden-bootstrap`;
- service alias and deployment class;
- OS family and broad sizing;
- network exposure model;
- HTTPS bootstrap model and certificate replacement requirement;
- monitoring summary;
- backup summary;
- first-account bootstrap status without credentials;
- explicit non-claims.

Non-claims:

- no final production-trusted custody;
- no full password migration;
- no final HTTPS/PKI integration;
- no Proxmox root-of-trust hardening claim;
- no one-command disaster recovery claim;
- no secret values in the sign-off.

## Tecrax Artifact Target

Current target: `L1` public-safe runbook.

Future candidates:

- `L3` read-only status checks for service/backup/restore-proof state;
- no L4 secret mutation or credential operation;
- no AI access to secret values or vault exports.

## Next Gate

After bootstrap, create the first backup and run an isolated restore proof before
storing important operational secrets in Vaultwarden.
