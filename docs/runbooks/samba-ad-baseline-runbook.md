# Samba AD baseline runbook

This runbook covers the first operator-owned baseline after Samba AD DC
deployment.

It is not an active Tecrax profile intent and does not add an identity
management connector. It documents a bounded initial AD structure that can
scale to more users, servers and locations without moving production objects
immediately after adoption.

## Scope

The baseline pass covers:

- top-level organizational unit layout;
- minimal security groups;
- domain password and lockout policy;
- empty or low-impact baseline GPO placeholders;
- validation and public-safe sign-off;
- PBS backup after the baseline changes.

It does not join production computers, create real user accounts, migrate
existing accounts, configure DHCP, deploy AdGuard, apply aggressive Windows
hardening, or store any credentials in Tecrax.

## Baseline Structure

Approved OU shape:

```text
MBP
|-- Users
|   |-- Admins
|   |-- Staff
|   `-- Service
|-- Computers
|   |-- Workstations
|   `-- Servers
|-- Groups
`-- Disabled
```

Rationale:

- `Users/Admins` separates privileged people from normal staff.
- `Users/Staff` is the initial human-user landing zone.
- `Users/Service` is reserved for real future service accounts such as backup,
  monitoring or application integration accounts. Do not create service accounts
  without a separate purpose and owner.
- `Computers/Workstations` and `Computers/Servers` allow different GPOs later.
- `Groups` keeps operator-created security groups in one place.
- `Disabled` provides a quarantine area for disabled user and computer objects.

Do not create location-specific OUs until there are real location-specific GPOs
or delegation needs. Prefer AD Sites and subnets for physical location behavior.

## Baseline Groups

Approved minimal groups:

```text
GG_MBP_Admins
GG_MBP_IT_Operators
GG_MBP_Staff
GG_MBP_Servers
```

Group semantics:

- `GG_MBP_Admins`: narrow group for domain-level administrators. Membership is
  manual and must stay small.
- `GG_MBP_IT_Operators`: operators/helpdesk/technical users that should not be
  treated as Domain Admins by default.
- `GG_MBP_Staff`: normal staff membership and future policy targeting.
- `GG_MBP_Servers`: server objects or server-role targeting when needed.

Do not add broad membership in this baseline pass unless the operator explicitly
approves the target object list.

## Password Policy

Recommended domain policy:

```text
complexity: on
minimum password length: 12
password history: 24
minimum password age: 1 day
maximum password age: 90 days
lockout threshold: 5 attempts
lockout duration: 15 minutes
lockout observation window: 15 minutes
```

This is intentionally conservative for a small environment. Fine-grained
password policies can be introduced later if administrators, service accounts
or special cases need different controls.

## GPO Baseline

Create the following GPO placeholders:

```text
GPO_MBP_Baseline_Computer
GPO_MBP_Baseline_User
```

Initial state:

- link `GPO_MBP_Baseline_Computer` to the `Computers` OU;
- link `GPO_MBP_Baseline_User` to the `Users` OU;
- do not enforce either GPO;
- do not add aggressive settings until a test Windows client exists.

Future low-risk settings may include audit policy, screen lock, Windows Firewall
domain profile, UAC and legacy hash/NTLM restrictions. Apply them as a separate
change with a test workstation.

## Prerequisites

- Samba AD DC deployment is complete.
- Bootstrap Administrator password has been rotated by the operator.
- DC health checks pass: Samba service, AD DNS, Kerberos, NTP and database
  check.
- PBS backup for the DC exists.
- The operator accepts that object names are public-safe enough for runbooks and
  sign-offs.

## Procedure

1. Create missing OUs only. Existing OUs are left untouched.
2. Create missing groups only. Existing groups are left untouched.
3. Move baseline groups to the `Groups` OU when supported by the local tooling.
4. Set the domain password and lockout policy.
5. Create missing GPO placeholders only.
6. Link the Computer GPO to `Computers` and the User GPO to `Users`.
7. Validate object existence, GPO links, password policy, DC health and database
   consistency.
8. Run a PBS backup of the DC after the baseline.

## Stop Conditions

Stop if any of these are true:

- DC service, AD DNS, Kerberos or NTP health is degraded;
- the old bootstrap Administrator password still works;
- creating objects would require exposing real user passwords or private
  inventories;
- the baseline would require joining production clients;
- GPO tooling cannot create/link placeholders cleanly;
- PBS is unavailable and no alternate backup path is approved.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `samba-ad-baseline`;
- target alias: `samba-ad-dc-01`;
- OU baseline summary;
- group baseline summary;
- password policy summary;
- GPO placeholder and link summary;
- DC health validation summary;
- backup status;
- explicit non-claims.

Non-claims:

- no production client join;
- no real user migration;
- no service-account creation;
- no aggressive GPO hardening;
- no AD restore proof;
- no external disaster-recovery copy.

## Next Gate

After this baseline, either add the first test workstation to validate GPO
behavior or deploy AdGuard Home as the filtering/forwarding DNS layer according
to the approved DNS authority model.
