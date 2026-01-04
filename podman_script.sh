#!/bin/bash

set -x

./podman_cleanup.sh

podman-compose build
podman-compose up -d

