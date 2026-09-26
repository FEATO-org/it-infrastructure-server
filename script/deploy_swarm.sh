#!/usr/bin/env bash
set -Eeuo pipefail

readonly SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly REPO_ROOT="$(cd -- "${SCRIPT_DIR}/.." && pwd)"

ENV_FILE="${ENV_FILE:-${REPO_ROOT}/.env}"
TLS_STATE_FILE="${TLS_STATE_FILE:-/var/lib/swarm-certbot/swarm-secrets.env}"

if [[ -f "${ENV_FILE}" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${ENV_FILE}"
  set +a
fi

if [[ -f "${TLS_STATE_FILE}" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "${TLS_STATE_FILE}"
  set +a
fi

export DEPLOY_ROOT="${DEPLOY_ROOT:-${REPO_ROOT}}"
export MINECRAFT_ASSET_ROOT="${MINECRAFT_ASSET_ROOT:-${DEPLOY_ROOT}/resources/minecraft}"

if [[ -z "${CONFIG_VERSION:-}" ]]; then
  CONFIG_VERSION="$(
    sha256sum \
      "${REPO_ROOT}/fluentbit/fluent-bit.conf" \
      "${REPO_ROOT}/fluentbit/parsers.conf" \
      "${REPO_ROOT}/fluentbit/discord.lua" \
      "${REPO_ROOT}/nginx/nginx.conf" \
      "${REPO_ROOT}/nginx/http.d/public.conf" \
      "${REPO_ROOT}/nginx/stream.d/minecraft.conf" |
      sha256sum |
      awk '{print substr($1,1,16)}'
  )"
fi
export CONFIG_VERSION

if [[ "$(docker info --format '{{.Swarm.ControlAvailable}}')" != "true" ]]; then
  echo "Run this script on a Swarm manager." >&2
  exit 1
fi

required_variables=(
  DISCORD_TOKEN
  GUILD_IDS
  APP_MODE
  NOTIFY_CHANNEL_ID
  NOTIFY_WEBHOOK_URL
  ERROR_WEBHOOK_URL
  LOKI_USER_ID
  PROM_USER_ID
  GRAFANA_API_KEY
  TLS_FULLCHAIN_SECRET
  TLS_PRIVATE_KEY_SECRET
)

for variable_name in "${required_variables[@]}"; do
  if [[ -z "${!variable_name:-}" ]]; then
    echo "Required environment variable is not set: ${variable_name}" >&2
    exit 1
  fi
done

external_networks=(
  database-network
  web-ingress-network
  minecraft-ingress-network
  minecraft-backend-network
)

for network_name in "${external_networks[@]}"; do
  if ! docker network inspect "${network_name}" >/dev/null 2>&1; then
    docker network create \
      --driver overlay \
      --attachable \
      --opt encrypted \
      "${network_name}" >/dev/null
    echo "Created overlay network: ${network_name}"
  fi
done

required_secrets=(
  mariadb_root_password
  mariadb_app_password
  forwarding_secret
  floodgate_key
  rcon_password
  minecraft_proxy_rcon_password
  luckperms_db_password
  cloudflare_tunnel_token
  "${TLS_FULLCHAIN_SECRET}"
  "${TLS_PRIVATE_KEY_SECRET}"
)

for secret_name in "${required_secrets[@]}"; do
  if ! docker secret inspect "${secret_name}" >/dev/null 2>&1; then
    echo "Required Swarm secret does not exist: ${secret_name}" >&2
    exit 1
  fi
done

for stack_file in \
  "${REPO_ROOT}/deploys/app/compose.yml" \
  "${REPO_ROOT}/deploys/system/compose.yml" \
  "${REPO_ROOT}/deploys/infra/compose.yml"; do
  docker compose --file "${stack_file}" config --quiet
  docker stack config --compose-file "${stack_file}" >/dev/null
done

docker stack deploy \
  --compose-file "${REPO_ROOT}/deploys/infra/compose.yml" \
  --with-registry-auth \
  --prune \
  infra

docker stack deploy \
  --compose-file "${REPO_ROOT}/deploys/app/compose.yml" \
  --with-registry-auth \
  --prune \
  app

docker stack deploy \
  --compose-file "${REPO_ROOT}/deploys/system/compose.yml" \
  --with-registry-auth \
  --prune \
  system

docker stack services infra
docker stack services app
docker stack services system
