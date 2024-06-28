#!/bin/bash
set -euxo pipefail
WORKDIR=$(pwd)
cd "$(dirname "$0")"

# scp ../resources/minecraft/plugins/* root@vps:/extras/plugins
scp ../resources/minecraft/datapacks/* root@vps:/extras/datapacks
# scp ../resources/minecraft/resourcepacks/* root@vps:/extras/resourcepacks
scp ../resources/minecraft/texturepacks/* root@vps:/extras/texturepacks
