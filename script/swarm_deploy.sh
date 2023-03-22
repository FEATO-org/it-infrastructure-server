#!/bin/bash
set -euxo pipefail
WORKDIR=$(pwd)
cd "$(dirname "$0")"
ARG=""

if [ "$#" == 2 ]
then
  ARG="$1"
fi

if [ "${ARG}" == "prune" ]
then
  docker stack deploy -c ../compose.yml --prune stack
else
 docker stack deploy -c ../compose.yml stack
fi
