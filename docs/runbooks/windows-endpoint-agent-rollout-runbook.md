# Windows endpoint agent rollout runbook

This runbook covers the first controlled rollout package for Zabbix and Wazuh
agents on domain-joined Windows endpoints.

It is a planning and operator execution gate for one or two pilot workstations.
It does not install agents broadly, store enrollment secrets, change detection
policy, or turn Tecrax into a Windows software deployment system.

## Scope

Allowed:

- define the first endpoint rollout rings;
- prepare separate AD/GPO delivery paths for Zabbix Agent 2 and Wazuh Agent;
- use a pilot OU or pilot security group before staff-wide rollout;
- validate agent health on one pilot endpoint;
- document rollback and stop conditions;
- keep installation credentials and enrollment material outside Tecrax.

Not allowed:

- deploy to all staff endpoints in the first pass;
- deploy to public-reader machines or unmanaged networks;
- store Wazuh enrollment passwords, Zabbix API tokens or MSI secrets in Git;
- embed NAS, mail or user-data credentials in GPO;
- bypass the Windows Pro/domain-joined endpoint gate;
- use AI/LLM output as an execution path for arbitrary endpoint commands.

## Public and Private Boundary

Safe in public docs and sign-offs:

- rollout ring names;
- package class and product major line;
- target count;
- GPO names without private topology;
- validation summary;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- Zabbix API tokens;
- Wazuh enrollment passwords and generated agent keys;
- private endpoint inventories until classified as safe;
- MSI files if redistribution terms are unclear;
- raw GPO backups containing private paths or credentials;
- screenshots or transcripts with user data.

## Rollout Rings

Use small rings and stop after each gate:

```text
pilot     - one or two operator-supervised domain workstations
staff     - ordinary staff endpoints after pilot success
critical  - delayed rollout for director/accounting/special workstations
public    - separate future track for reader/public machines
```

Do not include Windows Home devices. They must be upgraded to Windows Pro before
domain join and endpoint management.

## Baseline Model

Recommended first model:

- Windows endpoint is domain joined.
- Endpoint is in the approved workstation OU.
- Time, DNS and GPO refresh are already healthy.
- Windows Update for Business pilot policy exists.
- Zabbix and Wazuh are deployed through separate GPO/startup-script paths.
- Agent configuration is explicit and host naming follows the approved template.

Keep Zabbix and Wazuh separate. A Zabbix failure should not block Wazuh rollback,
and a Wazuh enrollment failure should not remove Zabbix monitoring.

## Zabbix Agent 2 Gate

Prepare a Windows-specific package path:

- installer source approved by the operator;
- hostname derived from the endpoint name;
- active checks preferred for the first pass;
- host template assignment controlled from Zabbix;
- no Zabbix API token in the GPO or endpoint script.

Validate on the pilot endpoint:

- service is installed and running;
- Zabbix sees the expected endpoint host;
- `agent.ping` is healthy;
- no duplicate host appears under a temporary or wrong name.

## Wazuh Agent Gate

Prepare a separate Wazuh package path:

- installer source approved by the operator;
- manager endpoint and agent group chosen by the operator;
- enrollment secret provided through an operator-owned private path;
- package repository or auto-update behavior explicitly controlled after install.

Validate on the Wazuh manager:

- endpoint appears under the expected host alias;
- agent status is active;
- enrollment secret is not present in Git, public docs or shell transcripts;
- no duplicate stale agent was created.

## GPO Delivery Model

Use one of these after the pilot design is reviewed:

- startup script for a minimal first package;
- Group Policy Software Installation if package behavior is predictable;
- later RMM/MDM/WSUS-like tooling only if GPO becomes too brittle.

The first pilot may use startup scripts because they are transparent and easy to
roll back. Do not combine user-data mapping, NAS credentials, browser settings
and agent rollout into one GPO.

Recommended split:

```text
GPO_MBP_Workstations_ZabbixAgent_Pilot
GPO_MBP_Workstations_WazuhAgent_Pilot
```

Link only to the approved workstation OU or target only the pilot security group.

## Rollback

Rollback must be prepared before rollout:

- unlink or disable only the affected agent GPO;
- stop further rollout rings;
- uninstall the affected agent from the pilot endpoint if required;
- remove duplicate/stale host records from Zabbix or Wazuh only after operator
  approval;
- preserve evidence of the failure without copying secrets.

Do not delete endpoint AD objects as rollback.

## Stop Conditions

Stop if:

- the endpoint is not domain joined or not in the expected OU;
- the endpoint is Windows Home;
- DNS, time or GPO refresh is not healthy;
- installer source cannot be verified;
- enrollment secrets would be exposed to Git, chat, shell history or LLM tooling;
- host naming creates duplicates;
- user work is interrupted;
- security software or firewall changes are required outside the approved pilot.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `windows-endpoint-agent-rollout-pilot`;
- target ring and endpoint count;
- Zabbix gate status;
- Wazuh gate status;
- rollback readiness;
- explicit non-claims.

Non-claims:

- no broad endpoint rollout yet;
- no public-reader machine rollout;
- no NAS/user-data migration;
- no final compliance hardening;
- no automatic remediation.

## Tecrax Artifact Decision

Current activation level: `L1 - public-safe runbook`.

A helper may be added later only after two or more pilot endpoints prove the
same command shape. A future helper should generate bounded package checks and
validation summaries, not carry secrets or execute arbitrary PowerShell.
