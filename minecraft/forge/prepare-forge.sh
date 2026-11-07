#!/usr/bin/env bash
set -euo pipefail
umask 077

secret_file=/run/secrets/forwarding_secret
config_file=/data/config/proxy-compatible-forge.toml
if [[ ! -r "$secret_file" ]]; then
  echo 'Forwarding secret is missing or unreadable' >&2
  exit 1
fi
secret=$(cat "$secret_file")
if [[ -z "$secret" || "$secret" == *$'\n'* || "$secret" == *$'\r'* || "$secret" == *$'\t'* ]]; then
  echo 'Forwarding secret must be a nonempty single line without tabs' >&2
  exit 1
fi
mkdir -p /data/config
# The ZIP settings seed new volumes only; operator changes are not overwritten.
cp -rn /forge-config/config/. /data/config/
if [[ -e "$config_file" && ! -L "$config_file" ]]; then
  echo 'Refusing to replace existing Proxy Compatible Forge configuration' >&2
  exit 1
fi
secret=${secret//\\/\\\\}
secret=${secret//\"/\\\"}
private_dir=$(mktemp -d /tmp/forge-forwarding.XXXXXX)
printf '[forwarding]\nenabled = true\nmode = "MODERN"\nsecret = "%s"\n' "$secret" > "$private_dir/config.toml"
ln -sfn "$private_dir/config.toml" "$config_file"
unset secret
