# PKI HTTPS rollout planning runbook

This runbook covers the planning baseline for future HTTPS rollout across
internal administrative services.

It is intentionally a planning runbook. It does not generate certificates, CSRs,
private keys, CA material, trust stores, reverse-proxy configuration or live
service TLS changes.

## Scope

The planning baseline covers:

- service inventory for future HTTPS coverage;
- internal FQDN and SAN naming pattern;
- rollout order and blast-radius control;
- service-local TLS versus reverse-proxy decision criteria;
- trust-root distribution dependencies;
- rollback and stop conditions;
- private certificate registry planning entries.

It does not cover:

- root or intermediate CA creation;
- certificate issuance;
- service reconfiguration;
- trust-root deployment;
- DNS mutation;
- firewall mutation;
- user endpoint rollout;
- compliance sign-off.

## Public And Private Boundary

Safe in public docs and sign-offs:

- service classes and generic rollout order;
- FQDN naming template;
- decision criteria;
- non-secret registry field names;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- CA private keys and passphrases;
- issued private certificates when they expose private host details;
- service private keys and keystores;
- exact private inventory if not redacted;
- admin passwords, API tokens and session cookies;
- raw reverse-proxy configs containing private targets or credentials.

## Target Services

Initial administrative services to plan for HTTPS:

- Proxmox VE;
- Proxmox Backup Server;
- Vaultwarden;
- PKI Center;
- Zabbix;
- Grafana;
- Wazuh;
- GLPI;
- BookStack;
- AdGuard Home.

Do not migrate all services at once. Each service needs a rollback path and a
bounded validation check.

## Naming Baseline

Preferred internal service naming pattern:

```text
<service>.mbp.infra.lan
```

Examples:

```text
proxmox.mbp.infra.lan
pbs.mbp.infra.lan
vault.mbp.infra.lan
pki.mbp.infra.lan
zabbix.mbp.infra.lan
grafana.mbp.infra.lan
wazuh.mbp.infra.lan
glpi.mbp.infra.lan
bookstack.mbp.infra.lan
adguard.mbp.infra.lan
```

Rules:

- every certificate must use explicit SANs;
- service aliases should be human-readable and stable;
- raw IP SANs are not the default for administrative services;
- wildcard certificates are deferred until there is a specific approved reason;
- DNS authority and reverse lookup cleanup should be coordinated with the later
  IPAM/naming cleanup stage.

## Rollout Order

Recommended order:

1. Non-critical dashboard/documentation services with easy rollback:
   Grafana, BookStack.
2. Helpdesk/monitoring services:
   GLPI, Zabbix.
3. DNS filtering and backup interfaces:
   AdGuard, PBS.
4. Security-sensitive services:
   Vaultwarden, Wazuh.
5. Root-of-trust/control-plane services:
   Proxmox VE, PKI Center.

Rationale:

- learn on lower-risk services first;
- avoid locking the operator out of Proxmox/PBS early;
- keep Vaultwarden and PKI behind stronger custody and recovery gates;
- keep Proxmox root-of-trust hardening tied to final trusted custody.

## TLS Placement Decision

Use service-native TLS when:

- the service has a clear supported certificate import path;
- rollback is simple and documented;
- the service is security-sensitive or already exposes its own TLS endpoint.

Use a reverse proxy when:

- the service lacks clean TLS support;
- multiple lightweight web apps can share a controlled ingress pattern;
- rollback can be performed without touching the backend application;
- private backend exposure can be restricted.

Do not introduce a single reverse proxy as a new critical dependency without
backup, monitoring, restore proof and owner clarity.

## Trust Distribution Dependencies

Windows domain endpoints:

- trust-root distribution should use AD/GPO after CA custody is approved;
- start with a pilot OU before broad staff endpoint rollout;
- record rollback and verification steps.

Linux VM/CT hosts:

- trust store updates should be package/config-management controlled;
- start with one non-critical host;
- record service validation after trust update.

Network devices and appliances:

- defer trust import until device-specific behavior is known;
- do not push trust roots through ad hoc scripts without backup and rollback.

## Private Registry Planning

The private certificate registry may contain planned entries before certificate
issuance. Planned entries are metadata only and must not contain private keys,
CSRs, passphrases, keystores or issued certificates.

Suggested status values:

- `planned`;
- `csr_pending`;
- `issued`;
- `deployed`;
- `renewal_due`;
- `revoked`;
- `retired`.

## Validation

The planning gate passes when:

- target service list exists;
- FQDN/SAN naming template is documented;
- rollout order is documented;
- trust-root distribution dependencies are documented;
- private registry has planned metadata entries or a clear empty-template state;
- no live TLS or trust mutation was performed.

## Stop Conditions

Stop before execution if:

- CA custody is not approved;
- offline/root recovery is not defined;
- target service backup/restore proof is missing;
- operator access could be locked out;
- DNS ownership is unclear;
- trust-root distribution rollback is unclear;
- service private keys would be exposed to AI, Git, chat or public logs.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `pki-https-rollout-planning`;
- service classes included;
- naming template;
- rollout order;
- registry status;
- open hardening gates;
- explicit non-claims.

Non-claims:

- no certificates generated;
- no CSRs generated;
- no private keys generated;
- no trust root distributed;
- no service HTTPS migration;
- no reverse-proxy deployment;
- no compliance certification.

## Tecrax Artifact Target

Current target: `L1` public-safe planning runbook plus private planned
certificate registry metadata.

Future candidates:

- `L3` HTTPS readiness summary per service;
- `L3` certificate expiry and trust-root distribution status summaries;
- `L4` service certificate deployment only after custody, rollback and hardening
  gates are approved.
