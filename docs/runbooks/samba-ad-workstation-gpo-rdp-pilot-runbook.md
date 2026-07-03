# Samba AD Workstation GPO and RDP Pilot Runbook

This runbook covers the first low-impact workstation Group Policy pilot after a
Windows endpoint has joined a Samba AD domain and a real domain-user logon has
been validated.

It is an operator-owned L1 runbook. It does not turn Tecrax into a generic AD
GPO editor, Windows endpoint manager, RDP broker or update orchestration tool.

## Scope

Allowed:

- create separate, narrowly scoped workstation pilot GPOs;
- link the pilot GPOs to the approved workstation OU;
- apply low-impact computer-scope settings for RDP, Windows Firewall and screen
  lock behavior;
- create or use a dedicated domain group for pilot RDP access;
- validate computer-scope GPO refresh on one pilot workstation;
- validate the RDP listener and TCP reachability after reboot/update;
- record the endpoint update-management strategy as a next gate before broad
  rollout.

Not allowed:

- editing Default Domain Policy or Default Domain Controllers Policy;
- broad endpoint rollout;
- NIS2/KSC2 compliance-mode hardening;
- exposing RDP to the public internet;
- deploying endpoint agents;
- forcing production user restarts;
- storing domain admin credentials, real endpoint inventory, private OU paths,
  private IPs, exported `gpresult` reports or raw AD dumps in Git.

## Preconditions

- Samba AD DC is healthy.
- A pilot Windows Pro or Enterprise endpoint is joined to the domain.
- The pilot endpoint is in the approved workstation OU.
- The pilot endpoint uses AD DNS and domain time.
- A real domain-user logon and cached-logon proof have already succeeded.
- The operator has emergency local/console access to the endpoint.
- The operator has an approved privileged path for GPO creation and linking.
- Private SSH keys, known-hosts files, admin credentials and target catalog data
  remain outside the repository.

## Pilot GPO Shape

Use separate GPOs so each behavior can be disabled or rolled back independently:

```text
GPO_ORG_Workstations_RDP_Pilot
GPO_ORG_Workstations_Firewall_Pilot
GPO_ORG_Workstations_ScreenLock_Pilot
GPO_ORG_Workstations_Admin_Template
```

The real organization prefix, OU DN and GPO GUIDs are deployment-owned data.
Do not commit them if they identify a private environment.

Expected intent:

- RDP pilot GPO: allow RDP for approved internal/VPN pilot use only.
- Firewall pilot GPO: enable Windows Firewall for Domain, Private and Public
  profiles; default inbound block and outbound allow; add only explicit
  exceptions needed for the pilot.
- Screen lock pilot GPO: set an inactivity lock around 15 minutes and require
  password on resume.
- Admin template GPO: empty or nearly empty placeholder for future startup
  scripts or agent rollout, with no broad deployment enabled yet.

Do not place these settings in the default domain policies during the pilot.

## RDP Access Model

Use a dedicated domain group rather than adding ordinary users directly to local
RDP groups:

```text
GG_ORG_Remote_Desktop_Users
```

Add only approved pilot users. On each pilot endpoint, the domain group should be
added to the localized local Remote Desktop Users group. Prefer SID-based lookup
for validation because the local group name depends on the Windows display
language:

```powershell
$group = (New-Object System.Security.Principal.SecurityIdentifier('S-1-5-32-555')).Translate([System.Security.Principal.NTAccount]).Value.Split('\')[-1]
Get-LocalGroupMember -Group $group
```

RDP is allowed only from the internal network or VPN. Public exposure is a stop
condition.

## GPO Refresh Validation

On the pilot workstation, refresh computer policy:

```powershell
gpupdate /target:computer /force /wait:60
```

Validate only bounded facts in public-safe notes:

```powershell
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows NT\Terminal Services" /v fDenyTSConnections
reg query "HKLM\SOFTWARE\Policies\Microsoft\WindowsFirewall\DomainProfile" /v EnableFirewall
reg query "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" /v InactivityTimeoutSecs
```

