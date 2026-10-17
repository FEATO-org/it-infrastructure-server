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

# The growth section may be absent from the first-start seed or older configs.
if ! mc-image-helper yaml-path --file "$config" '$.horse-growth-settings' >/dev/null 2>&1; then
  growth_init=$(mktemp /tmp/betterhorses-growth.XXXXXX.json)
  trap 'rm -f -- "$growth_init"' EXIT
  cat > "$growth_init" <<'JSON'
{"file":"/data/plugins/BetterHorses/config.yml","ops":[{"$put":{"path":"$","key":"horse-growth-settings","value":{}}}]}
JSON
  mc-image-helper patch "$growth_init"
  rm -f -- "$growth_init"
  trap - EXIT
fi
if ! mc-image-helper yaml-path --file "$config" '$.max-stats' >/dev/null 2>&1; then
  max_stats_init=$(mktemp /tmp/betterhorses-max-stats.XXXXXX.json)
  trap 'rm -f -- "$max_stats_init"' EXIT
  cat > "$max_stats_init" <<'JSON'
{"file":"/data/plugins/BetterHorses/config.yml","ops":[{"$put":{"path":"$","key":"max-stats","value":{}}}]}
JSON
  mc-image-helper patch "$max_stats_init"
  rm -f -- "$max_stats_init"
  trap - EXIT
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
# Add only missing sections before patching selected keys; never sync whole runtime configs.
ensure_section() {
  section_file=$1
  parent_path=$2
  section_key=$3
  if ! mc-image-helper yaml-path --file "$section_file" "$parent_path.$section_key" >/dev/null 2>&1; then
    section_init=$(mktemp /tmp/paper-section.XXXXXX.json)
    trap 'rm -f -- "$section_init"' EXIT
    cat > "$section_init" <<JSON
{"file":"$section_file","ops":[{"\$put":{"path":"$parent_path","key":"$section_key","value":{}}}]}
JSON
    mc-image-helper patch "$section_init"
    rm -f -- "$section_init"
    trap - EXIT
  fi
}

ensure_section "$craftbook_config" '$' mechanics
ensure_section "$craftbook_config" '$.mechanics' Chairs
mc-image-helper patch /extras/craftbook-chairs.json

# BEGIN living/building configuration (also exercised by the isolated startup test).
for mechanic in BetterLeads SignCopier Bookcase HeadDrops; do
  ensure_section "$craftbook_config" '$.mechanics' "$mechanic"
done
mc-image-helper patch /extras/craftbook-life.json

# Bookcase reads one shared UTF-8 file; preserve operator-authored text on every restart.
if [ ! -e /data/plugins/CraftBook/books.txt ]; then
  cp /extras/craftbook-books.txt /data/plugins/CraftBook/books.txt
fi

for plugin in GSit EasyArmorStands; do
  case "$plugin" in
    GSit) seed=gsit-config.yml ;;
    EasyArmorStands) seed=easyarmorstands-config.yml ;;
  esac
  plugin_config="/data/plugins/$plugin/config.yml"
  mkdir -p "/data/plugins/$plugin"
  if [ ! -e "$plugin_config" ]; then
    cp "/extras/$seed" "$plugin_config"
  fi
  if [ ! -f "$plugin_config" ] || [ ! -s "$plugin_config" ]; then
    echo "ERROR: $plugin config.yml is empty or not a regular file." >&2
    exit 1
  fi
done

gsit_config=/data/plugins/GSit/config.yml
ensure_section "$gsit_config" '$' Lang
ensure_section "$gsit_config" '$' Options
for section in PlayerSit Pose Crawl; do
  ensure_section "$gsit_config" '$.Options' "$section"
done
mc-image-helper patch /extras/gsit-life.json

armorstands_config=/data/plugins/EasyArmorStands/config.yml
ensure_section "$armorstands_config" '$' editor
ensure_section "$armorstands_config" '$' integration
ensure_section "$armorstands_config" '$.integration' FancyHolograms
mc-image-helper patch /extras/easyarmorstands-life.json
# END living/building configuration.

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

# Prevent loss of unclaimed items on timeout; preserve other chest settings.
deadchest_config=/data/plugins/DeadChest/config.yml
mkdir -p /data/plugins/DeadChest
if [ ! -e "$deadchest_config" ]; then
  cp /extras/deadchest-config.yml "$deadchest_config"
fi
if [ ! -f "$deadchest_config" ] || [ ! -s "$deadchest_config" ]; then
  echo "ERROR: DeadChest config is missing, empty, or not a regular file." >&2
  exit 1
fi
# Let DeadChest migrate legacy protection settings once; never overlay defaults.
if ! mc-image-helper yaml-path --file "$deadchest_config" '$.chest' >/dev/null 2>&1; then
  chest_init=$(mktemp /tmp/deadchest-chest.XXXXXX.json)
  trap 'rm -f -- "$chest_init"' EXIT
  cat > "$chest_init" <<'JSON'
{"file":"/data/plugins/DeadChest/config.yml","ops":[{"$put":{"path":"$","key":"chest","value":{}}}]}
JSON
  mc-image-helper patch "$chest_init"
  rm -f -- "$chest_init"
  trap - EXIT
fi
if ! mc-image-helper yaml-path --file "$deadchest_config" '$.updates' >/dev/null 2>&1; then
  updates_init=$(mktemp /tmp/deadchest-updates.XXXXXX.json)
  trap 'rm -f -- "$updates_init"' EXIT
  cat > "$updates_init" <<'JSON'
{"file":"/data/plugins/DeadChest/config.yml","ops":[{"$put":{"path":"$","key":"updates","value":{}}}]}
JSON
  mc-image-helper patch "$updates_init"
  rm -f -- "$updates_init"
  trap - EXIT
fi
# Bukkit treats null as unset: a false legacy alias still triggers migration.
mc-image-helper patch /extras/deadchest-updates.json

# FAWE provides WorldEdit. Never leave the old standalone JAR in the persistent volume.
# Paper can promote staged updater JARs at startup; retain configuration and schematics.
for obsolete_jar in /data/plugins/worldedit-bukkit-*.jar \
    /data/plugins/update/worldedit-bukkit-*.jar \
    /data/plugins/.paper-remapped/worldedit-bukkit-*.jar \
    /data/plugins/update/dead-chest-*.jar; do
  [ ! -f "$obsolete_jar" ] || rm -f -- "$obsolete_jar"
done

# Correct only reviewed ValhallaMMO salvage recipes after /plugins synchronization.
sh /extras/startup/valhalla-salvage.sh
