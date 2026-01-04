#!/bin/bash

cp -f podman-compose-zkill.service ~/.config/systemd/user/podman-compose-zkill.service

systemctl --user daemon-reload
sleep 5
systemctl --user daemon-reload
sleep 5

systemctl --user enable podman-compose-zkill
systemctl --user start podman-compose-zkill

