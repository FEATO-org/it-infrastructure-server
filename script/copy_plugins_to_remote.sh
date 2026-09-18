#!/usr/bin/env bash
set -Eeuo pipefail
shopt -s nullglob
cd "$(dirname "$0")/.."

: "${REMOTE_HOST:?Set REMOTE_HOST to the deployment node SSH destination}"
REMOTE_DEPLOY_ROOT="${REMOTE_DEPLOY_ROOT:-/opt/it-infrastructure-server}"
# Keep old ignored Data Packs out of the curated mount used by the Swarm stack.
datapacks=(minecraft/java/datapacks/*.zip)
texturepacks=(resources/minecraft/texturepacks/*.mcpack)
if (( ${#datapacks[@]} )); then
  scp "${datapacks[@]}" "${REMOTE_HOST}:${REMOTE_DEPLOY_ROOT}/minecraft/java/datapacks/"
fi
if (( ${#texturepacks[@]} )); then
  scp "${texturepacks[@]}" "${REMOTE_HOST}:${REMOTE_DEPLOY_ROOT}/resources/minecraft/texturepacks/"
fi
