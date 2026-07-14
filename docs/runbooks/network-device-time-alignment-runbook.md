# Network-device time, NTP and DST alignment

This runbook covers a bounded correction of time presentation on managed network
devices after read-only evidence has proved that UTC/NTP synchronization is healthy
but the configured time zone or daylight-saving rule is wrong.

It does not authorize a generic network-device configuration passthrough. Each live
device still requires an explicit target scope, a pre-change backup, vendor-specific
commands and post-change validation before startup configuration is written.

## Required pre-state

- Confirm the authoritative local NTP source and its own upstream synchronization.
- Compare UTC epoch, displayed local time, configured zone/DST and NTP status. A
  one-hour display difference with a healthy NTP offset is a zone/DST problem, not
  NTP drift.
- Record the current time and NTP configuration without dumping unrelated secrets.
- Create an encrypted configuration export outside the device and verify its
  checksum and decryptability.
- Define the exact rollback commands before entering configuration mode.

## Target policy

- Infrastructure NTP transports UTC. Do not compensate for a local-time display
  problem by changing the clock or NTP epoch.
- Devices that display Polish local time use CET (`UTC+01:00`) plus the European
  recurring CEST rule (`UTC+02:00` in summer).
- Prefer a vendor-provided Europe/Central-European zone or predefined European DST
  rule over a manually maintained calendar when the device supports it.
- The approved local NTP service is primary. An existing, separately approved source
  may remain secondary when removing it is outside the authorized scope.

## Bounded vendor patterns

The commands below document the accepted command shapes. Replace NTP placeholders
from private operator context and confirm every command with the live device help.

### Hillstone

Use the vendor zone that explicitly includes Warsaw:

```text
configure
clock zone central-european
exit
show clock
show ntp status
```

Do not save unless the displayed local time is correct and the last NTP sync is
successful. Roll back to the exact zone captured in the pre-state if validation
fails.

### HPE V1910 / Comware 5

Comware 5 requires a base zone and a separate repeating summer-time rule:

```text
system-view
clock timezone CET add 01:00:00
clock summer-time CEST repeating 02:00:00 2000 March last Sunday 03:00:00 2000 October last Sunday 01:00:00
return
display clock
display ntp-service status
display ntp-service sessions
```

The year is the recurrence baseline for this legacy CLI. A time-zone/DST change can
temporarily reset NTP status; wait for `synchronized` before saving. Keep the legacy
full-CLI unlock exclusively in runtime secret custody and suppress it from output.

### TP-Link TL-SG2452

Use the existing private values for the NTP endpoints:

```text
configure
system-time ntp UTC+01:00 <primary-local-ntp> <approved-secondary-ntp> <fetching-rate>
system-time dst predefined Europe
exit
```

Validate the bounded `system-time` lines from running configuration and prove that
the primary local NTP server observed a request from the switch. Save with the
vendor-supported running-to-startup copy only after both checks pass.

## Validation gate

Before saving startup configuration, require all applicable checks:

- displayed time matches `Europe/Warsaw`;
- NTP state is synchronized or the device has made a successful query to the
  approved primary source;
- UTC/reference time remains correct;
- no unrelated configuration line changed;
- management access still works from the approved operator host.

After saving, reconnect and repeat the read-only clock/NTP checks. Keep the encrypted
pre-change export as rollback evidence.

## Stop conditions

Stop without saving and use the predeclared rollback if:

- the CLI syntax or DST transition semantics are ambiguous;
- NTP does not return to a healthy state within the device's normal polling window;
- the device would require a reboot, reset, firmware change or firewall-policy
  modification;
- validation would require exposing a credential or full unredacted configuration;
- the change affects VLANs, ports, routing, DHCP, DNS, SNMP or forwarding policy.

## Known validation gaps

Powered-off endpoints must be checked when they return. Systems excluded from access
remain explicit non-claims; do not infer their time-zone or NTP state from neighboring
devices.
