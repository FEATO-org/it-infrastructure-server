#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob
cd "$(dirname "$0")/.."

: "${REMOTE_HOST:?Set REMOTE_HOST to the deployment node SSH destination}"
REMOTE_DEPLOY_ROOT="${REMOTE_DEPLOY_ROOT:-/opt/it-infrastructure-server}"
# Java public downloads and inactive Geyser extensions retain their separate distribution path.
java_resourcepacks=(resources/minecraft/resourcepacks/java/*.zip)
geyser_extensions=(resources/minecraft/geyser/extensions/*.jar)

if [[ ! "$REMOTE_DEPLOY_ROOT" =~ ^/[A-Za-z0-9._/-]+$ ]]; then
  echo "REMOTE_DEPLOY_ROOT must be an absolute path containing only letters, digits, '.', '_', '-', and '/'." >&2
  exit 1
fi

ssh "$REMOTE_HOST" mkdir -p -- \
  "$REMOTE_DEPLOY_ROOT/resources/minecraft/resourcepacks/java" \
  "$REMOTE_DEPLOY_ROOT/resources/minecraft/geyser/extensions"

if (( ${#java_resourcepacks[@]} )); then
  scp "${java_resourcepacks[@]}" "${REMOTE_HOST}:${REMOTE_DEPLOY_ROOT}/resources/minecraft/resourcepacks/java/"
fi
if (( ${#geyser_extensions[@]} )); then
  scp "${geyser_extensions[@]}" "${REMOTE_HOST}:${REMOTE_DEPLOY_ROOT}/resources/minecraft/geyser/extensions/"
fi
