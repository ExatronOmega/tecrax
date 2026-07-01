# Basic alerting baseline runbook

This runbook covers the first basic alerting baseline after Grafana, Zabbix and
Wazuh are deployed.

It introduces local alert spools for infrastructure and security events without
claiming final notification routing. The baseline is deliberately conservative:
it does not require SMTP, chat webhooks, GLPI credentials or any external secret.

## Scope

The baseline covers:

- collecting new unresolved Zabbix problems at `Average` severity and above;
- collecting new Wazuh high-security alerts at level `10` and above;
- writing concise local alert records to host-local logs and the system journal;
- running both collectors through systemd timers;
- preserving a clear path to later GLPI, email or other notification routing.

It does not configure external media, paging, email, chat notifications, GLPI
ticket creation, escalation policy, on-call ownership, final incident handling
or compliance reporting.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic collector names;
- severity thresholds;
- host aliases and service roles;
- systemd timer cadence;
- validation summary;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- notification credentials, SMTP passwords and webhook URLs;
- exact private endpoints unless separately approved;
- raw alert payloads that reveal private topology;
- complete protected-endpoint inventory;
- GLPI API tokens or ticket-routing credentials.

## Baseline Model

Use local, host-owned collectors:

- Zabbix collector on the monitoring server:
  - source: active unresolved Zabbix problems;
  - threshold: severity `Average` and above;
  - output: host-local alert log and journal;
  - cadence: every five minutes.

- Wazuh collector on the security monitoring server:
  - source: Wazuh `alerts.json`;
  - threshold: rule level `10` and above;
  - output: host-local alert log and journal;
  - cadence: every five minutes.

This is a bootstrap alerting layer. It proves that critical events can be
extracted and summarized without external credentials. Later gates may replace
or complement this with Zabbix media actions, Wazuh integrations, GLPI tickets,
mail or chat notifications.

## Procedure

### 1. Confirm Existing Signal

Validate before deployment:

- Zabbix already has monitored hosts and active problem generation;
- Wazuh already has enrolled agents and alert files;
- neither system requires secret exposure to read the selected signal source;
- the chosen threshold avoids obvious low-severity noise.

### 2. Deploy Collectors

Install host-local scripts and systemd units:

- `tecrax-zabbix-alert-baseline.service`;
- `tecrax-zabbix-alert-baseline.timer`;
- `tecrax-wazuh-alert-baseline.service`;
- `tecrax-wazuh-alert-baseline.timer`.

The collectors should keep bounded state to avoid repeatedly logging the same
event id.

### 3. Validate

Validate:

- timers are enabled and active;
- one-shot service runs exit successfully;
- Zabbix collector records current `Average+` unresolved problems once;
- a second Zabbix collector run does not duplicate already-seen problems;
- Wazuh collector reports current high-alert count;
- Wazuh central services remain active;
- no credential is written to the collector logs.

## Stop Conditions

Stop before sign-off if any of these are true:

- the collector would require exposing a token, password or webhook URL;
- external notification credentials are not yet operator-owned;
- the collector floods logs with repeated duplicate events;
- a query requires raw private topology to be published;
- deployment would interrupt Zabbix or Wazuh service availability.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `basic-alerting-baseline`;
- Zabbix local collector summary;
- Wazuh local collector summary;
- timer status;
- validation summary;
- explicit non-claims.

Non-claims:

- no final external notification channel;
- no GLPI ticket routing;
- no on-call/escalation policy;
- no tuned alert severity matrix;
- no compliance incident process;
- no full security audit / strong and wide hardening claim.

## Next Gate

After the local alerting baseline is stable, choose the next routing layer:

1. GLPI ticket creation after GLPI deployment;
2. email or chat media after operator-owned credentials are available;
3. Grafana overview panels for current alert status;
4. final alert matrix during the strong and wide hardening stage.
