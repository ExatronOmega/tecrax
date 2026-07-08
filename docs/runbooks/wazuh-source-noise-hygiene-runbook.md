# Wazuh source noise hygiene runbook

This runbook covers a bounded Wazuh source-hygiene step before routing Wazuh
signals to a ticket system.

The goal is to reduce high-volume, low-value successful operational telemetry at
the Wazuh source while preserving failures, vulnerabilities, integrity findings,
disk pressure and unknown high-severity alerts.

## Scope

This procedure covers:

- bounded alert summary from `alerts.json`;
- classification into `observe_only`, `backlog`, `ticket_grouped` and
  `ticket_now`;
- manager alert-level baseline;
- shared agent scan cadence baseline;
- local Wazuh rule backup;
- narrowly scoped child rules for selected success-telemetry rules;
- Wazuh manager restart;
- post-change smoke validation.

It does not delete alerts or index data, globally silence Wazuh, suppress
authentication failures, hide vulnerability findings, change endpoint hardening
policy or enable live GLPI routing.

## Public and Private Boundary

Safe in public documentation and sign-offs:

- rule ids;
- routing classes;
- aggregate counts;
- checksums of before/after local rule files;
- restart and smoke status;
- non-claims.

Keep outside Git and public sign-offs:

- raw alert payloads;
- user identifiers from alert payloads;
- private host inventories beyond sanitized aliases;
- credential material;
- Wazuh API credentials, enrollment secrets and tokens.

## Candidate Noise Classes

Only suppress classes that are confirmed to be routine successful telemetry in
the local environment.

Typical candidates:

- PAM session opened/closed success telemetry;
- successful SSH authentication telemetry;
- successful sudo telemetry;
- successful application login telemetry that is already expected and audited
  elsewhere.

Do not suppress by default:

- authentication failures;
- privilege escalation failures;
- malware, rootkit or integrity findings;
- vulnerability findings;
- disk pressure;
- unknown high-level events;
- repeated successful logins that are themselves suspicious.

## Operational Baseline Tuning

Before adding many suppression rules, set a small operational baseline so Wazuh
does not behave like a raw default install.

Recommended first baseline for small Linux infrastructure environments:

- raise manager `log_alert_level` from `3` to `5` if low-level successful
  telemetry is flooding the dashboard;
- keep `jsonout_output` and `alerts_log` enabled;
- keep authentication failures, vulnerabilities, rootcheck, syscheck and disk
  pressure visible;
- use shared agent config to disable scan-on-start for routine scans;
- set syscheck/rootcheck cadence to a predictable daily baseline;
- set SCA cadence to a slower baseline, such as weekly, until final hardening
  policy exists;
- reduce syscollector noise by collecting core inventory while avoiding process
  and browser-extension collection unless explicitly needed;
- use `auto_ignore` for repeated FIM changes instead of suppressing all
  integrity monitoring.

Example shared agent baseline:

```xml
<agent_config>
  <syscheck>
    <disabled>no</disabled>
    <frequency>86400</frequency>
    <scan_on_start>no</scan_on_start>
    <alert_new_files>no</alert_new_files>
    <auto_ignore frequency="10" timeframe="3600">yes</auto_ignore>
    <skip_nfs>yes</skip_nfs>
    <skip_dev>yes</skip_dev>
    <skip_proc>yes</skip_proc>
    <skip_sys>yes</skip_sys>
  </syscheck>

  <rootcheck>
    <disabled>no</disabled>
    <frequency>86400</frequency>
    <skip_nfs>yes</skip_nfs>
  </rootcheck>

  <sca>
    <enabled>yes</enabled>
    <scan_on_start>no</scan_on_start>
    <interval>7d</interval>
    <skip_nfs>yes</skip_nfs>
  </sca>

  <wodle name="syscollector">
    <disabled>no</disabled>
    <interval>24h</interval>
    <scan_on_start>no</scan_on_start>
    <hardware>yes</hardware>
    <os>yes</os>
    <network>yes</network>
    <packages>yes</packages>
    <ports all="no">yes</ports>
    <processes>no</processes>
    <users>yes</users>
    <groups>yes</groups>
    <services>yes</services>
    <browser_extensions>no</browser_extensions>
  </wodle>
</agent_config>
```

Validate shared config before installation:

```sh
/var/ossec/bin/verify-agent-conf -f /path/to/agent.conf
```

## Procedure

### 1. Create a bounded summary

Use a private snapshot outside the repository:

```sh
tail -n 5000 /var/ossec/logs/alerts/alerts.json > /path/outside/repo/wazuh-alerts.json
python scripts/summarize-wazuh-alerts.py /path/outside/repo/wazuh-alerts.json --limit -1
```

Review:

- top rules;
- top agents;
- routing-class split;
- `ticket_now` and `ticket_grouped` candidates.

### 2. Decide suppression scope

Only continue when the noisy rule is:

- high-volume;
- low-value as a standalone ticket;
- successful telemetry rather than a failure;
- still available through normal source logs if deeper audit is needed.

If the rule contains failures, vulnerabilities, disk pressure, syscheck,
rootcheck or unknown high-level activity, keep it visible and route it to
backlog or grouped review instead.

### 3. Back up local rules

Before editing:

```sh
cp -a /var/ossec/etc/rules/local_rules.xml \
  /var/ossec/etc/rules/local_rules.xml.bak-YYYYMMDD-hygiene
sha256sum /var/ossec/etc/rules/local_rules.xml \
  /var/ossec/etc/rules/local_rules.xml.bak-YYYYMMDD-hygiene
```

### 4. Add local child rules

Add child rules in the local id range. Use `level="0"` only for the selected
success-telemetry parent rule ids.

Example:

```xml
<group name="local_noise_hygiene,">
  <rule id="100100" level="0">
    <if_sid>5501</if_sid>
    <description>Local hygiene: suppress routine successful PAM session opened telemetry.</description>
  </rule>
</group>
```

Use a new local rule id for each suppressed parent rule. Keep descriptions
explicit so future audits can see why the rule exists.

### 5. Validate and restart

Validate XML syntax before installation where possible. Then restart the Wazuh
manager:

```sh
systemctl restart wazuh-manager
systemctl is-active wazuh-manager
```

### 6. Smoke test

Trigger one known routine success path, such as a normal SSH login or normal
sudo action. Confirm that the alert count does not increase for the suppressed
success-telemetry rules.

Also confirm that non-suppressed classes still appear when present in the source
summary.

## Rollback

Restore the backup and restart the manager:

```sh
cp -a /var/ossec/etc/rules/local_rules.xml.bak-YYYYMMDD-hygiene \
  /var/ossec/etc/rules/local_rules.xml
systemctl restart wazuh-manager
```

Rollback affects future rule evaluation. It does not delete historical alerts
already stored in Wazuh.

## Sign-Off Shape

Record:

- date;
- run class: `wazuh-source-noise-hygiene`;
- aggregate baseline counts;
- suppressed parent rule ids;
- local child rule ids;
- checksum before and after;
- restart status;
- smoke result;
- remaining backlog;
- rollback path.

Non-claims:

- no deletion of historical alerts;
- no global Wazuh suppression;
- no Wazuh-to-ticket live routing unless separately enabled;
- no compliance readiness claim.
