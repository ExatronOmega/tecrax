# AdGuard Home deployment runbook

This runbook covers the operator-owned deployment gate for AdGuard Home as the
filtering and forwarding DNS layer in the Proxmox environment.

It is not an active Tecrax profile intent and does not add a DNS-management,
DHCP-management or AdGuard API connector. It documents a bounded deployment
sequence that preserves Samba AD DNS authority and keeps DHCP ownership outside
Tecrax.

## Scope

The deployment pass covers:

- creating a small AdGuard Home workload;
- installing AdGuard Home as a system service;
- preserving the operator-approved reserved service address;
- keeping Samba AD DNS authoritative for the AD domain;
- keeping DHCP owned by the security gateway;
- validating DNS forwarding behavior;
- PBS backup and public-safe sign-off.

It does not migrate DHCP scopes, change the DHCP authority configuration, migrate
clients, configure production filtering policy in detail, create user accounts,
or store AdGuard web credentials in Tecrax.

## Authority Model

Approved DNS model:

```text
AD-joined clients -> AD DNS -> AdGuard -> upstream internet DNS
Non-AD clients    -> AdGuard -> upstream internet DNS
AdGuard           -> AD DNS only for the AD domain and selected reverse zones
```

AdGuard is filtering/forwarding DNS. It is not authoritative for the AD domain
and must not replace Samba AD DNS service records.

## DHCP Boundary

DHCP is owned by an external security gateway. Tecrax and this runbook do not
modify DHCP scopes, reservations, leases or DNS options.

Later, after AdGuard is validated:

- AD-client DHCP scopes should hand out AD DNS;
- non-AD, IoT and guest DHCP scopes may hand out AdGuard;
- exact scopes and reservations remain private operator material.

## Placement

AdGuard Home should run as a lightweight critical DNS workload.

Recommended public-safe shape:

- deployment class: Proxmox CT or small VM;
- OS family: Debian;
- storage class: SSD-backed critical-service pool;
- small CPU and memory allocation;
- static private address reserved by the operator;
- operator account follows the environment hard rule: `rexecop`;
- no Docker dependency unless a later boundary decision requires it.

## Installation Source

Use an official AdGuard Home release package. The documented upstream method is
to unpack the release archive and install the service with:

```text
./AdGuardHome -s install
```

Do not pipe arbitrary installer scripts into a root shell in this baseline pass.
Verify the downloaded archive at least by transport source, version output and
service health. Add stronger release checksum/signature verification later if it
becomes available in the operator workflow.

## Initial Configuration

The first-run web setup requires operator-owned credentials. The operator enters
the web admin username/password manually through the AdGuard setup UI or another
interactive channel outside LLM visibility.

Recommended initial behavior:

- web setup listens on the temporary first-run port;
- DNS service listens on the reserved service address after setup;
- default upstream DNS is temporary until the operator chooses final upstreams;
- conditional forwarding for the AD domain points to Samba AD DNS;
- query logging and retention are conservative until storage/monitoring policy
  is decided.

Do not paste web admin passwords, recovery material or exported configuration
containing secrets into Tecrax.

## Validation

Validate after setup:

- workload boots automatically;
- AdGuard service is active;
- AdGuard web interface is reachable through the operator-approved path;
- plain DNS on port 53 responds;
- internet names resolve through AdGuard;
- AD domain names are conditionally forwarded to Samba AD DNS;
- Samba AD SRV records still resolve through AD DNS;
- no forwarding loop exists;
- PBS backup of the workload completes successfully.

## Stop Conditions

Stop if any of these are true:

- the reserved AdGuard address conflicts with an existing service;
- Samba AD DNS is not healthy;
- AdGuard would become authoritative for the AD domain;
- DNS forwarding creates a loop;
- DHCP-authority changes are required before AdGuard validates;
- AdGuard web admin credentials would need to be exposed to LLM/tooling;
- PBS is unavailable and no alternate backup path is approved.

## Sign-Off Shape

Use `../operator-signoff-template.md` and include:

- date;
- run class: `adguard-home-deployment`;
- target alias: `adguard-01`;
- deployment class;
- OS family and broad sizing class;
- service health summary;
- DNS validation summary;
- DHCP non-claim;
- backup status;
- explicit non-claims.

Non-claims:

- no DHCP migration;
- no production client migration;
- no DHCP-authority configuration change;
- no complete filtering-policy tuning;
- no AdGuard API connector;
- no secret custody in Tecrax;
- no external disaster-recovery copy.

## Next Gate

After AdGuard is deployed and validated, update Samba AD DNS forwarding to point
to AdGuard and then plan DHCP-authority changes as a separate operator-owned
network-gateway step.
