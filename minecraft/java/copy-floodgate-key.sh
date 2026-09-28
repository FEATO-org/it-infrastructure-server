#!/bin/sh
set -eu

secret=/run/secrets/floodgate_key
key_dir=/data/plugins/floodgate
key_file=${key_dir}/key.pem

if [ ! -f "$secret" ] || [ ! -r "$secret" ]; then
  echo "ERROR: Floodgate secret is missing or unreadable: $secret" >&2
  exit 1
fi
if [ ! -s "$secret" ]; then
  echo "ERROR: Floodgate secret is empty: $secret" >&2
  exit 1
fi

if ! mkdir -p "$key_dir"; then
  echo "ERROR: Cannot create Floodgate data directory: $key_dir" >&2
  exit 1
fi

if ! temp_file=$(mktemp "${key_dir}/.key.pem.XXXXXX"); then
  echo "ERROR: Cannot create temporary Floodgate key file." >&2
  exit 1
fi
trap 'rm -f -- "$temp_file"' EXIT

if [ -d "$key_file" ] || ! cp -- "$secret" "$temp_file" || ! chmod 600 "$temp_file" || ! mv -f -- "$temp_file" "$key_file"; then
  echo "ERROR: Cannot install Floodgate key from Swarm secret." >&2
  exit 1
fi

trap - EXIT
