# Admin-tools CT deployment runbook

This runbook covers the first admin-tools workload as a lightweight Proxmox LXC
container.

It is not an active Tecrax profile intent and does not add a generic shell
runner. It is an operator-owned deployment procedure used to create the first
low-risk workload for PBS backup and restore proof.

## Scope

The deployment pass covers:

- creating a lightweight Linux CT for admin-tools;
- creating the `rexecop` operator account;
- validating SSH and passwordless sudo;
- keeping secrets and private topology outside Git;
- making the CT eligible for the first PBS backup job;
- public-safe deployment sign-off.

It does not install Samba, AdGuard, Zabbix, Grafana, Wazuh, Vaultwarden, a CMDB,
or a permanent secret store. It does not mount broad host paths or move private
keys into the CT.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic target alias, such as `admin-tools-01`;
- target role: `admin_tools`;
- deployment class: Proxmox CT;
- OS family and broad sizing class;
- bounded access and service status;
- backup eligibility status;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- real addresses, host fingerprints, key paths and known-hosts paths;
- exact VM/CT ids if they identify private topology;
- passwords, tokens, private keys and vault exports;
- raw package logs and full command output;
- private inventory, DNS zone details and private network reservations.

## Prerequisites

- Proxmox host readiness is complete.
- PBS deployment and post-deploy hardening are complete.
- A non-conflicting private address is selected outside public docs.
- Any reserved future service address is preserved by the operator.
- Operator account naming follows the environment hard rule: use `rexecop`.

## Deployment Procedure

### 1. Select CT placement

Use the data pool for the CT root filesystem. Keep sizing conservative:

- one or two CPU cores;
- one or two GiB memory;
- small root filesystem;
- unprivileged CT unless a specific package requires otherwise.

Do not mount broad host paths during initial deployment. Add bind mounts later
only after a separate boundary decision.

### 2. Install from a standard template

Use a current Debian or Ubuntu standard template from the Proxmox template
repository. Verify the template was downloaded through Proxmox tooling.

The exact template filename is public-safe only if it does not reveal local
topology.

### 3. Create operator access

Inside the CT:

- create `rexecop`;
- install SSH server and sudo if not already present;
- install the approved operator public key;
- configure passwordless sudo for `rexecop`;
- leave root password-based access disabled or break-glass only according to
  operator policy.

Do not copy private keys or secrets into the CT.

### 4. Baseline packages

Install only minimal admin packages needed for the next gate. Examples:

- SSH server;
- sudo;
- ca-certificates;
- curl or equivalent fetch/debug tooling;
- basic text/process/network diagnostics.

Defer Ansible, inventories and private documentation until backup and restore
proof exist.

### 5. Validate

Validate:

- CT starts automatically or has an explicit start policy;
- network is reachable through the operator-approved path;
- SSH as `rexecop` works;
- passwordless sudo works;
- package state is clean;
- the CT is visible to Proxmox backup tooling.

### 6. Backup eligibility

The CT is eligible for the first PBS backup job when:

- it has no critical secrets;
- it has a bounded root filesystem;
- operator access works;
- package state is clean;
- public-safe sign-off can omit topology.

## Stop Conditions

Stop before sign-off if any of these are true:

- selected address conflicts with a reserved service address;
- CT requires privileged mode without a separate decision;
- SSH or sudo for `rexecop` fails;
- package state is interrupted;
- private keys or secrets would need to be copied into the CT;
- host bind mounts are needed before backup policy is defined.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- target alias: `admin-tools-01`;
- run class: `admin-tools-ct-deployment`;
- deployment class: Proxmox CT;
- OS family and broad sizing class;
- access validation summary;
- backup eligibility status;
- explicit non-claims.

Non-claims:

- no restore readiness until PBS restore proof passes;
- no external disaster recovery until off-host copy exists and is tested;
- no CMDB, vault, monitoring or automation controller activation;
- no secret custody inside the CT.

## Next Gate

After deployment, create the first PBS backup job for the admin-tools CT and
perform restore proof to a disposable restored CT.
