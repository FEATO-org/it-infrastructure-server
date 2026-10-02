#!/usr/bin/env bash
set -Eeuo pipefail
echo "deploy_swarm.sh now bootstraps infra only; update app/system in Portainer." >&2
exec "$(dirname -- "${BASH_SOURCE[0]}")/bootstrap_swarm.sh" "$@"
