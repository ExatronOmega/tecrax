# Proxmox Backup Server full OS upgrade runbook

This runbook documents the operator-owned full OS upgrade retry for the PBS VM.

It is not an active Tecrax package-management operation. It records the bounded
maintenance path used after repository/download integrity stabilized.

## Scope

The upgrade pass covers:

- checking PBS service state before maintenance;
- running full package upgrade through the approved no-subscription repository;
- retrying a repository hash mismatch only after clearing the affected archive;
- rebooting after kernel/ZFS updates;
- validating PBS service and UI after reboot;
- repairing a PBS VM bootloader quirk where needed.

It does not automate arbitrary fleet patching, bypass package integrity checks,
or claim a long-term patch-management policy.

## Public and Private Boundary

Safe in public docs and sign-offs:

- package upgrade class and final package state;
- whether integrity checks passed after retry;
- kernel version after reboot;
- PBS services and UI status;
- bootloader caveat summary.

Must remain outside Git and public sign-offs:

- private host addresses, SSH key paths and fingerprints;
- raw package logs if they expose topology;
- repository credentials if ever used;
- backup namespaces, datastore internals and task logs with private identifiers.

## Procedure

1. Confirm no important PBS task is running.
2. Confirm PBS services are active before maintenance.
3. Run package index update.
4. Run full upgrade non-interactively, preserving existing local config unless
   the operator approves a config replacement.
5. If apt reports `Hash Sum mismatch`, do not force installation. Remove the
   affected cached archive, refresh package metadata with no-cache options and
   retry the affected package download.
6. Re-run the full upgrade after the affected package downloads cleanly.
7. Reboot the PBS VM after kernel or ZFS updates.
8. Validate:
   - active kernel version;
   - PBS package version;
   - `proxmox-backup-proxy`, `proxmox-backup` and SSH services;
   - PBS web UI response;
   - no remaining upgradable packages;
   - clean `dpkg --audit`.

## PBS VM Bootloader Quirk

The first upgrade installed a newer kernel but the VM kept booting the old
kernel. Investigation showed that this PBS VM boots from a small EFI partition
with a minimal GRUB configuration and copied kernel/initrd files. The normal
root filesystem GRUB config was updated, but the EFI partition still pointed to
the old copied kernel.

The corrective action was:

- generate the missing initramfs with the real initramfs tool behind the Proxmox
  diversion;
- regenerate the root GRUB config;
- mount the EFI partition;
- copy the new kernel and initrd to the EFI partition;
- update the EFI partition's minimal GRUB config with the new kernel as default
  and the old kernel as fallback;
- reboot and verify the active kernel.

Document this quirk before future PBS kernel upgrades.

## Validation Evidence

The full OS upgrade retry completed with:

- repository hash mismatch handled by clean re-download of the affected package;
- full upgrade completed with exit code 0;
- PBS rebooted successfully;
- active kernel moved to the upgraded kernel line;
- PBS services active after reboot;
- PBS web UI returned a successful response;
- apt reported no remaining upgradable packages;
- no `dpkg --audit` issues reported.

## Stop Conditions

Stop before sign-off if:

- package integrity checks fail repeatedly;
- apt/dpkg is left in an interrupted state;
- the VM does not boot after upgrade;
- PBS services fail after reboot;
- the active kernel does not match the expected upgraded kernel and bootloader
  repair is not approved or not understood;
- evidence would require exposing secrets or private backup metadata.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- generic target alias;
- run class: `pbs-full-os-upgrade`;
- package upgrade result;
- integrity retry result, if any;
- active kernel after reboot;
- PBS service/UI status;
- bootloader caveat and remediation summary;
- explicit non-claims.

Non-claims:

- no generic fleet patching automation;
- no external PBS datastore sync/export claim;
- no future upgrade guarantee without repeating validation.
