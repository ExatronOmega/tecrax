#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  prepare-windows-ad-pilot-endpoint.sh [--apply]
    --host HOST --user USER --identity-file PATH --known-hosts PATH
    [--target-name NAME] [--interface-alias NAME]
    [--dns-server SERVER[,SERVER...]]
    [--ntp-server SERVER]
    [--domain DOMAIN]

Public-safe operator helper for a Windows AD pilot endpoint baseline.

Defaults to dry-run. The --apply flag is required before any endpoint mutation.
Secrets, private keys, host fingerprints, real inventory and domain credentials
must stay outside the repository.
EOF
}

apply=false
host=""
user=""
identity_file=""
known_hosts=""
target_name=""
interface_alias="Ethernet"
dns_servers=""
ntp_server=""
domain=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      apply=true
      shift
      ;;
    --host)
      host="${2:-}"
      shift 2
      ;;
    --user)
      user="${2:-}"
      shift 2
      ;;
    --identity-file)
      identity_file="${2:-}"
      shift 2
      ;;
    --known-hosts)
      known_hosts="${2:-}"
      shift 2
      ;;
    --target-name)
      target_name="${2:-}"
      shift 2
      ;;
    --interface-alias)
      interface_alias="${2:-}"
      shift 2
      ;;
    --dns-server)
      dns_servers="${2:-}"
      shift 2
      ;;
    --ntp-server)
      ntp_server="${2:-}"
      shift 2
      ;;
    --domain)
      domain="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

require_value() {
  local name="$1"
  local value="$2"
  if [[ -z "$value" ]]; then
    echo "Missing required argument: $name" >&2
    usage >&2
    exit 2
  fi
}

require_value "--host" "$host"
require_value "--user" "$user"
require_value "--identity-file" "$identity_file"
require_value "--known-hosts" "$known_hosts"

if [[ ! -f "$identity_file" ]]; then
  echo "Identity file does not exist: $identity_file" >&2
  exit 2
fi

if [[ ! -f "$known_hosts" ]]; then
  echo "known_hosts file does not exist: $known_hosts" >&2
  exit 2
fi

ps_quote() {
  local value="$1"
  value=${value//\'/\'\'}
  printf "'%s'" "$value"
}

ps_string_array_from_csv() {
  local csv="$1"
  if [[ -z "$csv" ]]; then
    printf '@()'
    return
  fi

  local first=true
  local out='@('
  local item
  IFS=',' read -r -a items <<<"$csv"
  for item in "${items[@]}"; do
    item="${item#"${item%%[![:space:]]*}"}"
    item="${item%"${item##*[![:space:]]}"}"
    [[ -z "$item" ]] && continue
    if [[ "$first" == true ]]; then
      first=false
    else
      out+=', '
    fi
    out+="$(ps_quote "$item")"
  done
  out+=')'
  printf '%s' "$out"
}

apply_ps='$false'
if [[ "$apply" == true ]]; then
  apply_ps='$true'
fi

dns_array="$(ps_string_array_from_csv "$dns_servers")"

read -r -d '' ps_script <<EOF || true
\$ErrorActionPreference = 'Stop'
\$ProgressPreference = 'SilentlyContinue'
\$Apply = $apply_ps
\$TargetName = $(ps_quote "$target_name")
\$InterfaceAlias = $(ps_quote "$interface_alias")
\$DnsServers = $dns_array
\$NtpServer = $(ps_quote "$ntp_server")
\$Domain = $(ps_quote "$domain")

function Section([string]\$Name) {
  Write-Output ""
  Write-Output "== \$Name =="
}

function Show-Value([string]\$Name, [object]\$Value) {
  Write-Output ("{0}: {1}" -f \$Name, [string]\$Value)
}

Section "mode"
Show-Value "apply" \$Apply

Section "identity"
Show-Value "computer_name_env" \$env:COMPUTERNAME
whoami

Section "os"
Get-CimInstance Win32_OperatingSystem |
  Select-Object Caption, Version, BuildNumber, LastBootUpTime |
  Format-List

Section "computer_system"
\$ComputerSystem = Get-CimInstance Win32_ComputerSystem
\$ComputerSystem | Select-Object Name, Domain, PartOfDomain, Workgroup | Format-List

Section "network"
Get-NetIPConfiguration -InterfaceAlias \$InterfaceAlias |
  Format-List InterfaceAlias, IPv4Address, IPv4DefaultGateway, DNSServer

Section "time_before"
w32tm /query /status

\$RestartRequired = \$false

if (-not \$Apply) {
  Section "dry_run"
  if (\$TargetName -and \$ComputerSystem.Name -ne \$TargetName) {
    Show-Value "would_rename_to" \$TargetName
  }
  if (\$DnsServers.Count -gt 0) {
    Show-Value "would_set_dns_on_interface" \$InterfaceAlias
    Show-Value "would_set_dns_servers" (\$DnsServers -join ',')
  }
  if (\$NtpServer) {
    Show-Value "would_set_ntp_server" \$NtpServer
  }
} else {
  Section "apply"
  if (\$TargetName -and \$ComputerSystem.Name -ne \$TargetName) {
    Rename-Computer -NewName \$TargetName -Force -PassThru
    \$RestartRequired = \$true
  } elseif (\$TargetName) {
    Show-Value "rename" "already_target_name"
  }

  if (\$DnsServers.Count -gt 0) {
    Set-DnsClientServerAddress -InterfaceAlias \$InterfaceAlias -ServerAddresses \$DnsServers
  }

  if (\$NtpServer) {
    w32tm /config /manualpeerlist:\$NtpServer /syncfromflags:manual /reliable:no /update
    Restart-Service w32time
    w32tm /resync /force
  }
}

Section "validation"
Get-DnsClientServerAddress -InterfaceAlias \$InterfaceAlias -AddressFamily IPv4 |
  Format-List InterfaceAlias, AddressFamily, ServerAddresses

if (\$NtpServer) {
  w32tm /stripchart /computer:\$NtpServer /samples:3 /dataonly
  w32tm /query /status
}

if (\$Domain) {
  Resolve-DnsName \$Domain -ErrorAction Stop | Format-Table -AutoSize
  Resolve-DnsName "_ldap._tcp.dc._msdcs.\$Domain" -Type SRV -ErrorAction Stop |
    Format-Table -AutoSize
}

Section "result"
Show-Value "restart_required" \$RestartRequired
EOF

encoded="$(
  printf '%s' "$ps_script" |
    iconv -f UTF-8 -t UTF-16LE |
    base64 -w 0
)"

ssh -i "$identity_file" \
  -o IdentitiesOnly=yes \
  -o BatchMode=yes \
  -o StrictHostKeyChecking=yes \
  -o UserKnownHostsFile="$known_hosts" \
  "$user@$host" \
  "powershell -NoProfile -ExecutionPolicy Bypass -EncodedCommand $encoded"
