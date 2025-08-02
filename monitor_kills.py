#!/usr/bin/python3

import csv

# I have a set of csv files that contain relevant information for the queries.
# I could have put them in a database, but because of the simple streaming app this is
# it is easier just to create a dict of these csv files, as they are small

def csv_to_dict(csv_file_path, id_is_which_column):
    item_dict = {}
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)  # Skip header row
        for row in csv_reader:
            item_id = row[0]  # First column = ID
            item_dict[item_id] = row  # Store full row
    return item_dict

items_dict = csv_to_dict('invTypes.csv',0)
flags_dict = csv_to_dict('invFlags.csv',0)
solar_systems_dict = csv_to_dict('mapSolarSystems.csv',2)
regions_dict = csv_to_dict('mapRegions.csv',0)

print (items_dict['587'])



