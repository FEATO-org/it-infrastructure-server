#!/usr/bin/env bash
set -euo pipefail

mapfile -t containers < <(docker ps -q --filter label=com.docker.swarm.service.name=app_minecraft-server)
if [ "${#containers[@]}" -ne 1 ]; then
  echo "Run on the minecraft-data node; expected exactly one app_minecraft-server task, found ${#containers[@]}." >&2
  exit 1
fi

container_id=${containers[0]}

rcon() {
  docker exec "$container_id" rcon-cli "$1"
}

# mayor is an auxiliary social-role group, not a replacement primary group.
rcon "lp creategroup mayor"
rcon "lp group mayor permission set feato.mayor true"
rcon "lp group mayor meta setprefix 100 &9[村長] "

echo "Mayor role configured: group 'mayor', permission 'feato.mayor', prefix '[村長]'."
echo "Assign with: lp user <player> parent add mayor"
echo "Remove with: lp user <player> parent remove mayor"
