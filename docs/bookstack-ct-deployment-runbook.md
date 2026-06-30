# BookStack CT deployment runbook

This runbook covers the operator-owned BookStack deployment gate for the Proxmox
stack.

BookStack is the documentation and handoff layer for IT procedures, runbooks,
service notes and operational knowledge. This runbook keeps deployment,
credential rotation, backup and restore proof separate from any future GLPI,
SSO, PKI or final documentation-migration claims.

## Scope

The deployment pass covers:

- creating a dedicated Linux CT for BookStack;
- placing the CT on the data-service storage class;
- installing BookStack from the upstream stable release branch;
- configuring a local database and web service;
- rotating bootstrap application credentials through the operator;
- adding host monitoring;
- adding local PBS and external backup coverage where approved;
- producing a public-safe sign-off.

It does not migrate all documentation, configure SSO/LDAP, claim final HTTPS/PKI
hardening, configure GLPI integration, create a final information architecture
or store BookStack credentials in Tecrax.

## Public and Private Boundary

Safe in public docs and sign-offs:

- service role and target alias;
- CT class and high-level resource shape;
- OS family;
- BookStack source class;
- backup and monitoring status summaries;
- documentation-space structure at a generic level;
- explicit non-claims.

Must remain outside Git and public sign-offs:

- BookStack admin password, database password and app key;
- exact private endpoint addresses unless separately approved;
- SSH keys, known-hosts, fingerprints and local secret paths;
- raw database dumps and uploaded files;
- full private topology or user inventory;
- exported documentation that contains secrets.

## Placement

Recommended public-safe shape:

- deployment class: Proxmox CT;
- OS family: Debian;
- storage class: data-service HDD mirror pool;
- initial sizing: small CPU/memory class and moderate disk;
- service alias: `bookstack-01`;
- operator account follows the environment hard rule: `rexecop`.

A CT is appropriate for the first small-environment deployment because BookStack
is a lightweight PHP application. If the service later needs heavier isolation,
SSO experiments or application-specific restore workflows, it can be promoted
to a VM in a separate migration gate.

## Installation Source

Use the upstream BookStack stable release branch and follow the official manual
installation model:

- PHP compatible web server;
- PHP command line and required extensions;
- MySQL or MariaDB database;
- Composer;
- BookStack `release` branch.

Do not commit `.env`, database dumps, generated app keys or bootstrap
credentials.

## Procedure

### 1. Preflight

Validate before CT creation:

- the selected service address is unused;
- data-service storage has enough free capacity;
- local DNS and NTP are healthy;
- PBS is reachable;
- the operator approves CT deployment for BookStack;
- bootstrap credentials will be rotated after first login.

### 2. Create CT

Create a dedicated CT with static network configuration, local DNS/time
baseline and operator access. Keep credentials outside Git.

For unprivileged CTs, time is inherited from the Proxmox host. If a local
chrony service is present only for source visibility, run it without clock
steering and validate the host NTP path separately.

### 3. Install BookStack

Install the web server, PHP runtime, PHP extensions, MariaDB, Git and Composer
from the operating-system package repositories.

Clone the BookStack stable release branch to the application path. Configure the
environment file with a generated application key and local database
credentials. Run migrations and enable the web service.

### 4. Bootstrap And Rotation

BookStack upstream provides default bootstrap credentials for first login. Treat
them as temporary only. The operator must replace them immediately after first
interactive login.

Do not paste the new credential into Git, chat, sign-offs or runbooks.

### 5. Documentation Structure

Create only a minimal starter structure before broad migration:

- Infrastructure;
- Runbooks;
- Backup and Restore;
- Monitoring and Alerting;
- Security and Incidents;
- Handoff.

Detailed migration can be delegated to a documentation helper model only with a
public-safe handoff and after operator approval.

### 6. Monitoring And Backup

Apply the Linux host onboarding package:

- local time synchronization;
- `zabbix-agent2` active checks;
- host entry in the infrastructure group through an operator-owned Zabbix API
  credential;
- validation of agent and availability checks.

Add local PBS backup coverage. Include the CT in the external base-services
backup job if it is part of the base operational stack.

Run first manual local PBS and external backup proofs before signing off
deployment.

### 7. Restore Proof

Before final documentation-migration claims, restore BookStack to an isolated
temporary target or equivalent controlled path and validate that the application
state and uploaded assets are recoverable.

This restore proof may be a separate gate if first deployment needs to remain
small.

## Validation

Validate:

- CT is running;
- local time synchronization is healthy;
- BookStack web endpoint returns a login page;
- database service is active;
- web service is active;
- BookStack migrations completed;
- operator can log in and rotate bootstrap credentials;
- Zabbix agent baseline is healthy;
- local PBS backup job exists and first manual backup completed;
- external backup coverage exists and first manual backup completed when the CT
  belongs to the base operational stack;
- no secret appears in public Tecrax docs or sign-offs.

## Stop Conditions

Stop before sign-off if any of these are true:

- generated application key, database credential or admin password would be
  exposed;
- service address conflicts with an existing workload;
- upstream source cannot be obtained from the expected release branch;
- BookStack web login does not work;
- bootstrap credentials cannot be rotated by the operator;
- backup coverage cannot be created or first backup fails;
- documentation migration would require exposing secrets to an LLM.

## Sign-Off Shape

Use `docs/operator-signoff-template.md` and include:

- date;
- run class: `bookstack-ct-deployment`;
- service alias and deployment class;
- OS family and broad sizing class;
- BookStack source class;
- monitoring validation summary;
- backup coverage summary;
- bootstrap credential rotation status;
- explicit non-claims.

Non-claims:

- no full documentation migration yet;
- no GLPI integration;
- no SSO/LDAP claim;
- no final HTTPS/TLS hardening or private CA trust claim;
- no one-command disaster recovery claim;
- no compliance documentation completion claim.
