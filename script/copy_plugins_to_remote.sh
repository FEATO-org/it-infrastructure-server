#!/bin/bash
set -euxo pipefail
WORKDIR=$(pwd)
cd "$(dirname "$0")"

scp ../minecraft/plugins/downloads/* vps:~/src/it-infrastructure-server/minecraft/plugins/downloads
scp ../minecraft/packs/* vps:~/src/it-infrastructure-server/minecraft/packs
