#!/usr/bin/env bash
set -euo pipefail

# Stable names identify only files managed by this script. Never remove other files.
data_dir=${1:-/data}
lock_file=${2:-/forge-pack/content.lock}
state_dir="$data_dir/.feato-content"
mkdir -p "$state_dir"

while IFS=$'\t' read -r relative expected url fallback; do
  [[ -z "$relative" || "$relative" == \#* ]] && continue
  if [[ ! "$relative" =~ ^(tacz/feato-[a-z0-9-]+\.zip|mods/feato-[a-z0-9-]+\.jar)$ || ! "$expected" =~ ^[0-9a-f]{64}$ || -z "$url" ]]; then
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
