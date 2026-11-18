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
      "${REPO_ROOT}/fluentbit/forge-jvm.conf" \
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

# Select exactly one eligible node for the JVM scrape. Other global tasks keep
# their existing inputs but receive an empty JVM config from the Swarm template.
if ! forge_jvm_node_list=$(docker node ls --filter node.label=minecraft-data=true --format '{{.ID}}'); then
  echo 'Failed to list Swarm nodes for the Forge JVM scraper.' >&2
  exit 1
fi
forge_jvm_nodes=()
while IFS= read -r node_id; do
  [[ -z "$node_id" ]] || forge_jvm_nodes+=("$node_id")
done <<< "$forge_jvm_node_list"
if [[ ${#forge_jvm_nodes[@]} -eq 0 ]]; then
  echo 'No node has minecraft-data=true; cannot select the Forge JVM scraper.' >&2
  exit 1
fi
if [[ -z "${FORGE_JVM_SCRAPE_NODE_ID:-}" ]]; then
  if [[ ${#forge_jvm_nodes[@]} -ne 1 ]]; then
    echo 'Multiple minecraft-data nodes: set FORGE_JVM_SCRAPE_NODE_ID to one eligible node ID.' >&2
    exit 1
  fi
  FORGE_JVM_SCRAPE_NODE_ID=${forge_jvm_nodes[0]}
fi
if [[ "$FORGE_JVM_SCRAPE_NODE_ID" != disabled && ! " ${forge_jvm_nodes[*]} " == *" ${FORGE_JVM_SCRAPE_NODE_ID} "* ]]; then
  echo 'FORGE_JVM_SCRAPE_NODE_ID must be the full ID of a minecraft-data=true node or disabled.' >&2
  exit 1
fi
export FORGE_JVM_SCRAPE_NODE_ID

forge_jvm_config="system_forge_jvm_template_${CONFIG_VERSION}"
if docker config inspect "$forge_jvm_config" >/dev/null 2>&1; then
  existing_driver=$(docker config inspect --format '{{.Spec.Templating.Name}}' "$forge_jvm_config")
  existing_hash=$(docker config inspect --format '{{json .Spec.Data}}' "$forge_jvm_config" | tr -d '"' | base64 -d | sha256sum | awk '{print $1}')
  expected_hash=$(sha256sum "${REPO_ROOT}/fluentbit/forge-jvm.conf" | awk '{print $1}')
  if [[ "$existing_driver" != golang || "$existing_hash" != "$expected_hash" ]]; then
    echo "Existing config does not match template: $forge_jvm_config" >&2
    exit 1
  fi
else
  docker config create --template-driver golang "$forge_jvm_config" "${REPO_ROOT}/fluentbit/forge-jvm.conf" >/dev/null
fi

external_networks=(
  database-network
  web-ingress-network
  minecraft-ingress-network
  minecraft-backend-network
  forge-jvm-monitoring-network
)

for network_name in "${external_networks[@]}"; do
  if ! docker network inspect "${network_name}" >/dev/null 2>&1; then
    network_options=(--driver overlay --opt encrypted)
    if [[ "${network_name}" != forge-jvm-monitoring-network ]]; then
      network_options+=(--attachable)
    fi
    docker network create "${network_options[@]}" "${network_name}" >/dev/null
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
