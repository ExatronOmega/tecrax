# Samba AD User Password Reset Runbook

This runbook covers an operator-owned password reset for an existing ordinary
Samba AD user account.

It is intended for cases where a user forgot their current password, but the
account itself is otherwise valid. It is not a bulk provisioning flow, a
password vault workflow or a generic privileged account recovery procedure.

## Scope

Allowed:

- verify the target user exists and is in the expected user OU;
- reset the password interactively on the Samba AD DC;
- force password change at next logon;
- validate the account metadata after reset;
- validate logon and password rotation on the endpoint when the user is present;
- record a public-safe sign-off.

Not allowed:

- paste passwords into chat, Git, shell scripts, command arguments or docs;
- use `--newpassword` in an operator transcript for a real user;
- reset multiple users as a side effect;
- change domain password policy;
- bypass normal user identity checks;
- store the temporary or final password in Tecrax, RExecOp, GovEngine, SCLite or
  public notes;
- automate password reset as a Tecrax mutation at this stage.

## Public and Private Boundary

Safe in public docs and sign-offs:

- target account alias or role, if non-sensitive;
- reset class: ordinary user password reset;
- `must-change-at-next-login` status;
- endpoint validation status;
- non-claims.

Must remain outside Git and public sign-offs:

- temporary passwords and final passwords;
- password hints;
- full user inventories;
- raw account dumps if they expose private directory structure;
- screenshots of user sessions;
- Domain Admin or delegated operator credentials.

## Preconditions

- Samba AD DC is healthy.
- The target user account already exists.
- The operator has an approved privileged path on the DC.
- The operator has verified the user identity through an out-of-band process.
- The new temporary password satisfies the current domain password policy.
- If endpoint validation is part of the same workcycle, the user or operator has
  console/RDP access to the pilot workstation.

## Procedure

### 1. Inspect Target Account

Before changing anything, inspect the bounded account state:

```bash
sudo samba-tool user show user01
```

Check only the facts needed for the reset:

- `sAMAccountName`;
- expected OU;
- account is enabled;
- current lockout/bad-password counters if relevant;
- no obvious mismatch between requested user and account.

Do not copy full account dumps into public docs.

### 2. Reset Password Interactively

Run from an approved operator shell on the DC:

```bash
sudo samba-tool user setpassword user01 --must-change-at-next-login
```

Do not pass the real password through `--newpassword`. Let `samba-tool` prompt
for the new temporary password interactively.

Expected behavior:

- the operator enters the temporary password twice;
- the command completes successfully;
- the user must change the password at next logon.

### 3. Validate Account Metadata

After reset, inspect a bounded subset:

```bash
sudo samba-tool user show user01
```

Expected facts:

- account still points to the expected user;
- `pwdLastSet` reflects must-change-at-next-login behavior;
- `whenChanged` advanced;
- account is not unexpectedly disabled or moved.

The exact representation of forced password change can differ between Samba
versions and tools. Validate with both account metadata and the endpoint logon
behavior when possible.

### 4. Endpoint Validation

On the pilot workstation:

1. Log in as the domain user with the temporary password.
2. Confirm Windows forces password change.
3. Set a new password known only to the user/operator.
4. Confirm the user reaches the desktop.
5. Run a minimal domain sanity check:

```powershell
whoami
nltest /dsgetdc:<domain.example.invalid>
gpupdate /force
```

If the endpoint is unavailable, record endpoint validation as deferred rather
than claiming completion.

## Stop Conditions

Stop before or during the reset if:

- the requested user identity is ambiguous;
- the operator would need to expose the password to LLM/tooling;
- the account is privileged and needs a separate break-glass procedure;
- the account appears disabled, stale or mapped to a different person;
- domain policy rejects the temporary password and the cause is unclear;
- endpoint validation would interrupt production work.

## Rollback

Password reset itself is not meaningfully rolled back by recovering the old
password. If the reset was wrong:

- immediately notify the operator;
- reset again to a fresh temporary password only after verifying identity;
- force password change at next logon;
- review `badPwdCount`, lockout state and recent logon attempts;
- disable the account only if there is a security concern and the operator
  explicitly approves.

Do not delete the user object as rollback.

## Evidence and Sign-Off

Public-safe sign-off may include:

- run class: `samba-ad-user-password-reset`;
- target account alias;
- password reset command class: interactive;
- must-change-at-next-login: yes/no;
- endpoint validation: done/deferred/failed;
- non-claims.

Do not include:

- temporary password;
- final password;
- raw `samba-tool user show` output with private fields;
- screenshots or transcripts containing user secrets.

## Tecrax Artifact Decision

Current activation level: `L1 - public-safe runbook`.

A helper is not added for the first real reset. A future L2 helper may be
reasonable only if it stays custody-safe:

- fixed command shape;
- no password argument support for real users;
- interactive TTY prompt only;
- target username allowlist or explicit operator confirmation;
- bounded pre/post account summaries;
- no generic shell passthrough.

Do not promote this directly to a bounded Tecrax mutation until the custody
model, authorization policy, evidence shape and rollback/incident process are
settled.
