#!/bin/sh
set -eu
if [ "${VERSION:-}" != "26.2" ]; then
  echo "[ValhallaSalvage] ERROR: unreviewed Minecraft VERSION; expected 26.2" >&2
  exit 1
fi
# Java and Jackson are already provided by the Minecraft image / mc-image-helper.
script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec java --class-path '/usr/share/mc-image-helper/lib/*' \
  "$script_dir/ValhallaSalvage.java" /data/plugins
