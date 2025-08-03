# In the Game EVE Online
## What Is Being Destroyed

This is a set of programs that monitor the output of zkillboards redis for kills as they happen.  It collates them and lists the ship type destroyed and all items destroyed and dropped.   You can then view the output and watch as it progresses.

## What you need

You need the following files from Fuzzworks, they don't change often but you should download them for yourself.

CSV Files you need to download into the main directory

- https://www.fuzzwork.co.uk/dump/latest/invTypes.csv
- https://www.fuzzwork.co.uk/dump/latest/invFlags.csv
- https://www.fuzzwork.co.uk/dump/latest/mapSolarSystems.csv
- https://www.fuzzwork.co.uk/dump/latest/mapRegions.csv

These files are git ignored.

## Program

- ZKillQuery.py

### Pip Install

- csv
- json
- requests
- time
- sqlite3
- Path
- Optional

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
- `regions`, are the regionID's that you are interested in.
- `db_fname`, is the sqlite db this is stored in.

## Files

- `ZKillQuery.py`, is the program
- `ZKillQuery.db`, is a db I use to play with the schema
- `ZKillQuery_setup.sql`, is the schema file used to initialize the database

## To Run

If you are just testing use `./test_init.sh` it will give you a new database.  Otherwise `./test.sh`.

`Cntrl-C` is the primary way to stop this.

## Observations

The redis stream is a going forward only stream, if your monitor is off you will miss the kills during that time.

I think in the future I will either package this as a persistent container and run with docker, or as a systemd service.  It should just run all the time.

## Notes:

`run_studio.sh` - I use to launch SQLiteStudio to observe the db in action.

I have not created any indices yet for this database as I am not sure how I am going to be querying it.   That is to come.

