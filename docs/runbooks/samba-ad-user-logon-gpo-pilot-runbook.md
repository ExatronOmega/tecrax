# Samba AD User Logon and GPO Pilot Runbook

This runbook covers the first real domain-user logon on a pilot Windows
workstation after Samba AD user provisioning and endpoint domain join.

It is an operator-owned pilot step. It does not create users, join workstations,
deploy endpoint agents, redesign GPOs or automate user migration.

## Scope

Allowed:

- verify that a provisioned domain user can log in on one pilot workstation;
- confirm first-logon password rotation;
- confirm domain DNS and domain time behavior after user logon;
- run a low-impact GPO refresh and report check;
- test cached logon behavior in a controlled way;
- record a public-safe sign-off.

Not allowed:

- broad user rollout;
- aggressive GPO hardening;
- endpoint Zabbix or Wazuh agent rollout;
- Folder Redirection or NAS data migration;
- DHCP/DNS option changes on the security gateway;
- storing real user passwords, domain credentials or full endpoint inventory in
  Git.

## Preconditions

- Samba AD DC is healthy.
- The pilot workstation is joined to the domain.
- The pilot workstation uses AD DNS.
- Windows Time uses the domain hierarchy after join.
- A provisioned ordinary user account exists and requires password change at
  first logon.
- Baseline GPO placeholders exist and are linked without aggressive settings.
- The operator has physical or console access to the pilot workstation.

## Pilot Flow

### 1. First Domain Logon

At the Windows sign-in screen, log in as the selected pilot domain user.

Expected behavior:

- Windows accepts the temporary password only as a first-logon credential;
- Windows forces the user to set a new password;
- the new password satisfies domain policy;
- the user profile is created successfully;
- the user reaches the desktop without local administrator rights.

Do not paste the temporary or final password into Git, chat, logs, runbooks or
sign-offs.

### 2. Post-Logon Validation

From the pilot workstation, validate basic domain state:

```powershell
whoami
whoami /groups
hostname
nltest /dsgetdc:<domain.example.invalid>
nslookup <domain.example.invalid>
w32tm /query /status
```

Expected behavior:

- `whoami` identifies the domain user;
- group output includes the expected baseline domain groups;
- the domain controller can be discovered;
- DNS resolves through AD DNS;
- Windows Time source is the domain controller or domain hierarchy.

### 3. GPO Refresh

Run:

```powershell
gpupdate /force
gpresult /r
```

Expected behavior:

- `gpupdate /force` completes without policy-processing errors;
- `gpresult /r` shows the baseline user and computer policy scope;
- no aggressive or unapproved policy is applied during the pilot.

For deeper troubleshooting, export the report locally:

```powershell
gpresult /h "$env:TEMP\gpo-report.html"
```

Do not commit exported reports to Git. They can contain private domain, user and
machine details.

### 4. Cached Logon Check

After one successful online domain logon, perform a controlled cached-logon
check only if it will not interrupt a real user:

1. Confirm the user has logged in successfully while the DC was reachable.
2. Disconnect the workstation from the network or isolate it from the DC.
3. Attempt logon with the same domain user and current password.
4. Restore network access immediately after the test.

Expected behavior:

- cached logon succeeds for the previously logged-in user;
- domain resources are not expected to work while the DC/network is unavailable;
- after reconnecting, DNS, time and DC discovery work again.

## Stop Conditions

Stop the pilot if:

- first-logon password rotation fails;
- the user receives local administrator rights unexpectedly;
- DNS no longer points to AD DNS;
- Windows Time is not using the domain hierarchy after join;
- `gpupdate` returns policy-processing errors;
- cache logon behavior is inconsistent or unclear;
- the test would interrupt production users.

## Rollback

Rollback depends on what failed:

- disable the pilot user account if the account was created incorrectly;
- move the workstation to a quarantine/test OU if GPO scope is wrong;
- unlink or disable only the pilot GPO if a policy causes problems;
- restore endpoint DNS/time settings using the Windows endpoint pilot runbook;
- remove the computer object and DNS records only after explicit operator
  approval.

Prefer disabling or isolating objects before deletion.

## Evidence and Sign-Off

Public-safe sign-off may include:

- run class: `samba-ad-user-logon-gpo-pilot`;
- pilot count, not full user or endpoint inventory;
- first-logon password rotation status;
- domain DNS status;
- domain time status;
- GPO refresh status;
- cached logon status;
- non-claims and next gate.

Do not include:

- passwords;
- screenshots with user data;
- full `gpresult` reports;
- full group membership dumps if they expose private structure;
- raw command output with private topology.

## Tecrax Activation Gate

Current level: `L1 - public-safe runbook`.

Do not promote this step to a bounded mutation yet. The next possible Tecrax
artifact is a read-only validation helper or intent after multiple pilot logons
prove that the checks are stable and can be redacted safely.

