#!/usr/bin/env bash
set -euo pipefail

readonly rcon_password_file=/run/secrets/minecraft_proxy_rcon_password
readonly rcon_cli_config=/root/.rcon-cli.yaml

case "${DEBUG:-false,,}" in
  true|on)
    echo "ERROR: DEBUG must be disabled while Proxy RCON uses a secret." >&2
    exit 1
    ;;
esac

if [[ ! -r "${rcon_password_file}" ]]; then
  echo "ERROR: Proxy RCON password secret is missing or unreadable: ${rcon_password_file}" >&2
  exit 1
fi

if ! RCON_PASSWORD="$(cat -- "${rcon_password_file}")"; then
  echo "ERROR: Failed to read Proxy RCON password secret." >&2
  exit 1
fi

if [[ -z "${RCON_PASSWORD}" ]]; then
  echo "ERROR: Proxy RCON password secret is empty." >&2
  exit 1
fi

if [[ "${RCON_PASSWORD}" == *$'\n'* || "${RCON_PASSWORD}" == *$'\r'* ]]; then
  echo "ERROR: Proxy RCON password secret must contain one line." >&2
  exit 1
fi

export RCON_PASSWORD

# docker exec runs rcon-cli as root, so provide its default root-owned configuration.
rcon_password_yaml=${RCON_PASSWORD//\'/\'\'}
rcon_cli_config_tmp="$(mktemp "${rcon_cli_config}.XXXXXX")"
trap 'rm -f -- "${rcon_cli_config_tmp}"' EXIT
printf "host: localhost\nport: %s\npassword: '%s'\n" "${RCON_PORT:-25575}" "${rcon_password_yaml}" > "${rcon_cli_config_tmp}"
mv -f -- "${rcon_cli_config_tmp}" "${rcon_cli_config}"
trap - EXIT

exec "$@"
