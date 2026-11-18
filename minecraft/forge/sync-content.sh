#!/usr/bin/env bash
set -euo pipefail

# Stable names identify only files managed by this script. Never remove other files.
data_dir=${1:-/data}
lock_file=${2:-/forge-pack/content.lock}
state_dir="$data_dir/.feato-content"
mkdir -p "$state_dir"

# Retire only ZIPs that match both the former pin and the active management record.
retire_gunpack() {
  local filename=$1 expected=$2 archive_name=$3
  local target="$data_dir/tacz/$filename"
  local state="$state_dir/tacz_${filename}.sha256"
  local archive="$state_dir/retired/$archive_name"

  if [[ -e "$target" || -L "$target" ]]; then
    if [[ -L "$target" || ! -f "$target" || -L "$state" || ! -f "$state" ]] || \
       [[ "$(cat "$state")" != "$expected" || "$(sha256sum "$target" | cut -d ' ' -f 1)" != "$expected" ]]; then
      echo "Refusing to retire unmanaged or modified content: $target" >&2
      exit 1
    fi
    if [[ -L "$state_dir/retired" || -e "$archive" || -L "$archive" ]]; then
      echo "Refusing to overwrite or redirect retired content: $archive" >&2
      exit 1
    fi
    mkdir -p "$state_dir/retired"
    mv -nT -- "$target" "$archive"
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
  feato-weapons-and-tactics.zip
retire_gunpack feato-classics-reborn.zip \
  2d0c082c234c7c30b40055225b518481d13fad9401c4c442f65fb5b04664f8df \
  feato-classics-reborn-1.1.4.zip

while IFS=$'\t' read -r relative expected url fallback; do
  [[ -z "$relative" || "$relative" == \#* ]] && continue
  if [[ ! "$relative" =~ ^(tacz/feato-[a-z0-9-]+\.zip|mods/feato-[a-z0-9-]+\.jar|monitoring/jmx_prometheus_javaagent-1\.7\.0\.jar)$ || ! "$expected" =~ ^[0-9a-f]{64}$ || -z "$url" ]]; then
    echo "Invalid content lock entry: $relative" >&2
    exit 1
  fi
  target="$data_dir/$relative"
  state="$state_dir/${relative//\//_}.sha256"
  mkdir -p "$(dirname "$target")"
  if [[ -L "$target" || ( -e "$target" && ! -f "$target" ) ]]; then
    echo "Refusing non-regular content path: $target" >&2
    exit 1
  fi
  current=''
  [[ ! -f "$target" ]] || current=$(sha256sum "$target" | cut -d ' ' -f 1)
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
