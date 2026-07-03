# Windows Endpoint Update Management Pilot Runbook

This runbook covers the first controlled Windows endpoint update-management
baseline for domain-joined pilot workstations.

It is an operator-owned L1 runbook. It does not turn Tecrax into WSUS, RMM,
Windows Update orchestration, Wake-on-LAN automation or a generic endpoint
manager.

## Scope

Allowed:

- create a separate pilot GPO for Windows endpoint update behavior;
- link the pilot GPO only to the approved workstation OU;
- set a conservative Windows Update / Windows Update for Business baseline;
- prevent forced automatic restart while a user is logged on;
- define active hours and a scheduled install window;
- defer quality and feature updates for the pilot;
- validate policy application on one or two pilot endpoints;
- record Wake-on-LAN as a later maintenance-window enhancement.

Not allowed:

- editing Default Domain Policy;
- broad endpoint rollout;
- forcing immediate updates or restarts on user workstations;
- approving individual KB packages;
- deploying WSUS/RMM before the pilot proves a need for it;
- waking endpoints through WoL without inventory/IPAM and explicit test scope;
- storing private OU DNs, GPO GUIDs, endpoint names, IPs, MACs or update logs in
  Git.

## Preconditions

- Samba AD DC is healthy.
- The pilot endpoint is joined to the domain and placed in the workstation OU.
- The endpoint has already passed domain-user logon, GPO refresh and rollback
  sanity checks.
- Emergency local/console access exists before changing update/restart policy.
- RDP/SSH or local operator access is available for validation.
- Private endpoint inventory and domain administrative credentials remain
  outside the repository.

## Pilot Policy Shape

Use a separate GPO, for example:

```text
GPO_ORG_Workstations_Update_Pilot
```

The real organization prefix, OU DN and GPO GUID are deployment-owned data.

Recommended first pilot values:

```text
Automatic updates: enabled
Scheduled install: 03:00
Scheduled install day: every day or approved maintenance cadence
No auto-reboot with logged-on users: enabled
Active hours: 07:00-18:00
Quality update deferral: 7 days
Feature update deferral: 30 days
WSUS/RMM: not enabled in the first pilot
```

These values are intentionally conservative. They reduce random user disruption
without pretending that the environment has full per-update approval yet.

## Registry Policy Validation

After linking the pilot GPO, refresh computer policy on the pilot endpoint:

```powershell
gpupdate /target:computer /force /wait:60
```

Validate bounded registry facts:

```powershell
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU"
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v ActiveHoursStart
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v ActiveHoursEnd
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v DeferQualityUpdatesPeriodInDays
reg query "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate" /v DeferFeatureUpdatesPeriodInDays
```

Expected pilot evidence:

- automatic updates are policy-managed;
- scheduled install time is the approved maintenance hour;
- active hours match the approved user-work window;
- automatic reboot with logged-on users is disabled;
- quality and feature update deferrals match pilot values.

Do not commit full Windows Update logs, event logs or `gpresult` exports.

## Rings

Do not roll out to all endpoints at once. Define rings first:

```text
pilot     - 1-2 endpoints under operator observation
staff     - ordinary staff endpoints after pilot success
critical  - machines with explicit maintenance windows or manual approval
```

The exact membership list is private operational inventory and should not be
stored in the public Tecrax repository.

## Wake-on-LAN Future Gate

Wake-on-LAN can be useful for late-night maintenance windows, but it is not part
of the first update-policy baseline.

Before WoL is allowed, validate:

- endpoint is on Ethernet and supports WoL in BIOS/UEFI and NIC settings;
- switch, VLAN and gateway path permit the approved magic packet flow;
- MAC/IP/VLAN inventory is complete and private;
- update rings and maintenance windows exist;
- public or reader-facing endpoints have explicit exclusions;
- wake, update, reboot and evidence collection have a rollback/stop path.

Possible future deterministic workflow:

```text
collect update status -> wake pilot ring -> wait for online state ->
trigger scan/install window -> validate pending reboot -> schedule reboot ->
collect evidence -> escalate exceptions
```

That workflow belongs to a later RExecOp/GovEngine/SCLite-backed path, not to
this L1 runbook.

## Stop Conditions

Stop if:

- the GPO would affect a broader OU than intended;
- a user endpoint would restart without explicit approval;
- active hours or maintenance windows are wrong;
- the endpoint is on Windows Home or otherwise outside domain-management scope;
- Windows Update policy conflicts with another management tool;
- the operator cannot verify local/console recovery;
- WoL requires unknown switch/VLAN/firewall changes.

## Rollback

Prefer reversible changes:

- unlink or disable the update pilot GPO;
- move the endpoint to a quarantine/test OU if scope is wrong;
- reset the affected Windows Update policy keys only on the pilot endpoint if
  needed;
- restore the prior update behavior before widening rollout.

Do not delete endpoint or AD objects as a rollback for update-policy mistakes.

## Evidence and Sign-Off

Public-safe sign-off may include:

- run class: `windows-endpoint-update-management-pilot`;
- pilot endpoint count;
- update GPO linked: yes/no;
- computer policy refresh status;
- scheduled install window;
- active hours;
- no-auto-reboot-with-logged-on-users status;
- quality/feature deferral status;
- WoL future gate status;
- non-claims and next gate.

Do not include:

- private endpoint names, IPs, MACs or OU DNs;
- GPO GUIDs if they expose private topology;
- full Windows Update logs;
- raw `gpresult` exports;
- screenshots with user data.

## Tecrax Activation Gate

Current level: `L1 - public-safe runbook`.

No helper or bounded mutation is added yet. A future L2 helper is reasonable only
after the update GPO shape is repeated and can be represented as fixed inputs,
dry-run validation, explicit stop conditions and no generic shell passthrough.

Potential future L3 facts:

- endpoint update policy applied;
- pending reboot state;
- update deferral policy summary;
- update ring coverage counts;
- WoL capability presence by class, never raw private MAC inventory.

Potential future L4/L5 behavior is deferred until after stable ring policy,
inventory/IPAM, monitoring visibility, operator approval, GovEngine admission,
RExecOp execution contracts and SCLite evidence shape exist.