Expected values:

- RDP policy permits connections for the pilot;
- Domain-profile firewall policy is enabled;
- inactivity timeout is set to the approved pilot value.

Do not commit full `gpresult` output. It can expose private names, paths and
policy structure.

## RDP Listener Validation

After a reboot or Windows update, validate the RDP listener:

```powershell
Get-Service TermService,UmRdpService
qwinsta
Get-NetTCPConnection -LocalPort 3389 -ErrorAction SilentlyContinue
Test-NetConnection -ComputerName 127.0.0.1 -Port 3389
```

From an operator workstation, validate internal TCP reachability without
recording private addresses in Git:

```bash
timeout 5 bash -c '</dev/tcp/windows-endpoint.example.invalid/3389'
```

Expected behavior:

- `TermService` is running;
- `rdp-tcp` is in `Listen` state;
- TCP 3389 is reachable from the approved internal management path;
- the dedicated domain RDP group remains in the localized local RDP group.

If the policy appears correct but `rdp-tcp` is not listening, review the
TerminalServices event logs and reboot/update state before widening firewall or
AD changes.

## Endpoint Update-Management Gate

Do not start broad endpoint rollout until update behavior is controlled.

The next runbook or helper candidate should define:

- update rings such as `pilot`, `staff` and `critical`;
- Windows Update for Business or GPO baseline for active hours;
- no forced restart while a user is logged on, unless explicitly approved;
- restart windows and pending-reboot visibility;
- feature-update deferrals;
- missing-patch visibility through monitoring or ticketing;
- a later WSUS/RMM decision only if per-update approval is required.

At this stage, this is a planning gate, not an active Tecrax mutation or
endpoint update orchestrator.

## Stop Conditions

Stop and roll back or isolate the pilot if:

- the GPO target is broader than the approved workstation OU;
- Default Domain Policy would need to be edited;
- RDP would be reachable from the public internet;
- firewall policy breaks emergency access;
- `gpupdate` reports policy-processing errors;
- `rdp-tcp` does not listen after reboot and the cause is unclear;
- a Windows update or reboot would interrupt a production user;
- the operator cannot verify local/console recovery access.

## Rollback

Prefer reversible actions:

- unlink or disable the specific pilot GPO that caused the issue;
- move the workstation to a quarantine/test OU if scope is wrong;
- remove the pilot domain group from the local RDP group;
- restore the previous firewall/RDP setting on the pilot endpoint;
- leave domain accounts and computer objects intact unless explicit cleanup is
  approved.

Do not delete AD objects as a first response. Disable, unlink or isolate first.

## Evidence and Sign-Off

Public-safe sign-off may include:

- run class: `samba-ad-workstation-gpo-rdp-pilot`;
- pilot endpoint count, not full endpoint inventory;
- GPO count and high-level role names;
- workstation OU scoped: yes/no;
- computer-scope GPO refresh status;
- RDP listener validation status;
- internal TCP reachability status;
- update-management gate status;
- non-claims and next gate.

Do not include:

- domain admin credentials;
- private hostnames, IPs, OU DNs or GPO GUIDs if they expose topology;
- raw event logs;
- full `gpresult` reports;
- screenshots with user data.

## Tecrax Activation Gate

Current level: `L1 - public-safe runbook`.

No helper is added yet. A future L2 helper may be justified only after the same
pilot flow is repeated on multiple endpoints and can be bounded to fixed
arguments, strict preflight, dry-run output and no generic shell passthrough.

Potential future L3 facts:

- workstation GPO presence by role;
- endpoint policy-applied status;
- RDP listener status;
- pending reboot / update ring status.

Potential future L4 mutations are deferred until after stable runbooks,
operator-owned wrappers, GovEngine admission, RExecOp execution contracts and
SCLite evidence shape exist.
