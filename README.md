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

## Initial Programs

- monitor_kills.py - This will be the main reader of the Zkill Redis stream
- watch_output.sh  - Is a temporary program to read output from Zkill redis to create a dataset to test monitor_kills.py against

### Pip Install

- csv
- json
- requests

## Config.json

Here is an example of the config.json file you need to create.

```
{
    "redis_queue_name": "BobTheWHGod",
    "regions": [ 10000047 ]
}
```

Where redis_queue_name is required by ZKill Redis to keep a queue for you. And you can provide a set of regions that you are interested in.  In the long run the program will only print out kills from those regions.

### Ignore victims.py

I saved some code for later, will destroy when done with it.


