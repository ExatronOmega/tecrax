# Wazuh agent baseline runbook

This runbook covers the first Wazuh agent baseline for Linux infrastructure
hosts in the Proxmox deployment.

It extends the Wazuh central deployment with endpoint telemetry from the current
server stack. It does not deploy user PC/laptop agents, tune detection policy,
configure final alert routing, or turn Tecrax into a Wazuh administration
connector.

## Scope

The baseline covers:

- installing `wazuh-agent` on current Linux infrastructure hosts;
- enrolling agents to the Wazuh manager;
- using explicit host aliases matching the service inventory;
- validating active agent status from the Wazuh manager;
- disabling the Wazuh package repository after installation to prevent
  accidental upgrades outside a planned maintenance window;
- recording that future Linux hosts should receive the Wazuh agent as part of
  the mandatory onboarding package.

It does not cover Windows endpoint deployment, broad user-device rollout, final
alert routing, Grafana datasource integration, custom rules or compliance
reporting.

## Public and Private Boundary

Safe in public docs and sign-offs:

- host aliases and service roles;
- package name and product major line;
- manager/agent model;
- active/inactive count summaries;
- validation summary;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- enrollment passwords, API credentials and dashboard credentials;
- exact private endpoint addresses unless separately approved;
- generated agent keys;
- raw Wazuh API payloads containing topology or credentials;
- complete user endpoint inventory until classified as safe;
- shell history containing secrets.

## Baseline Model

Use `wazuh-agent` enrolled to the Wazuh manager for current Linux
infrastructure hosts.

Reasons:

- the Wazuh manager becomes the security monitoring authority for endpoint
  telemetry;
- every infrastructure host receives a consistent baseline before user endpoints
  are added;
- host aliases remain explicit and deterministic;
- Wazuh package repositories are disabled after installation, keeping upgrades
  intentional.

The Wazuh manager host itself is represented by the local manager/server agent
entry and should not be duplicated as a separate remote agent unless the operator
explicitly chooses that model.

## Mandatory New-Host Onboarding Package

Every new Linux infrastructure host should get this baseline package before
being treated as a normal managed workload:

- time synchronization configured and verified;
- DNS resolver/search baseline configured and verified;
- backup eligibility decision recorded;
- Zabbix host monitoring installed and registered where applicable;
- Wazuh agent installed and enrolled where applicable;
- service alias added to the monitoring/security inventory;
- public-safe sign-off or private operator note created, depending on
  sensitivity.

This package is an operator workflow. It is not yet an active Tecrax mutation
intent.

## Procedure

### 1. Confirm Inventory

Confirm the selected infrastructure host aliases before installing agents. Avoid
creating duplicate Wazuh agents when a host was already enrolled.

### 2. Install Agent

Install `wazuh-agent` from the official Wazuh package repository or another
operator-approved source.

Set deployment metadata through deterministic installer variables or an
equivalent reviewed configuration path:

- manager endpoint;
- agent name matching the selected service alias;
- optional agent group only if the group is already approved.

Enable and start the `wazuh-agent` service.

### 3. Disable Package Repository

After the package is installed, disable the Wazuh package repository on the
endpoint. Wazuh upgrades should happen in an explicit maintenance window, not as
a side effect of generic OS updates.

### 4. Validate

Validate:

- package is installed;
- service is enabled and active;
- Wazuh manager lists the agent under the expected alias;
- agent status is `Active`;
- Wazuh package repository is disabled on the endpoint;
- no secret appears in public Tecrax docs or sign-offs.

## Stop Conditions

Stop before sign-off if any of these are true:

- agent hostname would not match the service alias;
- enrollment secret or generated key would be exposed to Git, shell output or
  chat;
- the host cannot reach the Wazuh manager agent ports;
- agent status does not become active after a reasonable wait;
- package installation would require changing unrelated security policy;
- the Wazuh repository remains enabled after installation.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- run class: `wazuh-agent-baseline`;
- selected host aliases;
- package and product line;
- Wazuh manager active-agent summary;
- repository-disabled summary;
- onboarding package update;
- explicit non-claims.

Non-claims:

- no user PC/laptop rollout yet;
- no Windows agent coverage yet;
- no final alert routing;
- no Grafana Wazuh datasource;
- no tuned detection policy;
- no SSO claim.

## Next Gate

After infrastructure agents are stable, continue with one of:

1. first user endpoint rollout plan;
2. Wazuh to Grafana integration path;
3. basic alerting after Grafana and Wazuh are both stable.
