#!/usr/bin/python3

import csv
import json
import os

# I have a set of csv files that contain relevant information for the queries.
# I could have put them in a database, but because of the simple streaming app this is
# it is easier just to create a dict of these csv files, as they are small

def csv_to_dict(csv_file_path, id_is_which_column):
    item_dict = {}
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)  # Skip header row
        for row in csv_reader:
            item_id = row[id_is_which_column]  # First column = ID
            item_dict[item_id] = row  # Store full row
    return item_dict

items_dict = csv_to_dict('invTypes.csv',0)
flags_dict = csv_to_dict('invFlags.csv',0)
solar_systems_dict = csv_to_dict('mapSolarSystems.csv',2)
regions_dict = csv_to_dict('mapRegions.csv',0)

# Now read in your configuration

if os.path.exists('config.json'):
    print("Config Exists")
    try:
        with open('config.json', 'r', encoding='utf-8') as file:
            config = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        os.exit(1)

    print("Redis Queue:", config["redis_queue_name"])
    print("Regions of Interest:", config["regions"])
    print("DB Output:", config["db_output"])

else:
    print("config.json does not exist")
    os.exit(1)

print("----------------------------------------------")
print("")

# OK for first iteration rather than reading directly from zkill redis, we will read from a data set
# data set is of the format jsonl, where each line is a syntactically correct json

with open(config["db_output"], 'a', encoding='utf-8') as output:
    csv_writer = csv.writer(output)
    with open('output.jsonl', 'r', encoding='utf-8') as file:
        for line in file:
            if line.strip():  # Checks if line is non-empty
                try:
                    data = json.loads(line)
                    killmail_id = data["package"]["killmail"]["killmail_id"]
                    killmail_time = data["package"]["killmail"]["killmail_time"]
                    solar_system_id = str(data["package"]["killmail"]["solar_system_id"])
                    ship_type_id    = str(data["package"]["killmail"]["victim"]["ship_type_id"])
                    items_list      = data["package"]["killmail"]["victim"]["items"]

                    solar_system_name = solar_systems_dict[solar_system_id][2]
                    region            = str(solar_systems_dict[solar_system_id][0])
                    region_name       = regions_dict[region][1]

                    print("Kill :", killmail_id, solar_system_name, region_name)
                    print("    ", items_dict[ship_type_id][2])
                    for item in items_list:
                        item_type_id = str(item["item_type_id"])
                        item_name    = items_dict[item_type_id][2]
                        quantity     = 0
                        if 'quantity_destroyed' in item:
                            quantity = item["quantity_destroyed"]
                        else:
                            quantity = item["quantity_dropped"]

                        print ("    ", "    ", item_name, quantity)

                        csv_writer.writerow( [killmail_id, killmail_time, solar_system_id, ship_type_id, item_type_id, quantity] )
                except json.JSONDecodeError as e:
                    print(f"Invalid JSON: {e}")
                    print("Skipping line")



