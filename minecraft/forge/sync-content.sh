#!/usr/bin/env bash
set -euo pipefail

# Stable names identify only files managed by this script. Never remove other files.
data_dir=${1:-/data}
lock_file=${2:-/forge-pack/content.lock}
state_dir="$data_dir/.feato-content"
mkdir -p "$state_dir"

# Retire only the previously pinned and recorded Weapons and Tactics ZIP.
legacy="$data_dir/tacz/feato-weapons-and-tactics.zip"
legacy_state="$state_dir/tacz_feato-weapons-and-tactics.zip.sha256"
legacy_hash=e9983776641a5ffa95fef55198d91ff595faff1630934cb4bfa7d6a8c4666c10
archive="$state_dir/retired/feato-weapons-and-tactics.zip"
if [[ -e "$legacy" || -L "$legacy" ]]; then
  if [[ -L "$legacy" || ! -f "$legacy" || -L "$legacy_state" || ! -f "$legacy_state" ]] || \
     [[ "$(cat "$legacy_state")" != "$legacy_hash" || "$(sha256sum "$legacy" | cut -d ' ' -f 1)" != "$legacy_hash" ]]; then
    echo "Refusing to retire unmanaged or modified content: $legacy" >&2
    exit 1
  fi
  mkdir -p "$state_dir/retired"
  if [[ -e "$archive" || -L "$archive" ]]; then
    echo "Refusing to overwrite retired content: $archive" >&2
    exit 1
  fi
  mv -- "$legacy" "$archive"
fi
if [[ ! -e "$legacy" && ! -L "$legacy" && -f "$legacy_state" && ! -L "$legacy_state" ]] && \
   [[ "$(cat "$legacy_state")" == "$legacy_hash" ]]; then
  rm -- "$legacy_state"
fi

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
