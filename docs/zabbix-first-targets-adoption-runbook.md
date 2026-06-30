# Zabbix first targets adoption runbook

This runbook covers the first monitored-target adoption gate for the Zabbix
baseline.

It uses a deliberately narrow monitoring scope: ICMP availability for the base
infrastructure hosts. It does not claim full host metrics, agent coverage,
alert routing, dashboards or incident response readiness.

## Scope

The adoption pass covers:

- creating a dedicated infrastructure host group;
- adding the first base infrastructure hosts;
- linking the default `ICMP Ping` template;
- avoiding agent templates until agents are actually installed;
- validating first ICMP values;
- recording public-safe sign-off evidence.

It does not install agents, configure SNMP, discover networks, tune triggers,
create notification channels, import dashboards or store Zabbix API tokens in
Tecrax.

## Public and Private Boundary

Safe in public docs and sign-offs:

- target aliases and service roles;
- monitoring class: ICMP availability;
- host group name if non-sensitive;
- validation summary;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- Zabbix API tokens;
- Zabbix web credentials;
- private target catalog with complete addressing;
- raw API payloads containing secrets;
- exported Zabbix configuration if it contains private topology.

## Prerequisites

- Zabbix VM deployment gate is complete.
- Zabbix web credential has been rotated by the operator.
- Zabbix API token is created by the operator and stored in an operator-owned
  secret path outside Git.
- AD DNS record for the Zabbix host exists.
- Zabbix PostgreSQL logical dump gate is complete or explicitly deferred.

## Procedure

### 1. Verify API Access

Validate the API token without printing it. A safe first check is API version
or a read-only `hostgroup.get` call.

Do not paste the token into shell history, Git-tracked files or chat logs.

### 2. Create Host Group

Create a dedicated first-pass infrastructure group. Keep the name generic and
non-secret.

### 3. Add First Hosts

Add the initial service hosts with static interfaces and link only `ICMP Ping`.

Recommended first targets:

- Proxmox host;
- Proxmox Backup Server;
- Samba AD DC;
- AdGuard Home;
- admin-tools;
- Zabbix self host.

If a default Zabbix self host already exists, normalize it instead of creating
a duplicate. Remove or avoid agent templates until an agent is present.

### 4. Validate

Validate:

- hosts exist in the intended group;
- each host has the expected service address/interface;
- `ICMP Ping` is linked;
- first `icmpping` value is `1`;
- packet loss value is `0`;
- item state is normal;
- no new false-positive problems were introduced.

## Stop Conditions

Stop before sign-off if any of these are true:

- API token would be exposed to LLM/tooling output;
- host creation requires guessing private topology;
- ICMP item state is unsupported;
- a template claims metrics that are not actually collected;
- default self-host changes would break Zabbix server health monitoring;
- new false-positive problems remain active.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- run class: `zabbix-first-targets-adoption`;
- host group;
- monitored target aliases;
- monitoring class;
- validation summary;
- cleanup summary, if default templates were adjusted;
- explicit non-claims.

Non-claims:

- no Linux/Windows agent coverage;
- no SNMP coverage;
- no alert routing;
- no Grafana dashboard;
- no Wazuh integration;
- no network discovery;
- no incident procedure readiness.

## Next Gate

After ICMP availability is stable, choose the next monitored depth:

- Proxmox/PBS API or exporter-based checks;
- Linux agent or agent2 deployment for selected servers;
- AdGuard health checks;
- Samba AD DNS/Kerberos checks;
- alert channel and escalation policy.
