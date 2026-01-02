#!/usr/bin/env python3

import csv
import json
import os
import sys

import requests
import time

import logging

import sqlite3
from pathlib import Path
from typing import Optional

# global variables
config = {}

items_dict = {}
flags_dict = {}
solar_systems_dict = {}
regions_dict = {}
regions_to_record = {}

data_dir = '/app/ZKillQueryData/'

if not os.path.exists(data_dir):
    # The datadir does not exist, alternative path is $HOME/ZKillQueryData
    data_dir = os.getenv('HOME') + "/ZKillQueryData/"

if not os.path.exists(data_dir):
    print(f"Unable to access data_dir :" + data_dir + ":")
    sys.exit(1)

print("DATA_DIR is " + data_dir)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(data_dir + 'run.log'),
        logging.StreamHandler()  # Also to stdout/journal
    ]
)

sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)

def create_database_connection(db_path: str) -> sqlite3.Connection:
    """Create and return a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn
    except sqlite3.Error as e:
        logging.info(f"Error connecting to database: {e}")
        raise

def execute_sql_file(conn: sqlite3.Connection, sql_file: Path) -> bool:
    """Execute SQL commands from a file within a transaction."""
    if not sql_file.is_file():
        logging.info(f"Error: SQL file not found at {sql_file}")
        return False

    try:
        cursor = conn.cursor()
        with open(sql_file, 'r') as f:
            sql_script = f.read()
        
        cursor.executescript(sql_script)
        conn.commit()
        return True
    except sqlite3.Error as e:
        conn.rollback()
        logging.info(f"Error executing SQL script: {e}")
        return False
    except Exception as e:
        conn.rollback()
        logging.info(f"Unexpected error: {e}")
        return False

def validate_sql_file(sql_file: Path) -> bool:
    """Perform basic validation on the SQL file."""
    if not sql_file.exists():
        logging.info(f"Error: File {sql_file} does not exist")
        return False
    if sql_file.suffix.lower() != '.sql':
        logging.info("Warning: File extension is not .sql")
    return True

def initialize_database(db_path: str, sql_file: str) -> bool:
    """Main function to initialize the database."""
    sql_path = Path(sql_file)
    
    if not validate_sql_file(sql_path):
        return False

    try:
        conn = create_database_connection(db_path)
        success = execute_sql_file(conn, sql_path)
        return success
    finally:
        if 'conn' in locals():
            conn.close()

def csv_to_dict(csv_file_path, id_is_which_column):
    item_dict = {}
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)  # Skip header row
        for row in csv_reader:
            item_id = row[id_is_which_column]  # First column = ID
            item_dict[item_id] = row  # Store full row
    return item_dict

def batch_insert(conn, table, columns, data):
    """
    conn: SQLite connection
    table: Table name (str)
    columns: List of column names (list/tuple)
    data: Sequence of parameter sequences
    """
    placeholders = ', '.join(['?'] * len(columns))
    columns_str = ', '.join(columns)
    sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
    
    cursor = conn.cursor()
    try:
        cursor.executemany(sql, data)
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        conn.rollback()
        raise e

def load_invTypes(conn):
    data = []

    for row in items_dict.values():
        typeID = row[0]
        typeName = row[2]
        description = row[3]
        data.append((typeID, typeName, description))

    batch_insert(conn, 'invTypes', ['typeID', 'typeName', 'description'], data)
 
def load_invFlags(conn):
    data = []

    for row in flags_dict.values():
        flagID = row[0]
        flagName = row[1]
        flagText = row[2]
        data.append((flagID, flagName, flagText))

    batch_insert(conn, 'invFlags', ['flagID', 'flagName', 'flagText'], data)
 
def load_regions(conn):
    data = []

    for row in regions_dict.values():
        regionID = row[0]
        regionName = row[1]
        data.append((regionID, regionName))

    batch_insert(conn, 'regions', ['regionID', 'regionName'], data)
 
def load_solar_systems(conn):
    data = []

    for row in solar_systems_dict.values():
        regionID = row[0]
        solarSystemID = row[2]
        solarSystemName = row[3]
        data.append((solarSystemID, regionID, solarSystemName))

    batch_insert(conn, 'solar_systems', ['solarSystemID', 'regionID', 'solarSystemName'], data)

def insert_droppedItem(conn, typeID, flagID, quantity, killmail_id):
    sql = f"INSERT INTO droppedItems (typeID, flagID, quantity, killmail_id) VALUES (?,?,?,?)"
    
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [typeID, flagID, quantity, killmail_id])
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        conn.rollback()
        logging.info("ERROR E", e)
        raise e

def insert_killmail(conn, killmail_id, xtime, solarSystemID, ship_type_id):
    sql = f"INSERT INTO killmails (killmail_id, time, solarSystemID, ship_type_id) VALUES (?,?,?,?)"
    
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [killmail_id, xtime, solarSystemID, ship_type_id])
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        conn.rollback()
        logging.info("ERROR E", e)
        raise e

def insert_zkill(conn, data):
    try:
        killmail_id = data["package"]["killmail"]["killmail_id"]
        killmail_time = data["package"]["killmail"]["killmail_time"]
        solar_system_id = str(data["package"]["killmail"]["solar_system_id"])
        ship_type_id    = str(data["package"]["killmail"]["victim"]["ship_type_id"])

        items_list      = data["package"]["killmail"]["victim"]["items"]

        solar_system_name = solar_systems_dict[str(solar_system_id)][3]
        region            = str(solar_systems_dict[str(solar_system_id)][0])
        region_name       = regions_dict[region][1]

        logging.info("KILL " + "Ship: (" + items_dict[str(ship_type_id)][2] + ") " + "System: (" + solar_system_name + ")", "Region: (" + region_name + ")")

        if not region in regions_to_record:
            logging.info("Not Recorded " + region)
            return
        else:
            logging.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            logging.info("Recording" + region)
            logging.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        insert_killmail(conn, int(killmail_id), str(killmail_time), int(solar_system_id), int(ship_type_id))

        for item in items_list:
            item_type_id = item["item_type_id"]
            flag_id = item["flag"]
            x = items_dict[str(item_type_id)]
            item_name    = items_dict[str(item_type_id)][2]
            quantity     = 0
            if 'quantity_destroyed' in item:
                quantity = item["quantity_destroyed"]
            else:
                quantity = item["quantity_dropped"]

            count = insert_droppedItem(conn, item_type_id, flag_id, quantity, killmail_id)

    except json.JSONDecodeError as e:
        logging.info(f"Invalid JSON: {e}")
        logging.info("Skipping line")
        return

# ==============================================
# Main program execution starts here
# ==============================================
if __name__ == "__main__":
    if os.path.exists(data_dir + 'config.json'):
        logging.info("Config Exists")
        try:
            with open(data_dir + 'config.json', 'r', encoding='utf-8') as file:
                config = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.info(f"Error loading config: {e}")
            sys.exit(1)

        logging.info("Redis Queue: " + config["redis_queue_name"])

        regions_string = ', '.join(str(region) for region in config["regions"])

        logging.info("Regions of Interest: " + regions_string)
        logging.info("DB FName:" + config["db_fname"])

        for iRegion in config["regions"]:
            regions_to_record[str(iRegion)] = 1

    else:
        logging.info("config.json does not exist")
        sys.exit(1)

    # Load the tables

    items_dict = csv_to_dict(data_dir + 'invTypes.csv',0)
    flags_dict = csv_to_dict(data_dir + 'invFlags.csv',0)
    solar_systems_dict = csv_to_dict(data_dir + 'mapSolarSystems.csv',2)
    regions_dict = csv_to_dict(data_dir + 'mapRegions.csv',0)

    # Do we need to create the database?

    db_fname = config["db_fname"]
    sql_path = Path(config["db_fname"])
    created = False

    if not os.path.exists(db_fname):
        try:
            sql_file = "ZKillQuery_setup.sql"

            if initialize_database(sql_path, sql_file):
                logging.info("Database initialized successfully!")
                created = True
            else:
                logging.info("Failed to initialize database.")
                exit(1)
        except KeyboardInterrupt:
            logging.info("\nOperation cancelled by user.")
            exit(1)
        except Exception as e:
            logging.info(f"An unexpected error occurred: {e}")
            exit(1)
    else:
        logging.info("Database already exists")

    conn = create_database_connection(sql_path)

    if created:
        load_invTypes(conn)
        load_invFlags(conn)
        load_regions(conn)
        load_solar_systems(conn)

    # Sit in a loop and accept notifications from Zkillmails RedisQ

    while True:
        try:
            response = requests.get("https://zkillredisq.stream/listen.php?queueID=" + config["redis_queue_name"], stream=True)
            response.raise_for_status()
            data = response.json()
            logging.info(data)
            insert_zkill(conn, data)
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e} - Retrying in 10 seconds...")
            time.sleep(10)  # Backoff to avoid hammering the API
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e} - Skipping...")
            continue
        except Exception as e:  # Catch-all for unexpected issues
            print(f"Unexpected error: {e}")
            raise  # Re-raise to exit if critical, or handle as needed

