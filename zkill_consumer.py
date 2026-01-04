#!/usr/bin/env python3

import csv
import json
import os
import sys

import requests
import time
import datetime
import sqlite3

from pathlib import Path
from typing import Optional

from utils import setup_logger, get_data_dir, generate_timestamp, write_string_to_file, get_file_from_queue

# global variables
config = {}

items_dict = {}
flags_dict = {}
solar_systems_dict = {}
regions_dict = {}
regions_to_record = {}

def create_database_connection(db_path: str) -> sqlite3.Connection:
    """Create and return a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn
    except sqlite3.Error as e:
        logger.info(f"Error connecting to database: {e}")
        raise

def execute_sql_file(conn: sqlite3.Connection, sql_file: Path) -> bool:
    """Execute SQL commands from a file within a transaction."""
    if not sql_file.is_file():
        logger.info(f"Error: SQL file not found at {sql_file}")
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
        logger.info(f"Error executing SQL script: {e}")
        return False
    except Exception as e:
        conn.rollback()
        logger.info(f"Unexpected error: {e}")
        return False

def validate_sql_file(sql_file: Path) -> bool:
    """Perform basic validation on the SQL file."""
    if not sql_file.exists():
        logger.info(f"Error: File {sql_file} does not exist")
        return False
    if sql_file.suffix.lower() != '.sql':
        logger.info("Warning: File extension is not .sql")
    return True

def initialize_database(db_path: str, sql_file: str) -> bool:
    """Main function to initialize the database."""
    sql_path = Path(sql_file)
    
    if not validate_sql_file(sql_path):
        return False

    try:
        logger.info("Initializing database at " + sql_file)
        conn = create_database_connection(db_path)
        success = execute_sql_file(conn, sql_path)
        logger.info("Initialized successfully " + str(success))
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
    logger.info("Inserting invTypes")
    data = []

    for row in items_dict.values():
        typeID = row[0]
        typeName = row[2]
        description = row[3]
        data.append((typeID, typeName, description))

    batch_insert(conn, 'invTypes', ['typeID', 'typeName', 'description'], data)
 
def load_invFlags(conn):
    logger.info("Inserting invFlags")
    data = []

    for row in flags_dict.values():
        flagID = row[0]
        flagName = row[1]
        flagText = row[2]
        data.append((flagID, flagName, flagText))

    batch_insert(conn, 'invFlags', ['flagID', 'flagName', 'flagText'], data)
 
def load_regions(conn):
    logger.info("Inserting invRegions")
    data = []

    for row in regions_dict.values():
        regionID = row[0]
        regionName = row[1]
        data.append((regionID, regionName))

    batch_insert(conn, 'regions', ['regionID', 'regionName'], data)
 
def load_solar_systems(conn):
    logger.info("Inserting inv_solar_systems")
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
        logger.info("ERROR E", e)
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
        logger.info("ERROR E", e)
        raise e

def insert_zkill(conn, data):
    try:
        killmail_id = data["killmail_id"]
        killmail_time = data["killmail_time"]
        solar_system_id = str(data["solar_system_id"])
        ship_type_id    = str(data["victim"]["ship_type_id"])

        items_list      = data["victim"]["items"]

        solar_system_name = solar_systems_dict[str(solar_system_id)][3]
        region            = str(solar_systems_dict[str(solar_system_id)][0])
        region_name       = regions_dict[region][1]

        ship_type_name    = items_dict[str(ship_type_id)][2]

        message = ship_type_name + " Killed in " + solar_system_name + "/" + region_name
        logger.info (message)

        if not region in regions_to_record:
            logger.info("Not Recorded " + region)
            return
        else:
            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            logger.info("Recording" + region)
            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        insert_killmail(conn, int(killmail_id), str(killmail_time), int(solar_system_id), int(ship_type_id))

        for item in items_list:
            item_type_id = item["item_type_id"]
            flag_id = item["flag"]

            try:
                x = items_dict[str(item_type_id)]
                item_name    = items_dict[str(item_type_id)][2]
                quantity     = 0
                if 'quantity_destroyed' in item:
                    quantity = item["quantity_destroyed"]
                else:
                    quantity = item["quantity_dropped"]

                count = insert_droppedItem(conn, item_type_id, flag_id, quantity, killmail_id)
            except KeyError as e:
                logger.info(f"Unable to find Key: {e}")
                pass

    except json.JSONDecodeError as e:
        logger.info(f"Invalid JSON: {e}")
        logger.info("Skipping line")
        return

    except KeyError as e:
        logger.info(f"Unable to determine ship type: {e}")
        logger.info("Skipping line")
        return

# ==============================================
# Main program execution starts here
# ==============================================
if __name__ == "__main__":
    data_dir = get_data_dir()
    log_file = data_dir + "zkill.log"
    logger = setup_logger ("zkill_listener", log_file=log_file, console=True)

    if os.path.exists(data_dir + 'config.json'):
        logger.info("Config Exists")
        try:
            with open(data_dir + 'config.json', 'r', encoding='utf-8') as file:
                config = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.info(f"Error loading config: {e}")
            sys.exit(1)

        logger.info("Redis Queue: " + config["redis_queue_name"])

        regions_string = ', '.join(str(region) for region in config["regions"])

        logger.info("Regions of Interest: " + regions_string)
        logger.info("DB FName:" + config["db_fname"])

        for iRegion in config["regions"]:
            regions_to_record[str(iRegion)] = 1

    else:
        logger.info("config.json does not exist")
        sys.exit(1)

    queue_dir = data_dir + "queue/"

    # Load the tables

    items_dict = csv_to_dict(data_dir + 'invTypes.csv',0)
    flags_dict = csv_to_dict(data_dir + 'invFlags.csv',0)
    solar_systems_dict = csv_to_dict(data_dir + 'mapSolarSystems.csv',2)
    regions_dict = csv_to_dict(data_dir + 'mapRegions.csv',0)

    # Do we need to create the database?

    db_fname = data_dir + config["db_fname"]
    sql_path = Path(db_fname)
    created = False

    if not os.path.exists(db_fname):
        try:
            sql_file = "ZKillQuery_setup.sql"

            if initialize_database(sql_path, sql_file):
                logger.info("Database initialized successfully!")
                created = True
            else:
                logger.info("Failed to initialize database.")
                exit(1)
        except KeyboardInterrupt:
            logger.info("\nOperation cancelled by user.")
            exit(1)
        except Exception as e:
            logger.info(f"An unexpected error occurred: {e}")
            exit(1)
    else:
        logger.info("Database already exists")

    conn = create_database_connection(sql_path)

    if created:
        load_invTypes(conn)
        load_invFlags(conn)
        load_regions(conn)
        load_solar_systems(conn)

    while True:
        try:
            logger.info("Checking Queue")

            oldest_queued = get_file_from_queue(queue_dir)
            if oldest_queued:
                logger.info("Oldest Queued " + oldest_queued.as_posix())

                data = json.loads(oldest_queued.read_text())
                killID = data['package']['killID']
                kill_hash = data['package']['zkb']['hash']

                url_template = "https://esi.evetech.net/latest/killmails/{zkillID}/{hash}/"
                url = url_template.format(zkillID=killID, hash=kill_hash)
                logger.info("Killmail info for url " + str(killID) + " " + kill_hash + " " + url)

                response = requests.get(url)
                response.raise_for_status()

                #print(response.text)

                data = response.json ()
                insert_zkill(conn, data)

                oldest_queued.unlink()
                logger.info("DELETED  ******** " + oldest_queued.as_posix())
            else:
                logger.info("Queue is empty, sleeping ...")
                time.sleep(10)

        except requests.exceptions.RequestException as e:
            print(f"Network error: {e} - Retrying in 10 seconds...")
            time.sleep(10)  # Backoff to avoid hammering the API
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e} - Skipping...")
            continue
        except Exception as e:  # Catch-all for unexpected issues
            print(f"Unexpected error: {e}")
            raise  # Re-raise to exit if critical, or handle as needed

