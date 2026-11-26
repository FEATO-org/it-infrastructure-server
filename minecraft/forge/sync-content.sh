#!/usr/bin/env bash
set -euo pipefail

# Stable names identify only files managed by this script. Never remove other files.
data_dir=${1:-/data}
lock_file=${2:-/forge-pack/content.lock}
state_dir="$data_dir/.feato-content"
if [[ -L "$data_dir" || ! -d "$data_dir" || -L "$state_dir" ]]; then
  echo "Unsafe data or state directory" >&2; exit 1
fi
mkdir -p "$state_dir"

# The image updates server.properties before PRE_START_SCRIPT; Forge reads this file.
# Reject Java-properties escapes and paths rather than guessing their interpretation.
world=world
properties="$data_dir/server.properties"
if [[ -L "$properties" || ( -e "$properties" && ! -f "$properties" ) ]]; then
  echo "Unsafe server.properties" >&2; exit 1
fi
if [[ -f "$properties" ]]; then
  # Escaped keys can spell level-name in Java properties; do not guess.
  if grep -Eq '^[[:space:]]*[^#![:space:]=:]*\\[^=:\s]*' "$properties"; then
    echo "Unsupported escaped property key" >&2; exit 1
  fi
  if grep -Eq '^[[:space:]]*level-name[[:space:]]*$' "$properties"; then
    echo "Empty level-name" >&2; exit 1
  fi
  mapfile -t levels < <(sed -nE 's/^[[:space:]]*level-name([[:space:]]*[:=][[:space:]]*|[[:space:]]+)//p' "$properties")
  if (( ${#levels[@]} > 1 )); then echo "Ambiguous level-name" >&2; exit 1; fi
  if (( ${#levels[@]} == 1 )); then world=${levels[0]%$'\r'}; fi
fi
if [[ ! "$world" =~ ^[a-zA-Z0-9_-]+$ ]]; then
  echo "Unsafe or unsupported level-name" >&2; exit 1
fi

safe_dir() {
  local dir=$1
  if [[ -L "$dir" || ( -e "$dir" && ! -d "$dir" ) ]]; then
    echo "Unsafe content directory: $dir" >&2; exit 1
  fi
  mkdir -p -- "$dir"
}

# Validate the whole lock before taking any retirement action.
while IFS=$'\t' read -r rel hash source fallback extra; do
  [[ -z "$rel" || "$rel" == \#* ]] && continue
  if [[ ! "$rel" =~ ^(tacz/feato-[a-z0-9-]+\.zip|mods/feato-[a-z0-9-]+\.jar|monitoring/jmx_prometheus_javaagent-1\.7\.0\.jar|datapacks/feato-[a-z0-9-]+\.zip)$ || ! "$hash" =~ ^[0-9a-f]{64}$ || -z "$source" || -n "$extra" ]]; then
    echo "Invalid content lock entry: $rel" >&2; exit 1
  fi
done < "$lock_file"

# Retire only recorded datapacks whose bytes still match the recorded hash.
# A world rename also retires the old world's managed copy.
shopt -s nullglob
for record in "$state_dir"/datapack__*__*.sha256; do
  name=${record##*/}
  if [[ ! "$name" =~ ^datapack__([a-zA-Z0-9_-]+)__(feato-[a-z0-9-]+\.zip)\.sha256$ ]]; then
    echo "Invalid datapack state: $name" >&2; exit 1
  fi
  old_world=${BASH_REMATCH[1]}; filename=${BASH_REMATCH[2]}
  if [[ "$old_world" == "$world" ]] && awk -F '\t' -v p="datapacks/$filename" '$1 == p {found=1} END {exit !found}' "$lock_file"; then continue; fi
  [[ ! -L "$record" && -f "$record" ]] || { echo "Unsafe state: $record" >&2; exit 1; }
  old_hash=$(cat "$record")
  [[ "$old_hash" =~ ^[0-9a-f]{64}$ ]] || { echo "Invalid state: $record" >&2; exit 1; }
  old_dir="$data_dir/$old_world"; packs="$old_dir/datapacks"; old_target="$packs/$filename"
  [[ ! -L "$old_dir" && ! -L "$packs" ]] || { echo "Unsafe datapack directory" >&2; exit 1; }
  if [[ -e "$old_target" || -L "$old_target" ]]; then
    [[ ! -L "$old_target" && -f "$old_target" && "$(sha256sum "$old_target" | cut -d ' ' -f 1)" == "$old_hash" ]] || { echo "Refusing to retire modified datapack: $old_target" >&2; exit 1; }
    safe_dir "$state_dir/retired-datapacks"
    archive="$state_dir/retired-datapacks/${old_world}__${filename}__${old_hash}"
    [[ ! -e "$archive" && ! -L "$archive" ]] || { echo "Retired datapack already exists: $archive" >&2; exit 1; }
    mv -nT -- "$old_target" "$archive"
    [[ ! -e "$old_target" && ! -L "$old_target" ]] || exit 1
  fi
  rm -- "$record"
done
shopt -u nullglob

# Retire only ZIPs that match both the former pin and the active management record.
retire_gunpack() {
  local filename=$1 expected=$2 archive_path=$3
  local target="$data_dir/tacz/$filename"
  local state="$state_dir/tacz_${filename}.sha256"
  local archive="$state_dir/$archive_path"
  local archive_dir="${archive%/*}"

  if [[ -e "$target" || -L "$target" ]]; then
    if [[ -L "$target" || ! -f "$target" || -L "$state" || ! -f "$state" ]] || \
       [[ "$(cat "$state")" != "$expected" || "$(sha256sum "$target" | cut -d ' ' -f 1)" != "$expected" ]]; then
      echo "Refusing to retire unmanaged or modified content: $target" >&2
      exit 1
    fi
    if [[ -L "$archive_dir" || -e "$archive" || -L "$archive" ]]; then
      echo "Refusing to overwrite or redirect retired content: $archive" >&2
      exit 1
    fi
    if ! mkdir -p -- "$archive_dir" || ! mv -nT -- "$target" "$archive"; then
      echo "Could not retire $target to $archive as UID $EUID. Check the source and destination directory permissions." >&2
      exit 1
    fi
    if [[ -e "$target" || -L "$target" ]]; then
      echo "Could not retire content without overwriting: $archive" >&2
      exit 1
    fi
    echo "Retired $target to $archive"
  fi
  if [[ -f "$state" && ! -L "$state" && "$(cat "$state")" == "$expected" ]]; then
    rm -f -- "$state"
  fi
}

retire_gunpack feato-weapons-and-tactics.zip \
  e9983776641a5ffa95fef55198d91ff595faff1630934cb4bfa7d6a8c4666c10 \
  retired/feato-weapons-and-tactics.zip

# Older root-run maintenance may have left the shared retired directory unwritable.
retire_gunpack feato-classics-reborn.zip \
  2d0c082c234c7c30b40055225b518481d13fad9401c4c442f65fb5b04664f8df \
  retired-classics/feato-classics-reborn-1.1.4.zip

while IFS=$'\t' read -r relative expected url fallback; do
  [[ -z "$relative" || "$relative" == \#* ]] && continue
  if [[ ! "$relative" =~ ^(tacz/feato-[a-z0-9-]+\.zip|mods/feato-[a-z0-9-]+\.jar|monitoring/jmx_prometheus_javaagent-1\.7\.0\.jar|datapacks/feato-[a-z0-9-]+\.zip)$ || ! "$expected" =~ ^[0-9a-f]{64}$ || -z "$url" ]]; then
    echo "Invalid content lock entry: $relative" >&2
    exit 1
  fi
  if [[ "$relative" == datapacks/* ]]; then
    safe_dir "$data_dir/$world"
    safe_dir "$data_dir/$world/datapacks"
    target="$data_dir/$world/$relative"
    state="$state_dir/datapack__${world}__${relative#datapacks/}.sha256"
  else
    safe_dir "$data_dir/${relative%%/*}"
    target="$data_dir/$relative"
    state="$state_dir/${relative//\//_}.sha256"
  fi
  if [[ -L "$state" || -L "$state.tmp" || ( -e "$state" && ! -f "$state" ) || ( -e "$state.tmp" && ! -f "$state.tmp" ) ]]; then
    echo "Unsafe content state: $state" >&2; exit 1
  fi
  if [[ -L "$target" || ( -e "$target" && ! -f "$target" ) ]]; then
    echo "Refusing non-regular content path: $target" >&2
    exit 1
  fi
  current=''
  [[ ! -f "$target" ]] || current=$(sha256sum "$target" | cut -d ' ' -f 1)
  if [[ "$relative" == datapacks/* && -n "$current" && ( ! -f "$state" || "$(cat "$state")" != "$current" ) ]]; then
    echo "Refusing unmanaged or modified datapack: $target" >&2; exit 1
  fi
  if [[ "$current" != "$expected" ]]; then
    if [[ -n "$current" && ( ! -f "$state" || "$(cat "$state")" != "$current" ) ]]; then
      echo "Refusing to replace unmanaged or modified file: $target" >&2
      exit 1
    fi
    temp=$(mktemp "${target}.tmp.XXXXXXXX")
    trap 'rm -f -- "$temp"' EXIT
    download() {
      curl --fail --location --silent --show-error --retry 2 --connect-timeout 20 --max-time 300 \
        --header 'Accept: application/octet-stream' --output "$temp" "$1"
    }
    if ! download "$url"; then
      if [[ -z "$fallback" ]] || ! download "$fallback"; then
        echo "Download failed: $relative" >&2
        exit 1
      fi
    fi
    actual=$(sha256sum "$temp" | cut -d ' ' -f 1)
    if [[ "$actual" != "$expected" ]]; then
      echo "SHA-256 mismatch: $relative" >&2
      exit 1
    fi
    mv -f -- "$temp" "$target"
    trap - EXIT
  fi
  printf '%s\n' "$expected" > "$state.tmp"
  mv -f -- "$state.tmp" "$state"
done < "$lock_file"
