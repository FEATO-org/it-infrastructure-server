#!/usr/bin/env bash
# Called after the image writes user_jvm_args.txt and before Forge's run.sh.
set -euo pipefail
args_file=${1:-/data/user_jvm_args.txt}
agent='-javaagent:/data/monitoring/jmx_prometheus_javaagent-1.7.0.jar=FORGE_JMX_BIND:9404:/forge-jmx/config.yml'
[[ ${JVM_OPTS:-} == *FORGE_JMX_BIND:9404* ]] || exit 0
if [[ ! -f "$args_file" || ! -r "$args_file" || ! -w "$args_file" ]]; then
  echo 'ERROR: Forge JVM argument file is missing or inaccessible; cannot safely disable JMX' >&2
  exit 1
fi
# The edit cannot be verified without these tools.
for cmd in grep sed mktemp mv; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "ERROR: Missing command $cmd; cannot safely disable JMX" >&2
    exit 1
  fi
done
# Only transform the exact, standalone option managed by this repository.
if ! grep -Eq -- '(^|[[:space:]])-javaagent:/data/monitoring/jmx_prometheus_javaagent-1\.7\.0\.jar=FORGE_JMX_BIND:9404:/forge-jmx/config\.yml([[:space:]]|$)' "$args_file"; then
  if grep -q 'FORGE_JMX_BIND' "$args_file"; then
    echo 'ERROR: Unexpected JMX agent argument; cannot safely disable JMX' >&2
    exit 1
  fi
  echo 'WARN: JMX agent argument missing from JVM argument file; JMX monitoring disabled' >&2
  exit 0
fi
bind_ip=''
commands_ok=true
for cmd in getent ip awk; do
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "WARN: JMX monitoring requires missing command: $cmd" >&2
    commands_ok=false
    break
  fi
done
if $commands_ok; then
  # Fluent Bit shares only the monitoring overlay with Forge. Unlike the Forge
  # alias, its service DNS does not depend on this task becoming ready.
  target=$(getent ahostsv4 system_fluent-bit | awk 'NR == 1 {print $1}') || true
  if [[ -z "$target" ]]; then
    echo 'WARN: JMX monitoring network DNS lookup failed for system_fluent-bit' >&2
  elif ! route=$(ip -4 route get "$target" 2>/dev/null); then
    echo 'WARN: JMX monitoring network route lookup failed' >&2
  else
    dev=$(awk '{for (i=1; i<=NF; i++) if ($i == "dev") {print $(i+1); exit}}' <<< "$route")
    default_dev=$(ip -4 route show default | awk 'NR == 1 {for (i=1; i<=NF; i++) if ($i == "dev") {print $(i+1); exit}}') || true
    bind_ip=$(awk '{for (i=1; i<=NF; i++) if ($i == "src") {print $(i+1); exit}}' <<< "$route")
    if [[ -z $dev || -z $default_dev || $dev == "$default_dev" || ! $bind_ip =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      echo 'WARN: JMX monitoring network source IP could not be determined' >&2
      bind_ip=''
    fi
  fi
fi
# The complete option is fixed above; never fall back to a wildcard bind.
if [[ -n "$bind_ip" ]]; then
  replacement="-javaagent:/data/monitoring/jmx_prometheus_javaagent-1.7.0.jar=${bind_ip}:9404:/forge-jmx/config.yml"
else
  replacement=''
fi
tmp=$(mktemp "${args_file}.jmx.XXXXXXXX")
trap 'rm -f -- "$tmp"' EXIT
if ! sed "s|${agent//./\\.}|${replacement}|g" "$args_file" > "$tmp" || grep -q 'FORGE_JMX_BIND' "$tmp"; then
  echo 'ERROR: JMX agent argument replacement failed; refusing unsafe startup' >&2
  exit 1
fi
mv -f -- "$tmp" "$args_file"
trap - EXIT
if [[ -n "$bind_ip" ]]; then
  echo 'JMX monitoring enabled on the dedicated overlay'
else
  echo 'WARN: JMX monitoring disabled; starting Forge without the JMX agent' >&2
fi
