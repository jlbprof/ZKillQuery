# In the Game EVE Online
## What Is Being Destroyed

This is a set of programs that monitor the output of zkillboards redis for kills as they happen.  It collates them and lists the ship type destroyed and all items destroyed and dropped.   You can then view the output and watch as it progresses.

## What you need

You need the following files from Fuzzwork, they don't change often but you should download them for yourself.

CSV Files you need to download into the main directory

- https://www.fuzzwork.co.uk/dump/latest/invTypes.csv
- https://www.fuzzwork.co.uk/dump/latest/invFlags.csv
- https://www.fuzzwork.co.uk/dump/latest/mapSolarSystems.csv
- https://www.fuzzwork.co.uk/dump/latest/mapRegions.csv
- https://www.fuzzwork.co.uk/dump/latest/invGroups.csv
- https://www.fuzzwork.co.uk/dump/latest/invCategories.csv

I added a directory csvDownloads with a script to perform the downloads.  You need to manually copy
them to your data directory.

These files are git ignored.

## Programs

- zkill_producer.py
- zkill_consumer.py

### Pip Install

- requirements.txt

## Config.json

Here is an example of the config.json file you need to create.

```
{
    "redis_queue_name": "BobTheWHGod",
    "regions": [ 10000047 ],
    "db_fname": "db_zkill_query.db"
}
```

- `redis_queue_name` is required by ZKill Redis to keep a queue for you
- `regions`, are the region IDs that you are interested in.
- `db_fname`, is the sqlite db this is stored in.

## Notable Files

- `ZKillQuery.db`, is a db I use to play with the schema
- `ZKillQuery_setup.sql`, is the schema file used to initialize the database

## To Run

`./zkill_producer.py` in one terminal
`./zkill_consumer.py` in another

Run producer and consumer concurrently for real-time processing.  Make sure you have $HOME/ZKillQueryData setup

It needs:

- config.json
- *.csv (see csvDownloads dir)
- and a queue directory

## Container Setup with Podman Compose

To run in containers:

1. Ensure `compose.yaml` is present (example below).
2. `podman-compose build`
3. `podman-compose up -d` (detached mode).

Example `compose.yaml`:
```yaml
version: '3.8'
services:
  zkill_producer:
    build: .
    command: python zkill_producer.py
   volumes:
      - ./ZKillQueryData:/app/ZKillQueryData
    restart: unless-stopped

  zkill_consumer:
    build: .
    command: python zkill_consumer.py
    volumes:
      - ./ZKillQueryData:/app/ZKillQueryData
    restart: unless-stopped
```

Requires Dockerfile in the repo root.

## Systemd Auto-Start

For auto-start on boot, create ~/.config/systemd/user/podman-compose-zkill.service:

```
[Unit]
Description=ZKill Podman Compose
After=network.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=podman-compose -f %h/ZKillQuery/compose.yaml up -d
ExecStop=podman-compose -f %h/ZKillQuery/compose.yaml down
WorkingDirectory=%h/ZKillQuery

[Install]
WantedBy=default.target
```


Then:
- systemctl --user daemon-reload
- systemctl --user enable podman-compose-zkill
- systemctl --user start podman-compose-zkill

%h is the user's home directory.

## Cleanup

To stop and clean: podman-compose down --rmi local || true

 It needs:
 
 - config.json
 
I have implemented containerization with podman compose and systemd auto-start as described above.

