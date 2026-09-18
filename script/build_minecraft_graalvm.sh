#!/usr/bin/env bash
set -Eeuo pipefail
export DOCKER_BUILDKIT=1
readonly REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ -f "${ENV_FILE:-${REPO_ROOT}/.env}" ]]; then
  set -a
  source "${ENV_FILE:-${REPO_ROOT}/.env}"
  set +a
fi
server_image="${MINECRAFT_SERVER_IMAGE:-it-infrastructure/minecraft-server:java25-graalvm}"
docker build --pull --no-cache --build-arg BASE_IMAGE=itzg/minecraft-server:java25 \
  --tag "${server_image}" --file "${REPO_ROOT}/minecraft/Dockerfile.graalvm" "${REPO_ROOT}/minecraft"
