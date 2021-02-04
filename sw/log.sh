#!/usr/bin/env bash

mkdir -p /tmp/logs

# start 3 brains
docker-compose -f just-brains.yml up -d

trap cleanup INT

cleanup () {
    docker-compose -f just-brains.yml down
    wc -l /tmp/logs/log.csv
}

sudo python3 -u main.py -t 1 2> /tmp/logs/log.csv
