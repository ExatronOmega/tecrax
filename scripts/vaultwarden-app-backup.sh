#!/usr/bin/env bash
set -euo pipefail
umask 077

src="${VAULTWARDEN_DATA_DIR:-/opt/vaultwarden/data}"
dest="${VAULTWARDEN_BACKUP_DIR:-/var/backups/vaultwarden/app}"
state_dir="${VAULTWARDEN_BACKUP_STATE_DIR:-/var/lib/tecrax/vaultwarden-app-backup}"
ts="$(date -u +%Y%m%dT%H%M%SZ)"
backup_id="vaultwarden-app-${ts}"
work="$(mktemp -d "/var/tmp/${backup_id}.XXXXXX")"
cleanup() {
  rm -rf "$work"
}
trap cleanup EXIT

require_file() {
  if [ ! -f "$1" ]; then
    echo "missing_required_file:$1" >&2
    exit 1
  fi
}

install -d -m 0700 "$dest" "$state_dir"
require_file "$src/db.sqlite3"
command -v sqlite3 >/dev/null
command -v tar >/dev/null
command -v sha256sum >/dev/null

install -d -m 0700 "$work/data"
sqlite3 "$src/db.sqlite3" ".backup '$work/data/db.sqlite3'"
sqlite_check="$(sqlite3 "$work/data/db.sqlite3" 'PRAGMA quick_check;')"
if [ "$sqlite_check" != "ok" ]; then
  echo "sqlite_quick_check_failed:$sqlite_check" >&2
  exit 1
fi

(
  cd "$src"
  tar \
    --exclude='./db.sqlite3' \
    --exclude='./db.sqlite3-shm' \
    --exclude='./db.sqlite3-wal' \
    --exclude='./tmp' \
    -cpf - .
) | (
  cd "$work/data"
  tar -xpf -
)

printf '%s\n' "$sqlite_check" > "$work/sqlite_quick_check.txt"
archive="$dest/${backup_id}.tar.gz"
manifest="$dest/${backup_id}.manifest.txt"
tar -C "$work" -czf "$archive" data sqlite_quick_check.txt
chmod 0600 "$archive"
archive_sha256="$(sha256sum "$archive" | awk '{print $1}')"

{
  printf 'backup_id=%s\n' "$backup_id"
  printf 'created_utc=%s\n' "$ts"
  printf 'source_data_dir=%s\n' "$src"
  printf 'archive=%s\n' "$archive"
  printf 'archive_sha256=%s\n' "$archive_sha256"
  printf 'sqlite_quick_check=%s\n' "$sqlite_check"
  printf 'contains_vault_data=true\n'
  printf 'public_safe=false\n'
  printf 'secret_values_printed=false\n'
  printf 'retention_prune_performed=false\n'
} > "$manifest"
chmod 0600 "$manifest"

ln -sfn "$(basename "$archive")" "$dest/latest.tar.gz"
ln -sfn "$(basename "$manifest")" "$dest/latest.manifest.txt"
printf 'vaultwarden_app_backup_created=%s\n' "$archive"
printf 'vaultwarden_app_backup_manifest=%s\n' "$manifest"
printf 'vaultwarden_app_backup_sha256=%s\n' "$archive_sha256"
