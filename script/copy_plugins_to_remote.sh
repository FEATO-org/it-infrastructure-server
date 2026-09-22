#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob
cd "$(dirname "$0")/.."

: "${REMOTE_HOST:?Set REMOTE_HOST to the deployment node SSH destination}"
REMOTE_DEPLOY_ROOT="${REMOTE_DEPLOY_ROOT:-/opt/it-infrastructure-server}"
# Keep old ignored Data Packs out of the curated mount used by the Swarm stack.
datapacks=(minecraft/java/datapacks/*.zip)
java_resourcepacks=(resources/minecraft/resourcepacks/java/*.zip)
bedrock_resourcepacks=(
  resources/minecraft/resourcepacks/bedrock/*.mcpack
  resources/minecraft/resourcepacks/bedrock/*.zip
)
geyser_custom_mappings=(resources/minecraft/geyser/custom_mappings/*.json)

if [[ ! "$REMOTE_DEPLOY_ROOT" =~ ^/[A-Za-z0-9._/-]+$ ]]; then
  echo "REMOTE_DEPLOY_ROOT must be an absolute path containing only letters, digits, '.', '_', '-', and '/'." >&2
  exit 1
fi

ssh "$REMOTE_HOST" mkdir -p -- \
  "$REMOTE_DEPLOY_ROOT/resources/minecraft/resourcepacks/java" \
  "$REMOTE_DEPLOY_ROOT/resources/minecraft/resourcepacks/bedrock" \
  "$REMOTE_DEPLOY_ROOT/resources/minecraft/geyser/custom_mappings"

if (( ${#datapacks[@]} )); then
  scp "${datapacks[@]}" "${REMOTE_HOST}:${REMOTE_DEPLOY_ROOT}/minecraft/java/datapacks/"
fi
if (( ${#java_resourcepacks[@]} )); then
  scp "${java_resourcepacks[@]}" "${REMOTE_HOST}:${REMOTE_DEPLOY_ROOT}/resources/minecraft/resourcepacks/java/"
fi
if (( ${#bedrock_resourcepacks[@]} )); then
  scp "${bedrock_resourcepacks[@]}" "${REMOTE_HOST}:${REMOTE_DEPLOY_ROOT}/resources/minecraft/resourcepacks/bedrock/"
fi
if (( ${#geyser_custom_mappings[@]} )); then
  scp "${geyser_custom_mappings[@]}" "${REMOTE_HOST}:${REMOTE_DEPLOY_ROOT}/resources/minecraft/geyser/custom_mappings/"
fi
