#!/bin/bash

set -x

podman-compose down || true

IMAGES=$(podman images | grep zkill | awk '{print $3}')
if [ -n "$IMAGES" ]; then
    echo "$IMAGES" | xargs podman rmi -f || true
fi

