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

- zkill_producer.py - Fetches killmail data from zKillboard Redis queue
- zkill_consumer.py - Processes killmails and stores in SQLite database
- zkill_db_init() - Database initialization function (called by init container)

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

### Local Development
`./zkill_producer.py` in one terminal
`./zkill_consumer.py` in another

Run producer and consumer concurrently for real-time processing.  Make sure you have $HOME/ZKillQueryData setup

It needs:

- config.json
- *.csv (see csvDownloads dir)
- and a queue directory

### Container Setup (Recommended)
The container setup includes:
- **Multiple consumers** (3 by default) for parallel processing
- **Database initialization** handled automatically by init container
- **Race condition prevention** with atomic file operations
- **Auto-scaling** - just change `replicas` in compose.yaml

## Container Setup with Podman Compose

To run in containers:

1. Ensure `compose.yaml` is present.
2. `podman-compose build`
3. `podman-compose up -d` (detached mode).

The compose setup includes:
- **zkill_db_init**: Initializes database with schema and reference data
- **zkill_producer**: Fetches killmails from zKillboard Redis queue
- **zkill_consumer**: Multiple instances (3 by default) process killmails concurrently
- **Automatic scaling**: Change `replicas: 3` to desired number of consumers

Key features:
- **Race condition prevention**: Atomic file operations prevent duplicate processing
- **Database safety**: Init container ensures database is ready before consumers start
- **Multi-consumer load balancing**: Consumers compete for files without conflicts

### Systemd Auto-Start

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
- `systemctl --user daemon-reload`
- `systemctl --user enable podman-compose-zkill`
- `systemctl --user start podman-compose-zkill`

%h is the user's home directory.

## Convenience Scripts

**`./podman_script.sh`** - Setup and start the service
**`./podman_cleanup.sh`** - Stop and clean up containers

## Scaling Consumers

To change the number of consumer containers:

1. Edit `compose.yaml`
2. Change `replicas: 3` under `zkill_consumer` service to your desired number
3. Restart: `systemctl --user restart podman-compose-zkill`

## Monitoring

- Each consumer logs with its unique ID (from container hostname)
- Database initialization logs to `zkill_db_init.log`
- Consumer logs to `zkill_consumer.log`
- Producer logs to `zkill_producer.log`

## Architecture

```
zKillboard Redis → Producer → File Queue (timestamped files)
                                     ↓
                              3+ Consumers (parallel)
                                     ↓
                              SQLite Database
```

The multi-consumer setup provides better throughput while preventing duplicate processing through atomic file operations.

