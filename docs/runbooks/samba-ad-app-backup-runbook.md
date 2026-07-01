# Samba AD application backup runbook

This runbook documents the operator-owned application-aware backup gate for the
Samba AD DC and AD DNS state.

It complements VM-level PBS backup. It is not an active Tecrax backup connector
and does not add generic domain-controller automation.

## Scope

The backup pass covers:

- pre-backup Samba database consistency check;
- native Samba domain backup from the running DC;
- restricted local custody of the backup artifact;
- checksum generation;
- copy to an operator-approved off-VM backup target;
- public-safe sign-off.

It does not expose domain secrets, copy backup contents into Git, replace PBS
VM backup, prove all AD disaster-recovery cases, or automate long-term retention.

## Public and Private Boundary

Safe in public docs and sign-offs:

- backup class: Samba AD application backup;
- whether the pre-check passed;
- whether a backup artifact and checksum were created;
- whether the off-VM copy was verified by checksum;
- bounded caveats and non-claims.

Must remain outside Git and public sign-offs:

- backup archive names if they reveal the private domain;
- backup contents, hashes if the operator classifies them as sensitive;
- real storage endpoint, share name, credentials and mount options;
- raw command output containing topology, domain identity or account details;
- restore credentials, Kerberos material, machine secrets and keytabs.

## Procedure

1. Run a Samba database check before creating the backup.
2. Create a native Samba domain backup from the running DC using an
   operator-approved credential path.
3. Store the local artifact in a root-owned backup directory on the DC.
4. Restrict local permissions on the backup and checksum files.
5. Copy the backup and checksum to an approved off-VM backup target.
6. Verify the copied artifact on the target with a checksum check.
7. Record only public-safe evidence.

## Validation Evidence

The first application-aware backup pass completed with:

- Samba database pre-check successful;
- native Samba domain backup artifact created;
- local artifact permission restricted on the DC;
- checksum sidecar created;
- off-VM copy written to the approved external backup target;
- target-side checksum verification successful.

The external target presents permissions through its storage protocol rather
than POSIX mode bits. Treat custody as controlled by the target share, storage
account and operator-owned credentials, not by Unix file mode shown on the
mounted path.

## Caveats

The first online backup was created through a machine-account credential path.
Samba reported SYSVOL NTACL warnings during backup. The backup still produced a
domain backup artifact, but SYSVOL ACL fidelity must remain a known caveat until
a future domain-admin credential path or separate SYSVOL ACL proof is performed.

## Stop Conditions

Stop before sign-off if:

- database check fails;
- the backup command fails or produces no artifact;
- the artifact cannot be permission-restricted locally;
- the off-VM copy cannot be verified by checksum;
- evidence would require exposing domain secrets or backup contents.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- generic target alias;
- run class: `samba-ad-app-backup`;
- pre-check result;
- backup artifact created: yes/no;
- off-VM copy verified: yes/no;
- caveats, especially SYSVOL ACL fidelity;
- explicit non-claims.

Non-claims:

- no replacement for VM-level PBS backup;
- no full disaster-recovery claim;
- no claim that every future AD tombstone, client trust, multi-DC or SYSVOL
  failure mode is covered.
