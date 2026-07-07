# Expected-off monitoring policy runbook

This runbook covers operator-owned monitoring policy for hosts that are
intentionally powered off by default.

It introduces an explicit `expected-off` class for on-demand infrastructure
hosts. It does not enable always-on monitoring, create GLPI tickets, change
Zabbix triggers, power on hosts, generate secrets or document private topology.

## Scope

The policy covers:

- on-demand infrastructure hosts that should normally be stopped;
- private operator context fields such as `expected_power_state: stopped`;
- Zabbix-to-GLPI live-candidate filtering for expected-off hosts;
- backup and restore-proof checks that remain valid even when a host is stopped;
- future alert classes for unexpected power state or missing backup evidence.

The policy does not cover:

- final PKI/CA custody rules;
- application-level secret backup;
- automatic power management;
- broad endpoint availability policy;
- live GLPI ticket creation for every host-down alert;
- Wazuh rule tuning.

## Public And Private Boundary

Safe in public docs and sign-offs:

- the expected-off concept;
- the normalized context field names;
- routing behavior and non-claims;
- validation evidence that a helper excludes expected-off outage events.

Must remain outside Git and public sign-offs:

- private host/IP mappings unless already public-safe;
- API tokens, passwords, private keys and SNMP credentials;
- real alert payloads if they contain protected system or user data;
- CA private material, keystores and passphrases.

## Policy

An expected-off host is an infrastructure host whose healthy baseline is
`stopped`, not `reachable`.

Rules:

- do not treat host-down/unavailable events for expected-off hosts as live GLPI
  ticket candidates;
- do not add expected-off hosts to ordinary always-on availability paging until
  a separate expected-state monitor exists;
- keep VM-level backup and isolated restore-proof evidence for the substrate;
- if the host is powered on for maintenance, validate it with explicit
  on-demand checks;
- future alerting should focus on unexpected state, such as powered-on longer
  than an approved window or missing/stale backup evidence.

## Operator Context Shape

Private operator context may use this public-safe shape:

```yaml
alert_routing:
  zabbix:
    infrastructure_hosts:
      - pve01
      - pki01
    expected_off_hosts:
      - pki01
```

Host inventory may additionally record:

```yaml
hosts:
  pki01:
    expected_power_state: stopped
```

The two lists have different meanings. `infrastructure_hosts` means the host is
part of the infrastructure estate. `expected_off_hosts` means host-down is not
an outage by itself.

## Procedure

### 1. Classify The Host

Confirm the host is intentionally on-demand. Record the expected state in
operator-owned inventory outside Tecrax.

Do not classify ordinary user endpoints as expected-off infrastructure hosts.
Staff laptops and PCs use endpoint rollout/reporting policy instead.

### 2. Configure Alert Routing Context

Add the host alias to `expected_off_hosts` in the private operator alert-routing
context.

Keep any credentials, API URLs and live alert snapshots outside Git.

### 3. Validate Deterministic Filtering

Use the Zabbix shadow collector with private operator context:

```sh
ZABBIX_API_TOKEN=... \
.venv/bin/python scripts/collect-zabbix-problems-for-glpi.py \
  --api-url https://zabbix.example.invalid/api_jsonrpc.php \
  --infra-host-file /path/outside/repo/alert-routing.yaml \
  --live-candidates-only \
  --include-routing-decision
```

Validate that expected-off host-down events do not appear in live-candidate
output. If running without `--live-candidates-only`, validate their routing
reason is `expected-off/on-demand`.

### 4. Validate Host Access Checks

Operator helpers may skip direct SSH access checks for stopped on-demand hosts.
The skip result is valid only when the private inventory explicitly says the
host is expected to be stopped.

### 5. Future Expected-State Alerts

When the stack is ready for the next monitoring iteration, add explicit checks
for:

- expected-off host powered on outside an approved maintenance window;
- expected-off host with missing or stale VM-level backup evidence;
- expected-off host exposing unexpected services;
- PKI/Vaultwarden-class hosts with custody material but no restore proof.

These checks should be deterministic and bounded. AI may summarize evidence or
propose operator actions, but it must not execute infrastructure commands.

## Stop Conditions

Stop before live routing if:

- a host is expected-off only because SSH or monitoring is broken;
- there is no operator-owned inventory entry proving expected state;
- the host is production-critical and should be always reachable;
- backup or restore-proof evidence is missing for a critical substrate;
- the routing output would hide a real outage on an always-on host.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- run class: `expected-off-monitoring-policy`;
- host class and expected state, using aliases only;
- filtering validation summary;
- backup/restore-proof status if applicable;
- future alert classes deferred;
- explicit non-claims.

Non-claims:

- no final Zabbix trigger tuning;
- no live GLPI ticket creation for expected-state changes;
- no automatic power management;
- no secret custody in Tecrax;
- no final PKI/CA security posture.
