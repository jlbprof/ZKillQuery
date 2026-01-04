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

Run producer and consumer concurrently for real-time processing.

# Make sure you have $HOME/ZKillQueryData setup

It needs:

- config.json
- *.csv (see csvDownloads dir)
- and a queue directory

## Observations

The redis stream is a forward only stream, if your monitor is off you will miss the kills during that time.

I think in the future I will either package this as a persistent container and run with docker, or as a systemd service.  It should just run all the time.

