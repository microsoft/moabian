#!/bin/bash

# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

set -euo pipefail

die() { ret=$?; printf "%s\n", "$@" >&2; exit "$ret"; }
[[ $EUID -eq 0 ]] || die "Must run $0 as root"

# change directories to the folder hosting this script
readonly _D="$(dirname "$(readlink -f "$0")")" && cd "$_D"

function info { 
    if tput colors &> /dev/null; then
        local color=$(tput smso)$(tput setaf 2) # inverse, green
        local reset=$(tput sgr0)
        printf "${color}○ %s ${reset}\n" "$1"
    else
        printf '%s\n' "$1"
    fi
}

info "Installing apt-get packages (root)" 

numpy=(
    nginx
)
echo "• installing: nginx"
apt-get install -qq --no-install-recommends ${numpy[*]}

# numpy https://www.piwheels.org/project/numpy/
numpy=(
    libatlas3-base
    libgfortran5
)
echo "• installing: numpy"
apt-get install -qq --no-install-recommends ${numpy[*]}

# OpenCV https://www.piwheels.org/project/opencv-contrib-python-headless/
# https://www.pyimagesearch.com/2019/09/16/install-opencv-4-on-raspberry-pi-4-and-raspbian-buster/
opencv=(
    libatk1.0-0
    libavcodec58
    libavformat58
    libavutil56
    libcairo2
    libcairo-gobject2
    libhdf5-dev
    libgdk-pixbuf2.0-0
    libgtk-3-0
    libilmbase23
    libjasper1
    libopenexr23
    libpango-1.0-0
    libpangocairo-1.0-0
    libswscale5
    libtiff5
    libwebp6
    libffi-dev
)
echo "• installing: opencv"
apt-get install -qq --no-install-recommends ${opencv[*]}
