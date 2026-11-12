#!/usr/bin/env bash
set -euo pipefail

# Run only with Forge stopped and a complete volume backup available.
data_dir=${1:-/data}
src="$data_dir/tacz"
state_dir="$data_dir/.feato-content"
retired="$state_dir/retired"
archive="$retired/tacz-directory"
entries=(
  'tacz_feato-charge-into-battle.zip.sha256|40797ee6fc734de14e3065e80f85a61efa67207af9914d24084b3b680a8aba60'
  'tacz_feato-eos.zip.sha256|0b490c48b3ce16c2dc15f8822fd488901bd04f46c7d647d91cffca758ec71bb3'
  'tacz_feato-alex-kim.zip.sha256|fe5d8689e44fff6bef3942dd3ff2d01b47107c32c5dbb8af812d24b36d66cb8d'
  'tacz_feato-classics-reborn.zip.sha256|6aa04aa13b87969b4a4f9edceb6ca69dc226f439d9fdbe82ec02b4620d4c1981'
  'tacz_feato-weapons-and-tactics.zip.sha256|e9983776641a5ffa95fef55198d91ff595faff1630934cb4bfa7d6a8c4666c10'
)
for dir in "$data_dir" "$src" "$state_dir" "$retired"; do
  if [[ -L "$dir" || ( -e "$dir" && ! -d "$dir" ) ]]; then
    echo "Refusing unsafe directory: $dir" >&2; exit 1
  fi
done
if [[ -e "$archive" || -L "$archive" ]]; then
  echo "Archive already exists: $archive; inspect it before proceeding" >&2; exit 1
fi
for entry in "${entries[@]}"; do
  IFS='|' read -r name expected <<< "$entry"
  file="$state_dir/$name"
  if [[ -e "$file" || -L "$file" ]]; then
    [[ ! -L "$file" && -f "$file" && "$(cat "$file")" == "$expected" ]] || {
      echo "Unexpected management record: $file" >&2; exit 1;
    }
  fi
done
if [[ ! -d "$src" ]]; then
  echo "TaCZ directory is absent; no files or records were changed"; exit 0
fi
mkdir -p "$archive/records"
mv -- "$src" "$archive/tacz"
for entry in "${entries[@]}"; do
  IFS='|' read -r name expected <<< "$entry"
  file="$state_dir/$name"
  [[ ! -f "$file" ]] || mv -- "$file" "$archive/records/$name"
done
echo "Retired directory and existing management records to: $archive"
