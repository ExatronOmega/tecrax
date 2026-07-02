#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  provision-samba-ad-users.sh [--apply]
    --csv PATH
    --user-ou OU_PATH
    [--password-stdin | --prompt-password]

Public-safe helper for deterministic Samba AD user provisioning.

CSV format:
  login,given_name,surname,email,groups

The groups field is a semicolon-separated list of existing group names.
The first line may be a header. Values must not contain commas.

Defaults to dry-run. The --apply flag is required before any AD mutation.
Domain credentials, temporary passwords, private inventory and real user lists
must stay outside the repository.
EOF
}

apply=false
csv_path=""
user_ou=""
password_stdin=false
prompt_password=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --apply)
      apply=true
      shift
      ;;
    --csv)
      csv_path="${2:-}"
      shift 2
      ;;
    --user-ou)
      user_ou="${2:-}"
      shift 2
      ;;
    --password-stdin)
      password_stdin=true
      shift
      ;;
    --prompt-password)
      prompt_password=true
      shift
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

require_value "--csv" "$csv_path"
require_value "--user-ou" "$user_ou"

if [[ ! -f "$csv_path" ]]; then
  echo "CSV file does not exist: $csv_path" >&2
  exit 2
fi

if [[ "$password_stdin" == true && "$prompt_password" == true ]]; then
  echo "--password-stdin and --prompt-password are mutually exclusive" >&2
  exit 2
fi

if [[ "$apply" == true && "$password_stdin" == false && "$prompt_password" == false ]]; then
  echo "Apply mode requires --password-stdin or --prompt-password" >&2
  exit 2
fi

temp_password=""
if [[ "$apply" == true && "$password_stdin" == true ]]; then
  IFS= read -r temp_password
elif [[ "$apply" == true && "$prompt_password" == true ]]; then
  read -r -s -p "Temporary password: " temp_password
  printf '\n' >&2
fi

if [[ "$apply" == true && -z "$temp_password" ]]; then
  echo "Temporary password cannot be empty" >&2
  exit 2
fi

trim() {
  local value="$1"
  value="${value#"${value%%[![:space:]]*}"}"
  value="${value%"${value##*[![:space:]]}"}"
  printf '%s' "$value"
}

ensure_user() {
  local login="$1"
  local given_name="$2"
  local surname="$3"
  local email="$4"

  if samba-tool user show "$login" >/dev/null 2>&1; then
    echo "user_exists:$login"
    return
  fi

  if [[ "$apply" != true ]]; then
    echo "would_create_user:$login"
    return
  fi

  samba-tool user create "$login" "$temp_password" \
    --userou="$user_ou" \
    --given-name="$given_name" \
    --surname="$surname" \
    --mail-address="$email" \
    --must-change-at-next-login >/dev/null
  echo "user_created:$login"
}

ensure_member() {
  local group="$1"
  local login="$2"

  if samba-tool group listmembers "$group" | grep -Fxq "$login"; then
    echo "member_exists:$group:$login"
    return
  fi

  if [[ "$apply" != true ]]; then
    echo "would_add_member:$group:$login"
    return
  fi

  samba-tool group addmembers "$group" "$login" >/dev/null
  echo "member_added:$group:$login"
}

line_no=0
while IFS=, read -r login given_name surname email groups extra; do
  line_no=$((line_no + 1))
  login="$(trim "${login:-}")"
  given_name="$(trim "${given_name:-}")"
  surname="$(trim "${surname:-}")"
  email="$(trim "${email:-}")"
  groups="$(trim "${groups:-}")"

  if [[ "$line_no" -eq 1 && "$login" == "login" ]]; then
    continue
  fi

  if [[ -n "${extra:-}" ]]; then
    echo "Line $line_no has too many CSV fields" >&2
    exit 2
  fi

  if [[ -z "$login" && -z "$given_name" && -z "$surname" && -z "$email" && -z "$groups" ]]; then
    continue
  fi

  if [[ -z "$login" || -z "$given_name" || -z "$surname" || -z "$email" ]]; then
    echo "Line $line_no is missing required user fields" >&2
    exit 2
  fi

  ensure_user "$login" "$given_name" "$surname" "$email"

  IFS=';' read -r -a group_items <<<"$groups"
  for group in "${group_items[@]}"; do
    group="$(trim "$group")"
    if [[ -n "$group" ]]; then
      ensure_member "$group" "$login"
    fi
  done
done <"$csv_path"
