# Windows AD pilot endpoint baseline

This runbook covers a small, operator-owned baseline for the first Windows
endpoint pilot before joining a workstation to an Active Directory domain. It is
intended for one or two test laptops, not broad endpoint rollout.

The runbook is public-safe. Keep real addresses, SSH key paths, host
fingerprints, user names, domain credentials and local inventory outside the
repository.

## Scope

Covered:

- verify SSH/PowerShell access to a Windows Pro endpoint;
- collect bounded endpoint baseline facts;
- apply an operator-approved endpoint hostname;
- optionally pin the pilot endpoint DNS server to the AD DNS resolver;
- optionally pin the pilot endpoint time source to the local infrastructure NTP
  source;
- validate AD DNS discovery before domain join;
- record that a reboot is required after rename.

Not covered:

- domain join credentials;
- automatic domain join;
- user data migration;
- GPO design;
- Zabbix/Wazuh endpoint rollout;
- WinRM/HTTPS hardening;
- production DHCP/DNS changes on the security gateway;
- broad endpoint rollout.

## Naming

Existing Proxmox VM/CT/service names do not need to be renamed if they are
already clear and stable. The endpoint naming template is for user devices and
edge devices.

Use this public template:

```text
ORG-<TYPE>-<NNN>
```

Recommended type tokens:

```text
LT   laptop
PC   desktop
PRN  printer
CAM  camera
SW   switch
FW   firewall
```

Examples:

```text
ORG-LT-001
ORG-LT-002
ORG-PC-001
ORG-PRN-001
```

The real organization prefix is operator-owned deployment data. Do not commit a
private site prefix or endpoint inventory if it identifies the environment.

## Prerequisites

- Windows Pro or Enterprise. Windows Home must be upgraded before AD join, GPO
  rollout or endpoint-agent deployment.
- OpenSSH Server installed and running on the endpoint.
- A temporary local operator account with administrative rights for the pilot.
- Public-key login configured for that account.
- Operator-owned SSH private key outside the repository.
- Operator-owned `known_hosts` outside the repository with strict host checking.
- The endpoint connected to a test/user VLAN where AD DNS and the local NTP
  source are reachable.
- Explicit operator approval before any `--apply` run.

Do not store local admin passwords, domain admin credentials, private SSH keys,
host fingerprints, real laptop serial numbers or private inventory in Git.

## Preflight

From an operator workstation, verify SSH reachability using private paths outside
the repository:

```bash
ssh -i /path/outside/repo/windows-pilot-key \
  -o IdentitiesOnly=yes \
  -o BatchMode=yes \
  -o StrictHostKeyChecking=yes \
  -o UserKnownHostsFile=/path/outside/repo/known_hosts \
  local-admin@windows-endpoint.example.invalid whoami
```

Run the helper in dry-run mode first:

```bash
scripts/prepare-windows-ad-pilot-endpoint.sh \
  --host windows-endpoint.example.invalid \
  --user local-admin \
  --identity-file /path/outside/repo/windows-pilot-key \
  --known-hosts /path/outside/repo/known_hosts \
  --target-name ORG-LT-001 \
  --interface-alias Ethernet \
  --dns-server ad-dns.example.invalid \
  --ntp-server ntp.example.invalid \
  --domain ad.example.invalid
```

Dry-run must not rename the endpoint, write DNS settings, write NTP settings or
restart services.

## Apply

After reviewing dry-run output, apply the baseline:

```bash
scripts/prepare-windows-ad-pilot-endpoint.sh \
  --apply \
  --host windows-endpoint.example.invalid \
  --user local-admin \
  --identity-file /path/outside/repo/windows-pilot-key \
  --known-hosts /path/outside/repo/known_hosts \
  --target-name ORG-LT-001 \
  --interface-alias Ethernet \
  --dns-server ad-dns.example.invalid \
  --ntp-server ntp.example.invalid \
  --domain ad.example.invalid
```

Expected effects:

- endpoint rename is scheduled if the current name differs from `--target-name`;
- DNS server list is set on the selected interface if `--dns-server` is passed;
- Windows Time is configured to use `--ntp-server` if provided;
- AD DNS root and LDAP SRV lookup are attempted if `--domain` is provided;
- the helper reports whether a reboot is required.

The rename takes effect only after reboot. Reboot timing remains an operator
decision.

## Validation

After reboot, rerun dry-run and confirm:

- hostname matches the approved endpoint name;
- Windows edition is Pro or Enterprise;
- endpoint is still outside the domain until the operator begins the AD join
  step;
- selected interface has the approved DNS server;
- Windows Time source is the approved local NTP source;
- AD DNS root and `_ldap._tcp.dc._msdcs.<domain>` resolve through AD DNS.

## Rollback

Before domain join:

- rename the endpoint back to its previous local hostname if needed;
- restore DNS to DHCP on the interface:

```powershell
Set-DnsClientServerAddress -InterfaceAlias Ethernet -ResetServerAddresses
```

- restore Windows Time to the normal local policy if needed;
- remove temporary SSH access when the pilot no longer requires it.

After domain join, rollback must be treated as an AD endpoint operation and
should include computer-account cleanup, DNS cleanup and GPO impact review.

## Future Tecrax intent

This helper is a staging artifact, not yet an active profile intent. A future
bounded intent such as `prepare_windows_ad_pilot_endpoint` should split:

- Tecrax: endpoint-domain vocabulary, facts contracts, validation rules and
  finding taxonomy;
- GovEngine: admission, constraints and approval requirements;
- RExecOp: generic execution lifecycle and connector dispatch;
- SCLite: canonical evidence, receipts and verification records.

The future intent must still avoid domain credentials and private topology in
public artifacts.
