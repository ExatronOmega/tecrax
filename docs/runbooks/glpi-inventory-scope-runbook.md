# GLPI inventory scope runbook

This runbook defines the first operator-owned scope for GLPI inventory.

It keeps GLPI useful as a helpdesk and inventory register without turning it
into an uncontrolled discovery engine or a second source of truth competing
with Zabbix, Wazuh, AD, Proxmox or the private operator context.

## Scope

The baseline covers:

- which asset classes may be entered in GLPI first;
- which asset classes are deferred;
- manual inventory versus agent-based inventory boundaries;
- required fields for a minimal useful inventory record;
- relationship to monitoring, backup and ownership status;
- validation and sign-off shape.

It does not deploy GLPI agents, perform network discovery, import endpoint data,
sync from AD, sync from Zabbix, change user workstations, mutate NAS data or
claim compliance readiness.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic asset classes;
- generic role names;
- counts by class;
- inventory coverage summary;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- real user names assigned to devices;
- serial numbers, asset tags and warranty details unless separately redacted;
- endpoint hostnames if they reveal people or internal structure;
- private IP plans and full topology exports;
- NAS data paths and share contents;
- credentials, tokens, keys and raw discovery output.

## Source-of-Truth Boundary

Use GLPI as the operational asset and ticket context register.

Do not make GLPI the only source of truth for:

- live availability or metrics: Zabbix owns monitoring state;
- security agent state: Wazuh owns security agent state;
- domain membership and user accounts: Samba AD owns identity state;
- VM/CT runtime state: Proxmox owns virtualization state;
- private target aliases and credentials: operator context owns runtime access
  references.

GLPI should link those domains together at a human-operational level: what the
asset is, what role it has, whether it is monitored, whether it is backed up,
who owns the service and where incidents should be attached.

## Phase 1 Asset Classes

Enter only low-risk, stable infrastructure records first:

- virtualization host;
- VM/CT services already deployed;
- backup service;
- monitoring and security services;
- documentation and helpdesk services;
- selected network devices already monitored;
- NAS as a storage service record, without importing share contents;
- Frigate/video-monitoring host as a service host record.

This phase should prefer manual records or controlled CSV import prepared by the
operator. No network sweep and no endpoint agent rollout.

## Deferred Asset Classes

Defer until the relevant pilot is complete:

- staff workstations and laptops: after AD endpoint pilot and naming/IPAM
  cleanup;
- public-reader computers: after separate public endpoint strategy;
- printers/scanners: after deciding whether they need monitoring, support
  ownership or only documentation;
- cameras: after deciding camera inventory boundary without storing stream
  credentials or private payloads;
- UPS: after firmware/update and monitoring decision;
- Synology user homes and shares: do not import share contents or ACL details
  during this phase.

## Minimal Inventory Fields

For Phase 1 records, keep fields practical:

- asset name or service alias;
- asset class;
- role;
- environment: infrastructure, network, storage, endpoint, public workstation
  or service;
- criticality: critical, important, normal or low;
- monitoring coverage: none, ICMP, SNMP, agent, API or mixed;
- security coverage: none, Wazuh agent, network-only or deferred;
- backup coverage: none, local, external, application-aware or not applicable;
- owner/responsible role, not personal secrets;
- documentation link or runbook reference;
- lifecycle status: active, pilot, deferred, legacy or retired.

Avoid free-form fields containing passwords, private paths, raw command output
or unredacted personal data.

## Procedure

### 1. Prepare Asset Classes

Create or verify a small set of GLPI asset categories for the infrastructure
stack. Keep names stable and Polish-facing where they are operator-visible.

Suggested starting categories:

- `Host wirtualizacji`;
- `Maszyna VM`;
- `Kontener CT`;
- `Usługa administracyjna`;
- `Urządzenie sieciowe`;
- `Storage / NAS`;
- `Monitoring wizyjny`;
- `Endpoint użytkownika`;
- `Komputer publiczny`;
- `Drukarka / skaner`;
- `UPS / zasilanie`.

### 2. Enter Phase 1 Records

Create records manually or through a bounded operator-prepared import.

Start with the infrastructure stack already known to be deployed and monitored.
Do not import users, endpoint agents or network-scan results.

### 3. Link Operational Context

For each Phase 1 record, add only bounded operational context:

- monitoring coverage class;
- backup coverage class;
- incident category;
- documentation/runbook pointer;
- owner/responsible role.

Do not paste raw Zabbix/Wazuh payloads or private operator context files into
GLPI records.

### 4. Validate

Validate:

- records can be found by service/asset class;
- tickets can be linked to a Phase 1 asset;
- no credential values are present;
- no raw discovery dump was imported;
- deferred asset classes remain deferred;
- inventory status does not contradict Zabbix/Wazuh/Proxmox/operator context.

## Stop Conditions

Stop before import or manual entry expansion if:

- the process would expose secrets, serial inventories or private topology in
  Git/public docs;
- GLPI would become the only copy of an operational fact already owned by
  another system;
- endpoint rollout would be needed before AD pilot is complete;
- Synology NAS shares, ACLs or user homes would be imported in detail;
- a network discovery sweep would touch production segments without a separate
  decision.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `glpi-inventory-scope`;
- asset classes in scope;
- asset classes deferred;
- validation summary;
- explicit non-claims.

Non-claims:

- no GLPI agent rollout;
- no network discovery;
- no endpoint inventory rollout;
- no AD/Zabbix/Wazuh/Proxmox sync;
- no complete asset inventory;
- no compliance readiness.

## Tecrax Artifact Target

Current target: `L1` public-safe runbook.

Future candidates:

- `L2` helper for validating sanitized inventory CSV shape;
- `L3` inventory coverage summary comparing GLPI classes with bounded public
  counts from Zabbix/Proxmox/operator context;
- no L4 inventory mutation until identity, IPAM, endpoint and GLPI data model
  decisions are stable.

## Next Gate

Use this scope to create a small Phase 1 infrastructure inventory baseline in
GLPI. Do not add endpoint agents or discovery until the AD endpoint pilot and
IPAM/naming cleanup are ready.
