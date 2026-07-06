# Basic incident handling runbook

This runbook defines the first operator-owned incident-handling baseline for the
Tecrax/MBP infrastructure stack.

It gives the operator a small, repeatable process for turning a monitoring or
security signal into a GLPI incident record and a contained follow-up. It is not
a full NIS2/KSC2 incident-response program.

## Scope

The baseline covers:

- initial triage for Zabbix, Wazuh, GLPI, user-reported and operator-observed
  incidents;
- minimal severity and category vocabulary in Polish;
- GLPI incident record expectations;
- containment and escalation decision points;
- evidence custody boundaries;
- closure and follow-up requirements.

It does not configure automatic Wazuh-to-GLPI routing, live Zabbix ticket
creation, legal notification workflows, user notification templates, forensics,
malware reverse engineering, breach reporting, compliance readiness or a full
on-call process.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic service aliases and roles;
- incident categories and severity labels;
- pass/fail validation summary;
- explicit non-claims;
- generic evidence classes.

Must remain outside Git and public sign-offs:

- real ticket contents containing user data;
- usernames, emails, workstation names or file paths unless separately redacted;
- security alert payloads;
- IP lists, packet captures, logs and raw command output;
- credentials, tokens, keys, recovery codes and private vault material;
- legal/privacy-sensitive assessment details.

## Severity Vocabulary

Use Polish operator-facing labels:

- `Awaria krytyczna` - service outage, confirmed compromise, active data-loss
  risk or broad production impact;
- `Wysoki` - important service degraded, suspicious security event, backup
  failure affecting recovery confidence or privileged-access anomaly;
- `Średni` - limited incident requiring operator action but no broad outage;
- `Ostrzeżenie` - early warning, noisy but actionable signal or repeated
  condition needing review;
- `Informacja` - context-only event, not an incident unless correlated with
  other evidence.

Keep upstream Zabbix/Wazuh technical names in the technical appendix when they
help debugging. Do not translate raw rule ids, item keys or event ids.

## Incident Categories

Start with a small category set:

- `Dostępność` - availability and service outage;
- `Wydajność` - resource pressure, overload and degradation;
- `Dysk / miejsce` - storage pressure, retention and capacity;
- `Backup` - failed, missing or unverified backup/restore path;
- `Bezpieczeństwo` - suspected compromise, suspicious login, malware or policy
  violation;
- `Sieć` - switch, gateway, VLAN, reachability and DNS/DHCP path issues;
- `DNS / domena` - AD DNS, domain login, Kerberos, GPO and time hierarchy;
- `Monitoring wizyjny` - Frigate/camera host availability and recording
  pipeline issues;
- `Usługi administracyjne` - Proxmox, PBS, GLPI, BookStack, Grafana, Wazuh,
  Zabbix and admin-tools.

## Procedure

### 1. Intake

Record the source:

- Zabbix problem;
- Wazuh alert;
- GLPI user request;
- operator observation;
- external signal.

If the source contains credentials, personal data, raw logs or private payloads,
do not paste it into public docs or Git. Store it only in the approved private
ticket/evidence location.

### 2. Triage

Answer four questions:

1. Is a critical service down or degraded?
2. Is there evidence of unauthorized access, malware, data loss or privileged
   account abuse?
3. Is backup or restore confidence affected?
4. Is the event recurring or spreading?

If the answer to any question is yes, create or update a GLPI incident ticket.
If the event is informational only, keep it as monitoring context unless it
correlates with another incident.

### 3. Classify

Assign:

- severity;
- category;
- affected service alias or device class;
- current state: `new`, `investigating`, `contained`, `waiting`, `resolved` or
  `postmortem`.

Use the smallest severity that still forces the right operator behavior. Do not
inflate every monitoring warning into an incident.

### 4. Contain

Containment can include:

- isolating a workstation;
- disabling a compromised account;
- stopping a risky service;
- blocking a network path;
- pausing a noisy automation;
- switching to a known-good backup or manual process.

Do not run destructive cleanup, file deletion, credential rotation, firewall
changes, NAS mutations or CA/key operations unless a separate runbook or direct
operator decision allows it.

### 5. Preserve Evidence

Preserve only what is needed:

- GLPI ticket id;
- monitoring event id;
- timestamp and source system;
- bounded summary;
- commands run by the operator;
- links to private evidence locations when required.

Avoid raw log dumps in public sign-offs. If screenshots or exports contain
private data, store them in the private evidence location and reference only the
class of evidence.

### 6. Resolve

Before closing:

- confirm the service or endpoint is back to the expected state;
- confirm the alert is resolved or intentionally suppressed;
- record what changed;
- record whether follow-up is required;
- if the incident affected backup, identity, DNS, PKI, NAS data or privileged
  accounts, require a post-incident follow-up item.

### 7. Follow Up

Create a follow-up when needed:

- source tuning in Zabbix/Wazuh;
- hardening action;
- backup/restore proof;
- user communication;
- documentation update;
- credential rotation;
- bounded Tecrax/RExecOp automation candidate.

Follow-up is not optional for repeated incidents. Repeated manual handling is a
candidate for deterministic Tecrax/RExecOp workflow only after the process is
stable and well bounded.

## Stop Conditions

Stop and escalate before acting if:

- containment would delete or overwrite data;
- the incident touches Synology NAS data and a delete-class action is involved;
- credential values would need to be shared with AI, chat, Git or public docs;
- the action would expose AD/DC, VPN, firewall, PKI or vault material;
- legal/privacy notification may be required;
- the action would interrupt production services without an operator-approved
  maintenance decision.

## Validation

Validate the baseline by creating a controlled, non-sensitive GLPI test incident
or reviewing an existing harmless incident record and confirming:

- source is recorded;
- severity and category are present;
- affected service/device class is present;
- private evidence is not copied into public docs;
- resolution and follow-up fields are understandable;
- the ticket can be found later by category and date.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `basic-incident-handling-baseline`;
- GLPI incident model summary;
- severity/category vocabulary summary;
- validation result;
- explicit non-claims.

Non-claims:

- no NIS2/KSC2 readiness;
- no legal notification workflow;
- no full forensics procedure;
- no automatic Wazuh-to-GLPI routing;
- no live Zabbix ticket routing unless separately enabled;
- no automatic containment;
- no secret custody or vault completion.

## Tecrax Artifact Target

Current target: `L1` public-safe runbook.

Future candidates:

- `L2` helper for creating sanitized incident templates;
- `L3` read-only incident coverage summaries from GLPI/Zabbix/Wazuh;
- `L4` bounded ticket creation only for allowlisted, action-oriented classes;
- `L5` deterministic reactions only after repeated, stable workcycles and
  GovEngine admission.

## Next Gate

Use this baseline during the next real or test incident. Do not expand
automation until at least one controlled incident record proves that the
classification, evidence boundary and follow-up process are usable.
