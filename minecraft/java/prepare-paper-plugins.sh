#!/bin/sh
set -eu

/extras/copy-floodgate-key.sh

config=/data/plugins/BetterHorses/config.yml
mkdir -p /data/plugins/BetterHorses

# BetterHorses fills missing defaults at enable; preserve existing runtime settings.
if [ ! -e "$config" ]; then
  cat > "$config" <<'YAML'
settings:
  mounted-damage-boost:
    enabled: false
YAML
fi

if [ ! -f "$config" ] || [ ! -s "$config" ]; then
  echo "ERROR: BetterHorses config is missing, empty, or not a regular file." >&2
  exit 1
fi

mc-image-helper patch /extras/betterhorses-horsemanship.json

# Keep mechanic settings outside the automatic /plugins sync.
craftbook_config=/data/plugins/CraftBook/mechanisms.yml
mkdir -p /data/plugins/CraftBook
if [ ! -e "$craftbook_config" ]; then
  cp /extras/craftbook-mechanisms.yml "$craftbook_config"
fi
if [ ! -f "$craftbook_config" ] || [ ! -s "$craftbook_config" ]; then
  echo "ERROR: CraftBook mechanisms.yml is empty or not a regular file." >&2
  exit 1
fi
# Add only a missing Chairs section; retain blocks and all other mechanics.
if ! mc-image-helper yaml-path --file "$craftbook_config" '$.mechanics.Chairs' >/dev/null 2>&1; then
  chair_init=$(mktemp /tmp/craftbook-chairs.XXXXXX.json)
  trap 'rm -f -- "$chair_init"' EXIT
  cat > "$chair_init" <<'JSON'
{"file":"/data/plugins/CraftBook/mechanisms.yml","ops":[{"$put":{"path":"$.mechanics","key":"Chairs","value":{}}}]}
JSON
  mc-image-helper patch "$chair_init"
  rm -f -- "$chair_init"
  trap - EXIT
fi
mc-image-helper patch /extras/craftbook-chairs.json

# Pin the official Spigot dev asset; the dev-build release URL is mutable.
protocol_jar=/data/plugins/ProtocolLib-Spigot.jar
protocol_sha256=a4ef57c36e27adec56b3a7935b7930fd1e366b310b9b698949e7f3320c84a8f9
if ! echo "$protocol_sha256  $protocol_jar" | sha256sum -c - >/dev/null 2>&1; then
  protocol_temp=$(mktemp /data/plugins/.ProtocolLib.XXXXXX)
  trap 'rm -f -- "$protocol_temp"' EXIT
  mc-image-helper get --accept application/octet-stream \
    -o "$protocol_temp" \
    https://api.github.com/repos/dmulloy2/ProtocolLib/releases/assets/608298575
  echo "$protocol_sha256  $protocol_temp" | sha256sum -c -
  mv -f -- "$protocol_temp" "$protocol_jar"
  trap - EXIT
fi

# Preserve runtime chest settings; disable only the built-in updater.
deadchest_config=/data/plugins/DeadChest/config.yml
mkdir -p /data/plugins/DeadChest
if [ ! -e "$deadchest_config" ]; then
  printf 'updates:\n  auto-check: false\n' > "$deadchest_config"
fi
mc-image-helper patch /extras/deadchest-updates.json

# Paper can promote staged updater JARs at startup. Remove only DeadChest builds.
for staged_jar in /data/plugins/update/dead-chest-*.jar; do
  [ ! -f "$staged_jar" ] || rm -f -- "$staged_jar"
done
