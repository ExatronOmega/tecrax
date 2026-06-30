# Wazuh VM deployment runbook

This runbook covers the operator-owned deployment gate for Wazuh as the security
monitoring layer in the Proxmox environment.

It is not an active Tecrax mutation and does not add a Wazuh administration
connector. Tecrax records the deployment boundary, validation shape and
public-safe sign-off expectations while keeping Wazuh credentials, agent
enrollment secrets, certificates and private topology outside Git.

## Scope

The deployment pass covers:

- creating a dedicated VM for Wazuh;
- placing the VM on the data-service storage class;
- installing the Wazuh central components as a single-node baseline;
- validating service health, DNS, time sync and reboot behavior;
- adding Zabbix host monitoring for the Wazuh VM;
- adding PBS VM-level backup coverage;
- producing a public-safe sign-off.

It does not deploy endpoint agents broadly, tune all detection rules, configure
final alert routing, integrate Wazuh into Grafana, create compliance reports,
enable SSO, or claim disaster-recovery coverage.

## Public and Private Boundary

Safe in public docs and sign-offs:

- generic target aliases and service roles;
- deployment form: VM;
- broad sizing class;
- OS family;
- Wazuh major line;
- bounded service status;
- backup status summary;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- real addresses, host fingerprints, key paths and local target catalogs;
- dashboard passwords, API credentials, enrollment secrets and recovery material;
- generated Wazuh password archives;
- TLS private keys and certificate custody material;
- raw logs, screenshots or command output that reveal private topology;
- complete protected-endpoint inventory until classified as safe;
- backup repository URLs and backup contents.

## Placement

Recommended public-safe shape:

- deployment class: Proxmox VM;
- OS family: Ubuntu LTS from an upstream cloud image;
- storage class: data-service HDD mirror pool;
- disk size: 160 GB at initial deployment;
- CPU and memory: 4 vCPU, 8 GiB RAM for the first small-environment baseline;
- hostname alias: `wazuh01`;
- operator account follows the environment hard rule: `rexecop`.

Prefer a VM over a CT for this service. Wazuh combines security ingestion,
indexing and a dashboard. A VM gives the service a normal kernel boundary,
simpler package behavior and cleaner PBS restore semantics.

## Version Choice

Use the current supported Wazuh quickstart line unless there is an explicit
reason to do a step-by-step distributed deployment. At the time this runbook was
written, the operator choice for this environment is:

```text
Wazuh line: 4.14 quickstart
Deployment: single-node/all-in-one central components
OS family: Ubuntu 24.04 LTS
```

After installation, disable the Wazuh package repository until an intentional
upgrade window is planned. Accidental SIEM upgrades are not acceptable during
the initial infrastructure rollout.

## Installation Source

Use primary upstream sources:

- Ubuntu cloud image from the official Ubuntu cloud image distribution;
- Wazuh installation assistant from the official Wazuh package endpoint;
- Wazuh documentation as the primary install reference.

The Wazuh quickstart uses an upstream installation assistant. Run it only from
the expected official endpoint and store its generated credential material on
the target VM with restricted permissions. Do not print generated passwords into
chat, public sign-offs, Git history or raw command transcripts.

## Deployment Procedure

### 1. Preflight

Validate before VM creation:

- the selected service address is unused;
- Proxmox storage has enough free capacity;
- PBS is reachable;
- DNS authority model is healthy;
- local NTP service is healthy;
- the Ubuntu cloud image has a known source;
- operator has break-glass console access.

### 2. Create the VM

Create a dedicated VM with cloud-init or an equivalent deterministic install
path. Enable QEMU guest agent and serial console. Set the static network
configuration through operator-owned Proxmox metadata.

The VM should use the local DNS/time model:

- DNS resolver follows the AD/AdGuard authority decision for infrastructure
  servers;
- NTP client uses the local Proxmox time source.

### 3. Prepare the OS

On first boot:

- validate SSH as `rexecop`;
- validate passwordless sudo if automation will continue through that account;
- install and enable QEMU guest agent;
- update base packages;
- configure chrony or equivalent NTP client to use the local time source;
- set a predictable hostname;
- keep any local key paths and known-hosts material outside Git.

### 4. Install Wazuh

Install Wazuh central components using the official assisted quickstart path.
Capture installer logs to a root-owned location on the VM. Do not print or copy
generated credentials to public artifacts.

After installation:

- verify the Wazuh dashboard endpoint returns HTTPS;
- verify Wazuh manager, indexer and dashboard services are active;
- verify generated password archives are present only in restricted local
  custody;
- disable the Wazuh apt repository to prevent accidental upgrades;
- record only public-safe service status in the sign-off.

### 5. Validate

Validate after deployment:

- VM boots and guest agent reports;
- SSH as `rexecop` works;
- local NTP source is selected;
- Wazuh manager service is active;
- Wazuh indexer service is active;
- Wazuh dashboard service is active;
- Wazuh dashboard web UI is reachable through the operator-approved path;
- DNS can resolve base infrastructure names;
- no secret appears in public Tecrax docs or sign-offs.

### 6. Reboot Proof

Reboot the VM once before sign-off. After reboot, validate again:

- network returns;
- SSH as `rexecop` works;
- guest agent is reachable;
- local NTP source is selected;
- Wazuh services return automatically;
- Wazuh dashboard is reachable.

### 7. Monitoring And Backup

Add the Wazuh VM to the existing Linux host monitoring baseline after the service
is healthy. This is host-level monitoring only and does not mean Wazuh agents
have been deployed to protected endpoints.

Add a PBS VM-level backup job for the Wazuh VM after the stack is healthy. Wazuh
state is index-backed, so a later gate should decide whether additional
application-aware export, snapshot or restore procedures are needed before
treating indexed security history as recoverable at application level.

## Stop Conditions

Stop before sign-off if any of these are true:

- service address conflict or unresolved stale gateway binding;
- DNS authority model is unhealthy;
- local NTP source is unavailable;
- Wazuh installer source cannot be verified as the official endpoint;
- generated credentials would be exposed to Git, chat or public logs;
- Wazuh services do not return after reboot;
- PBS is unavailable and no alternate backup path is approved;
- evidence would require publishing secrets, raw topology or host fingerprints.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- run class: `wazuh-vm-deployment`;
- target alias: `wazuh01`;
- deployment form;
- broad VM sizing;
- OS family;
- Wazuh major line;
- Wazuh service health summary;
- NTP/DNS validation summary;
- reboot proof summary;
- monitoring and backup status;
- explicit non-claims.

Non-claims:

- no broad endpoint-agent deployment yet;
- no final alerting policy;
- no Grafana datasource yet;
- no tuned detection policy;
- no SSO claim;
- no application-aware Wazuh restore proof yet;
- no external disaster-recovery copy beyond approved VM backup coverage.

## Next Gate

After the Wazuh VM is deployed and signed off:

1. Rotate or place Wazuh admin credentials into operator-owned custody.
2. Add first low-risk Wazuh agents deliberately.
3. Add Wazuh as a direct Grafana datasource or integration path.
4. Configure basic alerting after Grafana and Wazuh are both stable.
