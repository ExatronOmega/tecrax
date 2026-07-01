# Samba AD isolated restore proof runbook

This runbook documents the operator-owned isolated restore proof for the Samba
AD DC VM.

It proves that an existing DC VM backup can be restored into a temporary
isolated VM, booted without production network connectivity, validated locally
and removed. It does not replace application-aware AD backup or claim complete
domain disaster recovery.

## Scope

The restore proof covers:

- selecting an existing DC VM backup;
- restoring it to a temporary VM ID;
- preventing production network attachment before first boot;
- validating Samba AD DC and AD DNS locally through the guest agent;
- removing the temporary VM and disks after validation.

It does not:

- overwrite the production DC;
- join a restored DC to the live network;
- validate endpoint trust repair;
- validate every SYSVOL/GPO/ACL edge case;
- expose domain contents, credentials or raw directory data.

## Public and Private Boundary

Safe in public docs and sign-offs:

- backup source class: existing VM backup;
- temporary restore target class;
- isolation control: network link down before boot;
- bounded service status and DNS service-discovery checks;
- cleanup result.

Must remain outside Git and public sign-offs:

- exact backup object path if it reveals private topology;
- VM IDs if the operator classifies them as private;
- restored directory contents;
- account lists, hashes, keytabs, tickets and credentials;
- full command output with private names or addresses.

## Procedure

1. Select an approved DC VM backup object.
2. Restore it to a temporary VM ID, never over the production DC.
3. Before starting the VM:
   - assign a restore-proof name;
   - disable automatic boot;
   - ensure the network link is down;
   - preserve a clear restore-proof tag.
4. Start the temporary VM.
5. Use the QEMU guest agent, not production SSH/network access, for validation.
6. Validate:
   - the restored OS boots;
   - Samba AD DC service is active;
   - Samba database check passes;
   - local AD DNS answers LDAP and Kerberos SRV records;
   - the DC host record resolves locally;
   - the restored network interface remains disconnected.
7. Shut down and destroy the temporary VM and unreferenced disks.
8. Confirm the temporary VM configuration and disks are gone.

## Validation Evidence

The first isolated restore proof completed with:

- restore from an existing DC VM backup to a temporary VM;
- network link disabled before boot;
- restored VM booted successfully;
- guest agent validation path worked without production network access;
- Samba AD DC active;
- Samba database check passed;
- local AD DNS answered LDAP and Kerberos SRV records;
- restored interface remained `DOWN` / `NO-CARRIER`;
- temporary VM and restore disks removed after validation.

## Stop Conditions

Stop before sign-off if:

- the temporary VM would boot with production network connectivity;
- guest-agent validation is unavailable and no approved isolated console path
  exists;
- Samba AD DC does not start;
- database check fails;
- local AD DNS service-discovery records do not resolve;
- temporary restore artifacts cannot be removed.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- generic target alias;
- run class: `samba-ad-isolated-restore-proof`;
- backup source class;
- isolation control summary;
- bounded validation result;
- cleanup result;
- explicit non-claims.

Non-claims:

- no full disaster-recovery automation;
- no endpoint trust or client rejoin proof;
- no multi-DC restore proof;
- no SYSVOL ACL fidelity claim beyond what the tested restore path validates.
