#!/bin/bash

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

pyfile="$1"       # first argument is the python to run in docker
rest="${@:2}"     # remaining arguments $2 -> $n
config="${MOABDIR:-/home/pi/moab}/config"

docker run \
    --name scriptrunner \
    --mount type=bind,source="$PWD",target=/app/scripts,readonly \
    --mount type=bind,source="$config",target=/app/config \
    --privileged --rm -it \
    moab/control python3 /app/scripts/"$pyfile" $rest
