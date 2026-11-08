#!/usr/bin/env bash
set -euo pipefail

# Manual operation only: stop Forge and back up the whole volume first.
data_dir=${1:-/data}
state_dir="$data_dir/.feato-content"
archive="$state_dir/retired/removed-tacz-addons"
mods=(
  'guccivuitton-1.20.1-0.2.2.jar|9247e55f20acf8ec89af56d4ad45fcc8fe08bee9f7189421ef31835f3516bd57'
  'lrtactical-1.20.1-0.4.3.jar|930372cab33e1f563f597c74f9155b5ed25e6f2b0ff7e12dfc86255e1020ef2d'
)
configs=('config/lrtactical-common.toml' 'config/lrtactical-client.toml' 'world/serverconfig/lrtactical-server.toml')
records=(
  'tacz_feato-charge-into-battle.zip.sha256|40797ee6fc734de14e3065e80f85a61efa67207af9914d24084b3b680a8aba60'
  'tacz_feato-eos.zip.sha256|0b490c48b3ce16c2dc15f8822fd488901bd04f46c7d647d91cffca758ec71bb3'
  'tacz_feato-alex-kim.zip.sha256|fe5d8689e44fff6bef3942dd3ff2d01b47107c32c5dbb8af812d24b36d66cb8d'
  'tacz_feato-classics-reborn.zip.sha256|6aa04aa13b87969b4a4f9edceb6ca69dc226f439d9fdbe82ec02b4620d4c1981'
  'tacz_feato-weapons-and-tactics.zip.sha256|e9983776641a5ffa95fef55198d91ff595faff1630934cb4bfa7d6a8c4666c10'
)
for dir in "$data_dir" "$data_dir/mods" "$data_dir/tacz" "$data_dir/config" "$data_dir/world" "$data_dir/world/serverconfig" "$state_dir" "$state_dir/retired"; do
  [[ ! -L "$dir" && ( ! -e "$dir" || -d "$dir" ) ]] || { echo "Refusing unsafe directory: $dir" >&2; exit 1; }
done
[[ ! -e "$archive" && ! -L "$archive" ]] || { echo "Archive already exists: $archive" >&2; exit 1; }
for entry in "${mods[@]}"; do
  IFS='|' read -r name hash <<< "$entry"
  src="$data_dir/mods/$name"
  if [[ ! -e "$src" && ! -L "$src" ]]; then echo "Absent: mods/$name"; continue; fi
  [[ ! -L "$src" && -f "$src" ]] || { echo "Not a regular file: $src" >&2; exit 1; }
  [[ "$(sha256sum "$src" | cut -d ' ' -f 1)" == "$hash" ]] || { echo "Hash mismatch: $src" >&2; exit 1; }
done
for relative in "${configs[@]}"; do
  src="$data_dir/$relative"
  if [[ -e "$src" || -L "$src" ]]; then
    [[ ! -L "$src" && -f "$src" ]] || { echo "Not a regular config file: $src" >&2; exit 1; }
  fi
done
for entry in "${records[@]}"; do
  IFS='|' read -r name expected <<< "$entry"
  src="$state_dir/$name"
  if [[ -e "$src" || -L "$src" ]]; then
    [[ ! -L "$src" && -f "$src" && "$(cat "$src")" == "$expected" ]] || { echo "Unexpected management record: $src" >&2; exit 1; }
  fi
done
# All checks happen before the first move. Nothing is overwritten.
mkdir -p "$archive/mods" "$archive/config" "$archive/world-serverconfig" "$archive/records"
for entry in "${mods[@]}"; do
  IFS='|' read -r name hash <<< "$entry"
  src="$data_dir/mods/$name"
  if [[ -f "$src" ]]; then mv -- "$src" "$archive/mods/$name"; echo "Retired: mods/$name"; fi
done
if [[ -d "$data_dir/tacz" ]]; then
  mv -- "$data_dir/tacz" "$archive/tacz"
  echo 'Retired: tacz/'
fi
for relative in "${configs[@]}"; do
  src="$data_dir/$relative"
  if [[ -f "$src" ]]; then
    if [[ "$relative" == world/serverconfig/* ]]; then dest="$archive/world-serverconfig/${relative##*/}"; else dest="$archive/config/${relative##*/}"; fi
    mv -- "$src" "$dest"
    echo "Retired: $relative"
  fi
done
for entry in "${records[@]}"; do
  IFS='|' read -r name expected <<< "$entry"
  src="$state_dir/$name"
  if [[ -f "$src" ]]; then mv -- "$src" "$archive/records/$name"; fi
done
echo "Retired files are under: $archive"
