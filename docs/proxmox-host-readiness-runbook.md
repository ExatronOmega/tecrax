# Proxmox host readiness runbook

This runbook covers the first operator-owned readiness pass for a freshly
installed Proxmox VE host before VM/CT services are deployed.

It is not an active Tecrax profile intent. It is a manual/operator-owned
procedure used to establish a safe baseline for later bounded Tecrax operations.

## Scope

The readiness pass covers:

- package repository posture and host update;
- reboot decision after updates;
- disk health review;
- ZFS pool health and basic properties;
- dataset layout for the data pool;
- Proxmox storage registration;
- public-safe sign-off.

It does not create VM/CT workloads, configure Samba, AdGuard, PBS, Zabbix,
Grafana, Wazuh, Vaultwarden or generic deployment automation.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic target alias, such as `proxmox-node-01`;
- generic pool role names, such as system pool and data pool;
- property names, command classes and expected states;
- aggregate status: pass, fail, blocked, reboot-required.

Must remain outside Git and public sign-offs:

- real addresses and private hostnames;
- SSH keys, known-hosts files and fingerprints;
- full disk serial inventory if it identifies the private asset;
- raw `smartctl`, `zpool`, `apt` or Proxmox outputs;
- local paths to private environment, wrapper or inventory files;
- operation ids from private runtime storage.

## Prerequisites

- Access handoff in `docs/proxmox-access-handoff.md` is complete.
- Operator access uses the `rexecop` account where automation is involved.
- Emergency console or Web UI access exists before any update or reboot.
- The operator has confirmed the host is the intended freshly installed Proxmox
  node.
- The operator has chosen the privilege path for this manual run:
  - trusted root console/tmux/Web UI session; or
  - a temporary operator-controlled shell;
  - not broad unattended sudo for `rexecop`.
- Current storage intent is known:
  - system pool on SSD mirror;
  - data pool on HDD mirror;
  - no hardware RAID and no Dell S150 / BIOS RAID.

## Stop Conditions

Stop before mutation if any of these are true:

- strict host identity is not verified;
- either ZFS pool is not online;
- disk health has unreviewed critical errors;
- package repositories include unintended enterprise sources;
- a reboot would interrupt an unknown workload;
- the operator cannot access the host out-of-band.

## Procedure

### 1. Preflight

Inspect host identity, uptime, kernel, repository posture and pool state before
changing anything.

Public sign-off should retain only status summaries, not raw command output.

Expected checks:

- host is the intended Proxmox node;
- no unexpected workloads are running;
- package repositories match the no-subscription decision;
- system and data pools are online;
- chrony/NTP baseline is known.

### 2. Package Update

Update package indexes and apply pending Proxmox/Debian updates through the
operator-controlled shell or Web UI.

If the update indicates a required reboot, record `reboot_required=true` in the
private notes and perform the reboot only after console/Web UI access is
confirmed.

Do not create VM/CT workloads before this update/reboot decision is resolved.

### 3. Disk Health

Review SMART health for all internal disks.

If `smartctl` is unavailable, install the minimal SMART tooling before
continuing. Treat tooling installation as part of the package update phase, not
as a Tecrax connector capability.

The public sign-off may record:

- disk count reviewed;
- health summary per role: system mirror, data mirror;
- whether any disk requires follow-up.

It must not include full serial dumps, raw SMART output or device paths that are
treated as private topology.

### 4. ZFS Pool Health and Properties

Confirm both pools are online and have no known data errors.

Review or set only baseline properties that are already part of the operator
plan:

- `compression=lz4` where appropriate;
- `atime=off` where appropriate;
- `autotrim=on` for the SSD-backed system pool if confirmed suitable for the
  hardware and Proxmox version.

Do not change ashift, vdev layout, encryption, deduplication or pool topology in
this runbook.

### 5. Data Pool Dataset Layout

Create a logical dataset layout on the data pool before service deployment.

Recommended public-safe role names:

- `vmdata`;
- `backups`;
- `iso`;
- `templates`;
- `exports`;
- `logs`;
- `retention`;
- `admin-tools`;
- `docs`.

Exact dataset names may differ in the private implementation. Public docs should
describe roles, not private mount paths.

### 6. Proxmox Storage Registration

Register the intended storage entries in the Proxmox UI or operator-owned
configuration.

Minimum expected storage roles:

- VM/CT disk storage on the data pool;
- ISO/template storage;
- backup/export storage;
- admin-tools/documentation storage if managed by Proxmox.

Do not mark PBS, Samba, AdGuard, Zabbix, Grafana or Wazuh as deployed merely
because storage roles exist.

## Validation

A readiness pass is complete when:

- package update is complete or blocked with a documented reason;
- reboot state is resolved;
- disk health was reviewed;
- system and data pools are online;
- baseline ZFS properties were reviewed or applied;
- data pool storage roles exist;
- no service deployment has started prematurely;
- public-safe sign-off is written.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- Tecrax repository HEAD;
- generic target alias;
- run class: `operator-verified`;
- package update status;
- reboot status;
- disk health aggregate status;
- pool health aggregate status;
- ZFS property status;
- storage role status;
- explicit non-claims;
- secret/private-topology scan result.

Non-claims:

- no VM/CT workload deployment;
- no Samba/AdGuard/PBS/Zabbix/Grafana/Wazuh deployment;
- no backup health claim;
- no restore evidence claim unless a restore test was actually performed;
- no generic Proxmox mutation capability in Tecrax.

## Next Gate

After this runbook passes, continue with one of:

- `docs/chrony-ntp-server-mutation-runbook.md` for the governed NTP slice;
- a private `admin-tools` substrate runbook outside this public package;
- a PBS readiness runbook before critical service deployment.
