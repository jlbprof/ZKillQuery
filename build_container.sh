#!/bin/bash

set -x

# Cleanup old container/image (optional but safe)
podman stop zkillquery-run || true
podman rm zkillquery-run || true
podman rmi localhost/zkillquery:latest || true

# Build the image
podman build -t localhost/zkillquery:latest .

# Ensure Quadlet directory and file are in place
mkdir -p ~/.config/containers/systemd
cp zkillquery.container ~/.config/containers/systemd/

# Reload systemd user daemon to pick up the new/updated Quadlet
systemctl --user daemon-reload
sleep 5
systemctl --user daemon-reload
sleep 5
systemctl --user list-unit-files | grep zkillquery

# IMPORTANT: Use the correct Quadlet service name
systemctl --user enable container-zkillquery-run.service   # <-- fixed name
systemctl --user restart container-zkillquery-run.service  # restart = stop old + start new
# Or just start if it wasn't running:
# systemctl --user start container-zkillquery.service

