# Wazuh backup and restore decision runbook

This runbook records the first backup/export/restore decision for the Wazuh
single-node security monitoring service.

It is intentionally a decision runbook. It does not create snapshots, export
indices, read alerts, dump logs, change retention, alter Wazuh configuration or
perform a restore.

## Scope

The decision covers:

- current Wazuh component shape;
- current VM-level backup coverage;
- whether to add application-aware export now;
- future restore-proof expectations;
- public-safe sign-off shape.

It does not cover:

- Wazuh index snapshots;
- OpenSearch/Wazuh Indexer repository configuration;
- dashboard saved-object exports;
- alert/index retention tuning;
- Wazuh rule tuning;
- Wazuh-to-GLPI live routing;
- broad endpoint rollout.

## Observed Baseline

Current deployment class:

- single-node Wazuh VM;
- Wazuh manager, indexer, dashboard and Filebeat on one VM;
- VM storage on the data-service pool;
- VM-level local PBS backup coverage;
- VM included in the external base-services backup job;
- Linux infrastructure agents already enrolled separately.

Application data classes:

- Wazuh manager state and queues under `/var/ossec`;
- Wazuh Indexer data under `/var/lib/wazuh-indexer`;
- dashboard, indexer and Filebeat configuration under their service-specific
  `/etc` paths;
- generated credentials, certificates and enrollment material remain private.

## Decision

Do not add an application-aware Wazuh export at this stage.

For the current bootstrap/baseline phase, Wazuh recovery confidence is based on:

- local VM-level PBS backup;
- external VM-level base-services backup coverage;
- service health checks after VM boot;
- future isolated VM restore proof before treating Wazuh history as
  application-recoverable.

Rationale:

- Wazuh indices and alerts can contain sensitive security data;
- index snapshots require a repository/custody/retention decision that is not
  yet part of the baseline;
- Wazuh noise and retention policy are still open;
- endpoint rollout is not complete;
- GLPI routing from Wazuh is intentionally deferred until source hygiene and
  rule grouping are stable;
- app-aware export without restore proof would create false confidence.

## Future Application-Aware Options

During hardening or a dedicated Wazuh recovery phase, evaluate:

- Wazuh Indexer/OpenSearch snapshot repository;
- dashboard saved-object export if custom dashboards become operationally
  important;
- selected `/var/ossec` configuration backup;
- agent enrollment/key recovery model;
- retention and deletion policy for security logs;
- isolated restore proof from VM-level backup and, if adopted, index snapshot.

Do not implement these until custody, retention and restore validation are
defined.

## Restore-Proof Expectations

The next restore proof should validate only bounded service health unless a
separate application-restore scope is approved.

Minimum isolated VM restore proof:

- restore the Wazuh VM backup to a temporary isolated VM;
- prevent it from becoming the production Wazuh endpoint;
- validate boot, guest agent and OS time;
- validate manager/indexer/dashboard/Filebeat service status;
- validate local dashboard listener without exposing real alerts;
- validate that production Wazuh remains unchanged;
- remove or retain the temporary VM only by explicit operator decision.

Application-aware proof, if later approved:

- validate index snapshot restore into an isolated target;
- use count/metadata checks only unless protected data handling is approved;
- do not publish alert contents, raw logs, agent keys or dashboard credentials.

## Public And Private Boundary

Safe in public docs and sign-offs:

- VM-level backup coverage status;
- component classes;
- decision to defer app-aware export;
- bounded restore-proof expectations;
- non-claims.

Must remain outside Git and public sign-offs:

- raw Wazuh alerts and logs;
- Wazuh index data;
- agent keys and enrollment secrets;
- dashboard credentials;
- generated certificates and private keys;
- backup repository URLs, credentials and restored data contents.

## Stop Conditions

Stop before application-aware export if:

- Wazuh retention policy is undefined;
- snapshot repository custody is undefined;
- export would include sensitive alerts without handling rules;
- restore target is not isolated;
- operator expects snapshots to replace VM-level backup;
- GLPI routing would be enabled before Wazuh source hygiene.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `wazuh-backup-restore-decision`;
- observed component shape;
- VM-level backup coverage summary;
- application-aware export decision;
- future restore-proof expectation;
- explicit non-claims.

Non-claims:

- no Wazuh index snapshot configured;
- no application-aware restore proof completed;
- no alert contents inspected;
- no Wazuh retention policy finalized;
- no Wazuh-to-GLPI live routing;
- no endpoint rollout completion claim.

## Tecrax Artifact Target

Current target: `L1` public-safe decision runbook.

Future candidates:

- `L3` read-only Wazuh backup/restore status summary;
- `L3` Wazuh retention and index growth summary;
- no L4 Wazuh restore/export mutation before custody, retention and isolated
  restore gates are approved.
