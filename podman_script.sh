#!/bin/bash

set -x

podman-compose down || true
podman images | grep zkill | awk '{print $3}' | xargs podman rmi || true

podman-compose build
podman-compose up -d

