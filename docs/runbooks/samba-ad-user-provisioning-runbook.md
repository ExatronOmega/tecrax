# Samba AD User Provisioning Runbook

This runbook covers bounded creation of ordinary Samba AD user accounts from an
operator-owned CSV file.

It does not store real people lists, credentials, private naming, private OU
layout or temporary passwords in Git.

## Scope

Allowed:

- create ordinary user accounts in a declared staff/user OU;
- set given name, surname and email;
- add users to existing groups;
- force password change at first logon.

Not allowed:

- create or store real user inventories in the repository;
- store temporary passwords in the repository;
- assign built-in privileged groups by default;
- change domain password policy;
- create service accounts or admin break-glass accounts.

## Preconditions

- Samba AD DC is deployed and healthy.
- The target OU exists.
- Target groups exist.
- The operator has an approved privileged path on the DC.
- The temporary password satisfies the current domain password policy.

## Operator-Owned CSV

Keep the CSV outside the repository, for example in a private operator working
directory.

Format:

```text
login,given_name,surname,email,groups
user01,Example,Person,user01@example.invalid,GG_ORG_Staff;GG_ORG_Department
```

Use ASCII logins, lowercase letters and no whitespace. For small organizations,
the recommended login shape is:

```text
first-initial + surname
```

Examples:

```text
jkowalski
anowak
```

## Dry-Run

Run the helper on the Samba AD DC or through an approved operator shell:

```bash
scripts/provision-samba-ad-users.sh \
  --csv /path/outside/repo/users.csv \
  --user-ou 'OU=Staff,OU=Users,OU=ORG'
```

Expected dry-run output:

```text
would_create_user:user01
would_add_member:GG_ORG_Staff:user01
```

## Apply

Use a temporary password only for first logon, and force user rotation at first
logon:

```bash
printf '%s\n' "$TEMP_PASSWORD" |
scripts/provision-samba-ad-users.sh \
  --apply \
  --csv /path/outside/repo/users.csv \
  --user-ou 'OU=Staff,OU=Users,OU=ORG' \
  --password-stdin
```

For an interactive operator shell, prefer:

```bash
scripts/provision-samba-ad-users.sh \
  --apply \
  --csv /path/outside/repo/users.csv \
  --user-ou 'OU=Staff,OU=Users,OU=ORG' \
  --prompt-password
```

## Validation

Validate:

- `samba-tool user list` contains expected logins;
- `samba-tool user show <login>` points at the target OU;
- `pwdLastSet` is `0`, meaning the password must be changed;
- group memberships match the CSV;
- a pilot endpoint can log in with one test account and force password change.

## Rollback

Before deleting anything, verify the account has not been used for production
data or ownership. For pilot mistakes, disable first:

```bash
samba-tool user disable user01
```

Delete only after explicit approval and after confirming there is no data
ownership or audit reason to keep the disabled object.
