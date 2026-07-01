# Samba AD DC deployment runbook

This runbook covers the operator-owned deployment gate for the first Samba AD
DC and AD DNS authority in the Proxmox environment.

It is not an active Tecrax profile intent and does not add a generic Samba,
DNS, identity-management or VM-provisioning connector. It documents the bounded
sequence that must exist before any later Tecrax health checks or reactions can
claim domain/DNS readiness.

## Scope

The deployment pass covers:

- confirming immutable domain identity decisions before installation;
- creating a small VM for Samba AD DC on the SSD-backed critical-service pool;
- provisioning Samba as an AD DC with integrated DNS;
- validating time, Kerberos, LDAP and AD DNS service discovery;
- defining backup and restore handling for AD/DNS state;
- preserving the approved DNS authority model with AdGuard as filtering DNS.

It does not deploy AdGuard, migrate DHCP scopes, join production clients,
create all users/groups/GPOs, deploy a vault, expose domain secrets, or make
Tecrax a domain controller management plane.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic target alias, such as `samba-ad-dc-01`;
- target role: `ad_dns_authority`;
- deployment class: Proxmox VM;
- OS family and broad sizing class;
- authority model: AD DNS authoritative, filtering DNS separate;
- validation categories and explicit non-claims.

Must remain outside Git and public sign-offs:

- real AD DNS domain, realm and NetBIOS name until the operator explicitly
  approves disclosure;
- private addresses, host fingerprints, key paths and known-hosts paths;
- Administrator password, recovery material, Kerberos secrets, machine account
  passwords, keytabs and vault exports;
- full DHCP scopes, VLANs, static leases and production client inventory;
- raw Samba database dumps and full command output.

## Immutable Decisions

Stop before live deployment until the operator confirms:

- AD DNS domain;
- Kerberos realm;
- NetBIOS domain name;
- first DC hostname;
- first DC private address and gateway;
- DNS forwarder target for internet lookups;
- initial password handling method entered outside LLM/tooling;
- backup location and first restore-test approach.

These values are difficult or expensive to rename after clients, GPOs and
services depend on them. Do not infer them from examples or previous hostnames.

## Placement

Use a VM rather than a CT for the first domain controller. Samba AD DC owns
identity, Kerberos, DNS and time-sensitive service behavior; a VM gives cleaner
kernel, networking, restore and isolation boundaries.

Recommended public-safe shape:

- storage: SSD-backed critical-service pool;
- OS: current stable Debian;
- CPU and memory: small but not starved;
- disk: small system disk with headroom for logs and Samba state;
- start policy: automatic after Proxmox host boot;
- guest agent: enabled when available;
- root/operator access: environment hard rule account name `rexecop`.

Do not place bulky logs, unrelated tooling or application data on the DC. Keep
the DC narrow: identity and AD DNS authority only.

## Prerequisites

- Proxmox host readiness is complete.
- NTP/chrony is healthy on the Proxmox host and target VM.
- Local PBS is deployed and has passed at least one backup and restore proof on
  a low-risk workload.
- DNS authority checkpoint is approved:
  - AD clients use AD DNS;
  - AD DNS forwards non-local internet lookups to filtering DNS;
  - non-AD clients may use filtering DNS directly;
  - forwarding loops are forbidden.
- A public-safe sign-off location exists.
- The operator has a private place for domain identity, credentials and recovery
  notes outside the Tecrax repository.

## Deployment Procedure

### 1. Create the VM

Create a small Debian VM on the critical-service pool. Use deterministic VM
settings and record only public-safe sizing and role information in sign-off.

Before provisioning Samba, validate:

- boot works after a VM restart;
- network and resolver baseline are as expected;
- package state is clean;
- `rexecop` SSH and sudo access work;
- system time is synchronized.

### 2. Prepare host identity

Set the final DC hostname before Samba provisioning. Do not rename the machine
after provisioning unless following a separate AD DC migration procedure.

Ensure `/etc/hosts`, hostname, resolver configuration and time synchronization
are internally consistent for the future DC.

### 3. Provision Samba AD DC

Install Samba packages from the OS package source selected by the operator.
Provision the domain using the operator-approved private domain identity.

Password and recovery material must be entered manually by the operator or read
from an approved secret resolver that is outside LLM visibility.

After provisioning, configure the DC resolver to use itself for AD DNS service
records. Do not configure public DNS as a fallback resolver on the DC.

### 4. Configure forwarding

Configure AD DNS forwarding for non-local internet names according to the
approved DNS authority checkpoint. The intended downstream filtering resolver is
AdGuard after it exists; before AdGuard is deployed, use only the explicitly
approved temporary forwarder path and record it privately.

Do not create a forwarding loop between AD DNS and filtering DNS.

### 5. Validate AD DNS and identity services

Validate without exposing secrets:

- Samba service status is healthy;
- Kerberos can obtain a ticket for the administrative principal through
  operator-entered credentials;
- LDAP responds locally;
- AD DNS resolves the domain zone and service discovery SRV records;
- `_msdcs` records exist;
- non-local names forward through the approved path;
- time offset is acceptable for Kerberos;
- reboot preserves service health.

Do not paste tickets, hashes, keytabs, passwords, database contents or raw
directory dumps into public evidence.

### 6. Backup and restore handling

Before joining production clients, define and test at least the first backup
path:

- VM backup in PBS;
- Samba state/config backup method;
- restore target class for a test restore;
- explicit non-claim if only VM-level backup has been tested.

AD DC restore is identity-sensitive. A VM restore proof is useful, but it does
not automatically prove every future multi-DC, tombstone, SYSVOL or client-trust
failure mode.

### 7. Initial domain objects

Create only the minimum initial objects needed for the next gate:

- administrative group structure;
- one or more operator-managed admin accounts;
- baseline password policy;
- baseline DNS records needed for local validation.

Defer broad user migration, GPO rollout and workstation joins until backup,
DNS and rollback handling are signed off.

## Stop Conditions

Stop before or during deployment if any of these are true:

- domain, realm, NetBIOS name, hostname or private address are undecided;
- the operator would need to disclose passwords, hashes, keytabs or recovery
  material to LLM/tooling;
- NTP is unhealthy or time drift would break Kerberos assumptions;
- PBS is unavailable and no alternate backup path is approved;
- AD DNS would be bypassed by AD clients;
- AdGuard or public DNS would be configured as an AD client fallback without a
  deliberate failure-mode design;
- a forwarding rule can loop queries back to the same resolver class;
- provisioning requires replacing already active production identity without a
  migration plan.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- target alias: `samba-ad-dc-01`;
- run class: `samba-ad-dc-deployment`;
- deployment class: Proxmox VM;
- OS family and broad sizing class;
- domain identity confirmation status without revealing private values;
- NTP validation summary;
- AD DNS/SRV validation summary;
- Kerberos/LDAP validation summary;
- backup path status;
- explicit non-claims.

Non-claims:

- no AdGuard deployment;
- no DHCP migration;
- no production workstation migration;
- no complete GPO baseline unless separately signed off;
- no external disaster-recovery coverage until off-host copy exists and is
  tested;
- no secret custody in Tecrax.

## Next Gate

After this runbook is accepted, perform a live deployment only after the operator
confirms the immutable domain identity decisions. The next runbook after a
signed Samba AD DC deployment is AdGuard Home deployment as filtering/forwarding
DNS that respects AD DNS authority.
