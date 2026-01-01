#!/bin/bash

set -x

podman stop zkillquery-run
podman rm zkillquery-run

podman rmi zkillquery
podman build -t zkillquery .

podman run --name zkillquery-run -v ~/ZKillQueryData:/app/ZKillQueryData zkillquery


