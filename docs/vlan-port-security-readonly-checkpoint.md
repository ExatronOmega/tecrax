# VLAN and port-security read-only checkpoint

This document is a design checkpoint for future switch VLAN and port-security
observations. It does not activate an intent, workflow, connector action or facts
contract.

## Decision

Do not implement VLAN or port-security collection in the current network-device
slice. The existing `collect_network_device_inventory_readonly` and
`assess_network_device_management_posture_readonly` operations remain limited to
bounded device identity and SSH management posture.

VLAN and port-security may become separate read-only slices only after the
conditions below are met.

## Ownership

- Tecrax owns the infrastructure semantics, fixed wrapper action vocabulary,
  facts contract, validation rules, parser fixtures and runbook.
- RExecOp owns domain-neutral lifecycle, connector execution, action-shape
  enforcement and receipts. RExecOp must not learn switch-specific semantics.
- GovEngine owns admission and policy decisions for the new actions.
- SCLite owns canonical evidence, receipts and bundle truth.
- The operator-owned wrapper, target mappings, SSH options and any legacy device
  unlock flow remain outside Git.

## Minimum future shape

The future implementation must be split rather than folded into generic
inventory:

- `collect_switch_vlan_summary_readonly`: bounded VLAN summary only;
- `assess_switch_port_security_posture_readonly`: bounded port-security posture
  only.

Each future operation needs its own:

- facts contract and JSON schema;
- profile intent and validation rule;
- fixed connector action names;
- sanitized golden fixtures per vendor and firmware family;
- negative fixtures for prompt drift, unsupported devices and unsafe output;
- operator sign-off that contains no private topology or addresses.

## Allowed bounded facts

Allowed VLAN facts are count or boolean summaries only:

- VLAN count;
- whether a management VLAN signal is present, if the device exposes it without
  revealing topology;
- whether default VLAN usage is observed as a bounded boolean;
- whether the observation is complete, partial or blocked.

Allowed port-security facts are count or boolean summaries only:

- total observed access ports count, if available without interface identity;
- count of ports with port security enabled;
- count of ports without port security enabled;
- count of ports where status is unknown;
- whether sticky MAC or equivalent behavior is observed as an aggregate boolean,
  only if no addresses are retained.

## Forbidden data

The future slice must not retain or emit:

- running or startup configuration dumps;
- full VLAN tables;
- interface names, descriptions, aliases or physical topology;
- MAC addresses, learned addresses, neighbor data or endpoint identities;
- usernames, local user lists, SNMP communities or ACLs;
- firewall, DNS, NTP or routing configuration;
- private target addresses, hostnames, key paths, known-hosts paths or unlock
  material;
- any write command, configuration mode command, save command, reload command or
  generic CLI passthrough.

`show running-config`, `display current-configuration` and equivalent full-config
commands are explicitly out of scope for this checkpoint.

## Wrapper contract

Any future wrapper extension must accept fixed action names only. Candidate names:

- `vlan-summary`;
- `port-security-summary`.

The wrapper output must already be reduced to bounded read-only text before
Tecrax parsing. The wrapper must return non-zero on unexpected prompts,
unsupported devices or output that would require retaining forbidden data.

## Parser and fixture requirements

Parser support must remain explicit per vendor and firmware family. The first
eligible future fixtures would likely be:

- `tplink_sg2452_v1_vlan_summary`;
- `tplink_sg2452_v1_port_security_summary`;
- `hpe_v1910_comware5_vlan_summary`;
- `hpe_v1910_comware5_port_security_summary`.

Fixtures must be synthetic or sanitized and must include canaries proving that
private addresses, MAC addresses, user names, port descriptions and unlock
material do not enter normalized facts.

## Admission and validation requirements

Before activation, each operation must have:

- a sanitized example environment policy rule for the operation and fixed
  connector action;
- deny/fail-closed behavior for unknown action names and mutating modes;
- validation rules requiring complete bounded facts;
- tests proving unsupported output is incomplete rather than guessed;
- tests proving forbidden data is not retained;
- local RExecOp plan/admission coverage through the example environment.

## Exit criteria for this checkpoint

The design is accepted only as a future path. Implementation remains blocked
until:

- the exact device commands are reviewed as read-only on each target family;
- their output can be reduced without retaining forbidden data;
- an operator approves a sanitized fixture and sign-off;
- the new facts contract is reviewed independently of the existing inventory and
  management-posture contracts.
