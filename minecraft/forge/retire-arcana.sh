#!/usr/bin/env bash
set -euo pipefail

# Run only with Forge stopped and a complete volume backup available.
data_dir=${1:-/data}
state_dir="$data_dir/.feato-content"
archive="$state_dir/retired/arcana-removal"
src="$data_dir/mods/feato-arcana.jar"
record="$state_dir/mods_feato-arcana.jar.sha256"
expected=023cd1ea0f4a48fa77d1634ce97cf03753daacb24293dcdfad4727fa329e2936
shopt -s nullglob
configs=("$data_dir"/config/taczexpands*)
for dir in "$data_dir" "$data_dir/mods" "$data_dir/config" "$state_dir" "$state_dir/retired"; do
  [[ ! -L "$dir" && ( ! -e "$dir" || -d "$dir" ) ]] || { echo "Refusing unsafe directory: $dir" >&2; exit 1; }
done
[[ ! -e "$archive" && ! -L "$archive" ]] || { echo "Archive already exists: $archive" >&2; exit 1; }
if [[ -e "$src" || -L "$src" ]]; then
  [[ ! -L "$src" && -f "$src" ]] || { echo "Not a regular file: $src" >&2; exit 1; }
  [[ "$(sha256sum "$src" | cut -d ' ' -f 1)" == "$expected" ]] || { echo "Hash mismatch: $src" >&2; exit 1; }
  [[ ! -L "$record" && -f "$record" && "$(cat "$record")" == "$expected" ]] || { echo "Missing or mismatched management record: $record" >&2; exit 1; }
elif [[ -e "$record" || -L "$record" ]]; then
  [[ ! -L "$record" && -f "$record" && "$(cat "$record")" == "$expected" ]] || { echo "Unexpected management record: $record" >&2; exit 1; }
fi
for path in ${configs[@]+"${configs[@]}"}; do
  [[ ! -L "$path" && ( -f "$path" || -d "$path" ) ]] || { echo "Unsafe taczexpands path: $path" >&2; exit 1; }
done
if [[ ! -f "$src" && ! -f "$record" && -z "${configs[*]-}" ]]; then
  echo 'No Arcana files or taczexpands config found'; exit 0
fi
mkdir -p "$archive/config"
if [[ -f "$src" ]]; then mv -- "$src" "$archive/feato-arcana.jar"; echo 'Retired: mods/feato-arcana.jar'; fi
if [[ -f "$record" ]]; then mv -- "$record" "$archive/mods_feato-arcana.jar.sha256"; echo 'Retired: management record'; fi
for path in ${configs[@]+"${configs[@]}"}; do
  mv -- "$path" "$archive/config/${path##*/}"
  echo "Retired: config/${path##*/}"
done
echo "Retired files are under: $archive"
