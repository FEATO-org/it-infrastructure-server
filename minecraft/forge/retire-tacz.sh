#!/usr/bin/env bash
set -euo pipefail

# Run manually only while the Forge service is stopped and its volume is backed up.
data_dir=${1:-/data}
archive="$data_dir/.feato-content/retired/tacz-removal"
entries=(
  'mods/tacz-forge-1.20.1-1.2.0.jar|1c2f2915f76908d396a0da577665c977564c279ccb89d459a00a29225aa45a92|no'
  'mods/WaT-0.4.1.jar|8b9f4c3e3c238e7a24e5d301ac152dcc1a0d283c43e7f8037d37e0274e723124|no'
  'mods/guccivuitton-1.20.1-0.2.2.jar|9247e55f20acf8ec89af56d4ad45fcc8fe08bee9f7189421ef31835f3516bd57|no'
  'mods/lrtactical-1.20.1-0.4.3.jar|930372cab33e1f563f597c74f9155b5ed25e6f2b0ff7e12dfc86255e1020ef2d|no'
  'mods/tacz_c-1.0.2-forge-1.20.1.jar|31dce4d848c5be8c99bd32babf2ead50616387ecd0527c882cf9bdd8b6b44ee6|no'
  'mods/feato-arcana.jar|023cd1ea0f4a48fa77d1634ce97cf03753daacb24293dcdfad4727fa329e2936|yes'
  'tacz/feato-charge-into-battle.zip|40797ee6fc734de14e3065e80f85a61efa67207af9914d24084b3b680a8aba60|yes'
  'tacz/feato-eos.zip|0b490c48b3ce16c2dc15f8822fd488901bd04f46c7d647d91cffca758ec71bb3|yes'
  'tacz/feato-alex-kim.zip|fe5d8689e44fff6bef3942dd3ff2d01b47107c32c5dbb8af812d24b36d66cb8d|yes'
  'tacz/feato-classics-reborn.zip|6aa04aa13b87969b4a4f9edceb6ca69dc226f439d9fdbe82ec02b4620d4c1981|yes'
  'tacz/feato-weapons-and-tactics.zip|e9983776641a5ffa95fef55198d91ff595faff1630934cb4bfa7d6a8c4666c10|yes'
)

# Refuse symlinked parents and destinations before any move.
for dir in "$data_dir" "$data_dir/mods" "$data_dir/tacz" "$data_dir/.feato-content" "$data_dir/.feato-content/retired" "$archive"; do
  if [[ -L "$dir" || ( -e "$dir" && ! -d "$dir" ) ]]; then
    echo "Refusing unsafe directory: $dir" >&2; exit 1
  fi
done
for entry in "${entries[@]}"; do
  IFS='|' read -r relative expected managed <<< "$entry"
  src="$data_dir/$relative"
  state="$data_dir/.feato-content/${relative//\//_}.sha256"
  dest="$archive/${relative//\//_}"
  if [[ ! -e "$src" && ! -L "$src" ]]; then
    echo "Absent: $relative"; continue
  fi
  [[ ! -L "$src" && -f "$src" ]] || { echo "Not a regular file: $src" >&2; exit 1; }
  [[ "$(sha256sum "$src" | cut -d ' ' -f 1)" == "$expected" ]] || { echo "Hash mismatch: $src" >&2; exit 1; }
  if [[ "$managed" == yes ]]; then
    [[ ! -L "$state" && -f "$state" && "$(cat "$state")" == "$expected" ]] || { echo "Missing or mismatched management record: $state" >&2; exit 1; }
  fi
  [[ ! -e "$dest" && ! -L "$dest" && ! -e "$dest.sha256" && ! -L "$dest.sha256" ]] || { echo "Archive collision: $dest" >&2; exit 1; }
done
mkdir -p "$archive"
for entry in "${entries[@]}"; do
  IFS='|' read -r relative expected managed <<< "$entry"
  src="$data_dir/$relative"
  [[ -f "$src" && ! -L "$src" ]] || continue
  dest="$archive/${relative//\//_}"
  mv -- "$src" "$dest"
  if [[ "$managed" == yes ]]; then
    mv -- "$data_dir/.feato-content/${relative//\//_}.sha256" "$dest.sha256"
  fi
  echo "Retired: $relative"
done
