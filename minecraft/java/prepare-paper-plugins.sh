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
