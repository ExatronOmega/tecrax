# Zabbix Synology community template adoption runbook

This runbook covers adopting an upstream Zabbix Community Template for a
Synology NAS that is already monitored through an ICMP/SNMP baseline.

It is an operator-owned Zabbix configuration step. It is not a Tecrax bounded
mutation intent yet.

## Scope

This adoption pass covers:

- selecting the correct Synology community template family;
- importing a Zabbix-version-compatible template;
- linking it to an existing Synology host already validated through SNMP;
- validating discovered storage, disk, SMART, RAID and system-health items;
- recording public-safe sign-off evidence.

It does not enable SNMP on the NAS, change NAS storage, alter shares, modify
NAS users, rotate credentials, tune alert channels, delete existing templates or
replace the existing local baseline without a separate review.

## Public and Private Boundary

Safe in public docs and sign-offs:

- template family and imported template version;
- Zabbix major/minor version class;
- target alias and role;
- linked template names;
- validation counts;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- Zabbix API tokens and web credentials;
- SNMP communities, SNMPv3 users and passwords;
- complete target addressing or private topology;
- NAS serial numbers and license identifiers;
- raw API payloads containing host interfaces, secrets or private inventory.

## Template Selection

For a general Synology NAS, prefer the community template family:

```text
Storage_Devices/Synology/template_synology_diskstation_snmpv3
```

Use specialized templates only when their product scope is actually deployed:

- backup templates only for Synology Backup or Hyper Backup monitoring;
- DSM cluster templates only for a matching DSM cluster deployment;
- older non-SNMPv3 DiskStation templates only if the newer family cannot be
  imported or validated.

Choose the newest template version that the running Zabbix server accepts. A
template exported for a newer Zabbix release may be rejected by an older Zabbix
server even when the monitored OIDs are valid.

## Prerequisites

- Zabbix VM deployment/adoption gate is complete.
- The NAS host already exists in Zabbix under a public-safe alias.
- ICMP and SNMP read-only baseline are already green for the NAS.
- SNMP credentials are stored outside Git, preferably as host-level secret
  macros or an equivalent operator-owned secret path.
- A Zabbix API token is available from an operator-owned secret path outside Git.
- The operator has a recent Zabbix backup or rollback path for configuration
  mistakes.

## Procedure

### 1. Confirm Zabbix Version

Check the server API version without exposing credentials. Use this to select a
compatible template export version.

Stop if API access requires pasting a token into a tracked file, shell history or
public transcript.

### 2. Download Template Outside Repository

Download the upstream YAML into a temporary/operator workspace, not into the
Tecrax repository.

Inspect the YAML before import:

- export version;
- template name;
- template group;
- top-level item count;
- discovery rules;
- value maps;
- trigger scope.

Do not commit upstream YAML dumps unless a separate vendoring decision has been
made.

### 3. Import Template

Import the selected YAML through the Zabbix API or UI with rules that create
missing template groups, templates, items, discovery rules, triggers, graphs and
value maps.

Prefer update-safe import rules. Do not use a destructive import policy that
deletes existing unrelated templates or host configuration.

If import fails because the export version is unsupported, try the next older
template export from the same family. Record the reason in the sign-off.

### 4. Link Template to Existing NAS Host

Link the imported Synology template to the existing NAS host. Preserve the
existing ICMP/SNMP baseline while validating the community template.

Do not remove the local baseline template in the same step unless:

- the new template has passed validation;
- duplicate triggers have been reviewed;
- threshold differences are understood;
- rollback is clear.

### 5. Validate

Validate after at least one polling/discovery cycle:

- host SNMP interface is available;
- no unsupported items remain after discovery stabilizes;
- no new active problems were introduced;
- storage size and used values are present;
- storage percentage calculated items are healthy;
- disk status and temperature items are discovered;
- RAID or storage-pool status items are discovered when exposed by the NAS;
- system model/version/temperature items are collected without exposing serials.

Calculated LLD items can temporarily show unsupported immediately after link
time because source values have not been collected yet. Treat that as pending,
not failed, until a second validation cycle confirms the state.

## Stop Conditions

Stop before sign-off if any of these are true:

- a secret would be exposed in Git, logs or public docs;
- the template import requires deleting existing monitoring;
- SNMP baseline is not healthy before template link;
- unsupported items remain after enough polling cycles and the cause is unclear;
- new active problems appear and are likely template-induced false positives;
- the template scope does not match the actual Synology deployment.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `zabbix-synology-community-template-adoption`;
- target alias and role;
- Zabbix version class;
- selected template family and imported export version;
- linked template names;
- validation summary;
- temporary unsupported observations, if any;
- explicit non-claims.

Non-claims:

- no NAS configuration changes;
- no SNMP credential rotation;
- no alert-channel tuning;
- no Grafana dashboard update;
- no full DSM security audit;
- no replacement of local thresholds unless separately reviewed.

## Tecrax Artifact Decision

Current activation level: `L1 - public-safe runbook`.

A helper/wrapper is not required for the first adoption because importing and
linking Zabbix templates is a broad configuration mutation. Promote this to `L2`
only after repeated use shows a stable, narrow contract such as:

- fixed template family allowlist;
- explicit Zabbix version compatibility check;
- fixed target alias input;
- no generic API passthrough;
- dry-run/report mode;
- non-destructive import rules;
- post-link validation and fail-closed reporting.

Do not promote this directly to a bounded mutation intent until the helper,
pre-state checks, stop conditions, rollback path, GovEngine admission and SCLite
evidence shape are stable.

## Next Gate

Observe the community template for duplicate alerts and threshold overlap with
the local Tecrax Synology baseline. If the community template remains stable,
decide whether to keep both templates or retire the local baseline after a
separate threshold review.
