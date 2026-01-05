#!/bin/bash

set -x

./podman_cleanup.sh

podman-compose build

# No longer necessary if you are using systemd
#podman-compose up -d

