#!/bin/bash
set -euxo pipefail
WORKDIR=$(pwd)
cd "$(dirname "$0")"

scp ../minecraft/plugins/*.jar vps:~/src/it-infrastructure-server/minecraft/plugins
scp ../minecraft/plugins/Geyser-Spigot/packs/* vps:~/src/it-infrastructure-server/minecraft/plugins/Geyser-Spigot/packs
scp ../minecraft/datapacks/* vps:~/src/it-infrastructure-server/minecraft/datapacks
