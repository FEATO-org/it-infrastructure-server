#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 /path/to/ValhallaMMO.jar" >&2
  exit 2
fi

repo_root=$(cd "$(dirname "$0")/.." && pwd)
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT
main_url=https://gist.githubusercontent.com/LenTakayama/e8f65dbce8e58baec96c8554a4eba4e5/raw/ja-jp.json
materials_url=https://gist.githubusercontent.com/LenTakayama/e8f65dbce8e58baec96c8554a4eba4e5/raw/materials-ja-jp.json

curl --fail --silent --show-error --location "$main_url" -o "$tmp_dir/ja-jp.json"
curl --fail --silent --show-error --location "$materials_url" -o "$tmp_dir/materials-ja-jp.json"
python3 "$repo_root/script/validate_valhallammo_translation.py" \
  "$1" "$tmp_dir/ja-jp.json" "$tmp_dir/materials-ja-jp.json"
install -m 0644 "$tmp_dir/ja-jp.json" \
  "$repo_root/minecraft/java/plugins/ValhallaMMO/languages/ja-jp.json"
install -m 0644 "$tmp_dir/materials-ja-jp.json" \
  "$repo_root/minecraft/java/plugins/ValhallaMMO/languages/materials/ja-jp.json"
echo "ValhallaMMO Japanese translations updated after validation."
