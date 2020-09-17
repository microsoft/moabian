#!/bin/bash

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

pyfile="$1"       # first argument is the python to run in docker
rest="${@:2}"     # remaining arguments $2 -> $n

docker run \
    --name scriptrunner \
    --mount type=bind,source="$PWD",target=/app/scripts,readonly \
    --privileged --rm -it \
    moab/control python3 /app/scripts/"$pyfile" "$rest"
