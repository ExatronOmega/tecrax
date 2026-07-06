# Alert source hygiene checkpoint runbook

This runbook covers the alert-source hygiene checkpoint before live GLPI ticket
routing for Zabbix and Wazuh.

The checkpoint exists to tune and classify alert sources before creating tickets.
GLPI must receive actionable work items, not a raw copy of Zabbix problems or
Wazuh SIEM events.

## Scope

The checkpoint covers:

- bounded Zabbix active-problem summary;
- bounded Wazuh alert summary;
- source tuning decisions for noisy triggers/rules;
- routing classes for future GLPI integration;
- explicit non-claims before live ticket creation.

It does not create GLPI tickets, silence Wazuh globally, delete Wazuh/Zabbix
events, disable upstream rules, change production thresholds or claim completed
hardening.

## Routing Classes

Use these classes for the checkpoint:

- `ticket_now` - directly actionable, high-confidence work item;
- `ticket_grouped` - one ticket after grouping/deduplication, such as
  vulnerability findings by CVE/host/package;
- `backlog` - hardening or patch backlog, not an incident ticket;
- `observe_only` - telemetry retained in the source system and optional
  summary reports, not a GLPI ticket.

Raw telemetry stays in Zabbix/Wazuh. The routing class only controls whether the
event becomes a GLPI work item.

## Zabbix Hygiene

Before GLPI routing, inspect:

- active problem counts by severity;
- noisy triggers;
- host groups and tags used for routing;
- trigger severity and dependencies;
- maintenance windows for expected downtime;
- known expected states, such as video retention storage pressure.

Preferred actions:

- fix wrong thresholds or severity at source;
- add dependencies where one root problem creates many symptoms;
- use maintenance windows for planned work;
- keep known expected states visible but avoid repeated ticket floods;
- do not hide true availability or capacity problems just to reduce noise.

## Wazuh Hygiene

Before GLPI routing, inspect:

- top rules, levels, agents and groups;
- authentication success/failure patterns;
- sudo/PAM operational noise;
- SCA/rootcheck/syscheck findings;
- vulnerability-detector bursts and stale/false-positive candidates;
- disk, malware, privilege, auth-failure and integrity events.

Initial routing guidance:

- PAM/SSH successful login and normal sudo success: `observe_only`;
- isolated authentication failures: `ticket_grouped` only after thresholding;
- vulnerability-detector high findings: `ticket_grouped`;
- SCA/rootcheck benchmark findings: `backlog`;
- syscheck/config/package changes during operator work: `observe_only` or
  `backlog` until tuned;
- disk pressure and direct service-impact findings: `ticket_now`.

## Helper

Use the public-safe helper against a bounded snapshot or local alerts file:

```sh
python scripts/summarize-wazuh-alerts.py /path/to/alerts.json --limit 5000
```

The helper prints aggregate counts, top rules and routing classes. It does not
need Wazuh credentials and does not print raw payloads.

On a Wazuh server, create a bounded snapshot first if needed:

```sh
tail -n 5000 /var/ossec/logs/alerts/alerts.json > /tmp/wazuh-alerts-snapshot.json
python scripts/summarize-wazuh-alerts.py /tmp/wazuh-alerts-snapshot.json
rm -f /tmp/wazuh-alerts-snapshot.json
```

## Stop Conditions

Stop before live GLPI routing if:

- Wazuh/Zabbix alert volume would create ticket floods;
- high-severity rules are not understood;
- vulnerability alerts are repeating without grouping;
- source tuning would hide true incidents;
- the proposed routing needs raw private payloads or secrets;
- duplicate/grouping behavior is not validated in shadow mode.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- run class: `alert-source-hygiene-checkpoint`;
- Zabbix active-problem summary;
- Wazuh top-rule summary;
- source tuning decisions;
- routing decisions by class;
- remaining backlog;
- explicit non-claims.

Non-claims:

- no GLPI live ticket routing;
- no completed incident-response procedure;
- no completed hardening;
- no source rules disabled unless separately documented and approved;
- no secret custody in Tecrax.
