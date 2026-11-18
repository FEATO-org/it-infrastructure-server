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

# Synchronize pinned content after preserving the forwarding and configuration setup.
bash /forge-pack/sync-content.sh /data /forge-pack/content.lock

# The agent must bind only to the dedicated overlay, not the backend interface.
# The alias is scoped to that overlay; route lookup selects this task's source IP.
if [[ ${JVM_OPTS:-} == *FORGE_JMX_BIND:9404* ]]; then
bind_ip=''
for attempt in {1..30}; do
  vip=$(getent ahostsv4 forge-jvm-target | awk 'NR == 1 {print $1}') || true
  if [[ -n "$vip" ]]; then
    bind_ip=$(ip -4 route get "$vip" | awk '{for (i=1; i<=NF; i++) if ($i == "src") {print $(i+1); exit}}')
    [[ "$bind_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] && break
  fi
  sleep 1
done
if [[ ! "$bind_ip" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || ! grep -q 'FORGE_JMX_BIND:9404' /data/user_jvm_args.txt; then
  echo 'Cannot bind Forge JMX agent to the monitoring overlay; refusing startup' >&2
  exit 1
fi
sed -i "s/FORGE_JMX_BIND:9404/${bind_ip}:9404/g" /data/user_jvm_args.txt
fi
