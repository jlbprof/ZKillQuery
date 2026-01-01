#!/bin/bash

set -x

# Stop and remove any existing container (safe cleanup)
podman stop zkillquery-run || true
podman rm zkillquery-run || true

# Remove old image if exists
podman rmi localhost/zkillquery:latest || true

# Build the new image
podman build -t localhost/zkillquery:latest .

# Ensure Quadlet directory exists (one-time setup)
mkdir -p ~/.config/containers/systemd

# (Optional) Copy your Quadlet file here if it's not already in place
cp zkillquery.container ~/.config/containers/systemd/

# Reload systemd to detect the Quadlet
systemctl --user daemon-reload

# Enable for auto-start on boot/login
systemctl --user enable zkillquery.service

# Start (or restart) the container via systemd
systemctl --user start zkillquery.service

