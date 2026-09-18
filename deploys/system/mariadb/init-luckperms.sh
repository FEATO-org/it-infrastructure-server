#!/usr/bin/env bash
set -Eeuo pipefail
# Existing volumes need an explicit invocation; initdb runs only on empty volumes.
password="$(cat /run/secrets/luckperms_db_password)"
if [[ ! "$password" =~ ^[A-Za-z0-9+/=]+$ ]]; then
  echo "luckperms_db_password must be a nonempty base64 value." >&2
  exit 1
fi
umask 077
client_config="$(mktemp)"
trap 'rm -f "$client_config"' EXIT
printf '[client]\nuser=root\npassword=%s\nprotocol=socket\n' "$(cat /run/secrets/mariadb_root_password)" > "$client_config"
# Credentials stay out of process arguments, stdout and persistent SQL files.
mariadb --defaults-extra-file="$client_config" <<SQL
CREATE DATABASE IF NOT EXISTS luckperms CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'luckperms'@'%' IDENTIFIED BY '${password}';
GRANT SELECT, INSERT, UPDATE, DELETE, CREATE, ALTER, INDEX, DROP ON luckperms.* TO 'luckperms'@'%';
SQL
