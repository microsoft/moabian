#!/usr/bin/env bash
# vim:ft=sh ts=4 sw=4 et

set -euo pipefail
die()     { ret=$?; printf '%s\n' "$@" >&2; exit "$ret"; }
require() { hash "$@" || return -1; }

readonly _D="$(dirname "$(readlink -f "$0")")" && cd "$_D"

[[ $EUID -eq 0 ]] || die "$0 script needs to run as root. Try sudo $0"


brain_paths() {
    docker-compose config | grep "image:" | sed -r 's/.*image: (.+)/\1/'
}

brain_sha() {
    docker inspect "$1" | grep Id | sed -r 's/.*:([a-z0-9]*)",/\1/'
}

save_brains() {
    require "docker"
    require "docker-compose"

    if grep "MOABIAN=2" /etc/environment;  then
		return -1
	fi

    local p=$(brain_paths)

    mkdir --parents /tmp/brains

    for i in $p; do
        sha=$(brain_sha "$i")
        sha4=${sha:0:4}

        echo "docker save $sha4 > /tmp/brains/$sha4.tar.gz"
        docker save $sha4 > /tmp/brains/$sha4.tar.gz
    done
}

uninstall_docker_ce () {
    require "docker"
	if [[ $(docker --version | grep -i azure) ]]; then
		echo "Moby installed... "
		docker --version
	fi

    # stop everything before continuing
    systemctl stop menu brain docker iotedge || true

    # purge apt packages
    apt-get purge -y docker-ce docker-ce-cli
    apt-get autoremove -y --purge docker-ce docker-ce-cli

    # purge all docker related files
    rm -rf /var/lib/docker /etc/docker
    rm -rf /etc/apparmor.d/docker
    #groupdel docker
    rm -rf /var/run/docker.sock

    # remove docker ethernet bridge
    ifconfig docker0 down
    ip link delete docker0
}


load_brains () {
	echo "load_brains()"
	# test for /tmp/brains first
	return -1 # if it doesn't exist
}

add_moby_keys() {
    curl https://packages.microsoft.com/config/debian/stretch/multiarch/prod.list > /etc/apt/sources.list.d/microsoft.list
    curl https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/trusted.gpg.d/microsoft.gpg
    apt-get update --allow-releaseinfo-change -y
}

install_moby () {
    apt-get install moby-engine -y
    usermod -aG docker pi
}

install_docker_compose () {
    if ! command -v docker-compose &> /dev/null; then
        pip3 install docker-compose
    fi
}


load_brains() {
    if [[ -d /tmp/brains ]]; then
        for i in /tmp/brains/*; do
            docker load < $i
        done
    fi
}

download_default_brain () {
    wget https://github.com/microsoft/moabian/releases/download/v.2.4.0/brain.77b0.tar.gz -O /tmp/brain.tar.gz
    docker load < /tmp/brain.tar.gz
    docker tag 77b0 moab/brain:latest
}


#save_brains || true
#uninstall_docker_ce || true
#add_moby_keys
#install_moby
#sudo systemctl start docker
load_brains
download_default_brain


