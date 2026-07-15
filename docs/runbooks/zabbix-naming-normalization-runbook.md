# Zabbix naming normalization runbook

This runbook covers a controlled Zabbix naming and metadata normalization pass
before GLPI ticket automation.

It makes Zabbix host aliases, visible names, groups and tags predictable for
operator-facing Polish alert tickets. It does not rename operating-system
hosts, change DNS, modify Wazuh agent names, alter upstream templates or change
monitoring thresholds.

## Scope

Allowed:

- keep the Zabbix `host` field as the canonical host alias;
- align Zabbix visible names with canonical aliases;
- normalize host groups for infrastructure and network devices;
- add small, stable tags for routing and ticket presentation;
- remove profile/internal staging groups from operator-facing inventory where an
  approved operator-facing group exists;
- add ICMP availability templates to SNMP-managed infrastructure devices when
  the target already has an ICMP interface and monitoring policy expects
  availability plus SNMP.

Not allowed:

- rename Linux, Windows, network-device or NAS hostnames;
- change private addressing, DNS, DHCP or routing;
- edit upstream Zabbix template names, item keys or trigger names;
- change Wazuh agent identities as a side effect;
- remove templates or groups without preserving at least one appropriate group;
- include Zabbix API tokens or raw payloads in Git or sign-offs.

## Naming Model

Use short canonical aliases as the stable operator names:

```text
hypervisor01
backup01
directory01
monitoring01
ticketing01
network-switch-01
security-gateway-01
security-gateway-vlan05
```

The Zabbix `host` and visible `name` should match the canonical alias unless
there is a specific operator decision to expose a longer display name. Human
descriptions belong in tags, inventory fields, BookStack or GLPI, not in mixed
visible-name conventions.

## Group Model

Recommended first groups:

- `<ORG> Infrastructure` for servers, VM/CT services, storage and monitoring
  hosts;
- `<ORG> Network` for gateways and managed switches;
- optional upstream/default groups may remain if useful, but routing should not
  depend on inconsistent staging groups.

Avoid profile-owned staging groups as operator-facing inventory groups. Use
`managed_by=tecrax` as a tag instead.

## Tag Model

Minimum tags for routing:

- `managed_by=tecrax`;
- `category=<infrastructure|network|video-monitoring|storage>`;
- `role=<short role>`;
- `service=<service name>` where the host primarily represents one service.

Tags should help GLPI ticket mapping and Grafana filtering. Do not place
credentials, private URLs or raw topology in tags.

## ICMP Plus SNMP Model

For managed devices with SNMP, keep availability and telemetry separate:

- ICMP check proves reachability;
- SNMP templates provide device metrics.

Adding ICMP to an existing SNMP host is acceptable if the host already represents
that device and no duplicate availability-only host exists for the same
management address.

Gateways may be represented as:

- one SNMP management host;
- separate interface/VLAN ICMP hosts only when they model distinct reachability
  paths.

## Procedure

1. Export current Zabbix hosts, groups, templates and tags.
2. Compare Zabbix canonical aliases with Wazuh agent names.
3. Identify inconsistent visible names, groups and stale tags.
4. Prepare a bounded mutation plan.
5. Apply only metadata-safe changes:
   - visible name normalization;
   - group normalization;
   - tag normalization;
   - ICMP template addition for selected SNMP devices.
6. Re-export Zabbix hosts and compare with the intended plan.
7. Confirm Wazuh agent names were not changed.

## Stop Conditions

Stop if:

- a Zabbix host alias is ambiguous;
- a host would be left without a group;
- a template removal would be required;
- an upstream template would need to be edited;
- the mutation would expose API tokens or raw private payloads;
- a gateway/interface model needs an operator decision before proceeding.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `zabbix-naming-normalization`;
- host count reviewed;
- host count changed;
- group normalization summary;
- tag normalization summary;
- ICMP/SNMP normalization summary;
- explicit non-claims.

Non-claims:

- no DNS/DHCP/IPAM change;
- no Wazuh rename;
- no upstream template rewrite;
- no trigger threshold change;
- no GLPI ticket automation yet.
