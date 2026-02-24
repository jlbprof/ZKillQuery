#!/usr/bin/env python3

import csv
import json
import os
import sys

import requests
import time
import sqlite3

from pathlib import Path

from utils import setup_logger, get_data_dir, generate_timestamp, write_string_to_file, claim_file_from_queue, load_config

# global variables
config = {}

items_dict = {}
flags_dict = {}
solar_systems_dict = {}
regions_dict = {}
regions_to_record = {}
groups_dict = {}
categories_dict = {}

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
        logger.info(f"Unexpected error: 001 {e}")
        return False

def validate_sql_file(sql_file: Path, logger) -> bool:
    """Perform basic validation on the SQL file."""
    if not sql_file.exists():
        logger.info(f"Error: File {sql_file} does not exist")
        return False
    if sql_file.suffix.lower() != '.sql':
        logger.info("Warning: File extension is not .sql")
    return True

def initialize_database(db_path: str, sql_file: str, logger) -> bool:
    """Main function to initialize the database."""
    sql_path = Path(sql_file)
    
    if not validate_sql_file(sql_path, logger):
        return False

    conn = None
    try:
        logger.info(f"Initializing database at {sql_file}")
        conn = create_database_connection(db_path)
        success = execute_sql_file(conn, sql_path)
        logger.info(f"Initialized successfully {success}")
        return success
    finally:
        if conn is not None:
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

def csv_to_dict_try(csv_file_path, id_is_which_column, logger):
    item_dict = {}
    try:
        item_dict = csv_to_dict(csv_file_path, id_is_which_column)
    except Exception as e:
        logger.info(f"Unable to load {csv_file_path}")
        pass
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

def load_invTypes(conn, logger):
    logger.info("Inserting invTypes")
    data = []

    for row in items_dict.values():
        typeID = row[0]
        groupID = row[1]
        typeName = row[2]
        description = row[3]
        mass = row[4]
        volume = row[5]
        capacity = row[6]
        portionSize = row[7]
        raceID = row[8]
        basePrice = row[9]
        published = row[10]
        marketGroupID = row[11]
        iconID = row[12]
        soundID = row[13]
        graphicID = row[14]
        data.append((typeID, groupID, typeName, description, mass, volume, capacity, portionSize, raceID, basePrice, published, marketGroupID, iconID, soundID, graphicID))

    batch_insert(conn, 'invTypes', ['typeID', 'groupID', 'typeName', 'description', 'mass', 'volume', 'capacity', 'portionSize', 'raceID', 'basePrice', 'published', 'marketGroupID', 'iconID', 'soundID', 'graphicID'], data)
 
def load_invFlags(conn, logger):
    logger.info("Inserting invFlags")
    data = []

    for row in flags_dict.values():
        flagID = row[0]
        flagName = row[1]
        flagText = row[2]
        orderID = row[3]
        data.append((flagID, flagName, flagText, orderID))

    batch_insert(conn, 'invFlags', ['flagID', 'flagName', 'flagText', 'orderID'], data)
 
def load_regions(conn, logger):
    logger.info("Inserting invRegions")
    data = []

    for row in regions_dict.values():
        regionID = row[0]
        regionName = row[1]
        x = float(row[2]) if row[2] and row[2] != 'None' else None
        y = float(row[3]) if row[3] and row[3] != 'None' else None
        z = float(row[4]) if row[4] and row[4] != 'None' else None
        xMin = float(row[5]) if row[5] and row[5] != 'None' else None
        xMax = float(row[6]) if row[6] and row[6] != 'None' else None
        yMin = float(row[7]) if row[7] and row[7] != 'None' else None
        yMax = float(row[8]) if row[8] and row[8] != 'None' else None
        zMin = float(row[9]) if row[9] and row[9] != 'None' else None
        zMax = float(row[10]) if row[10] and row[10] != 'None' else None
        factionID = int(row[11]) if row[11] and row[11] != 'None' else None
        nebula = int(row[12]) if row[12] and row[12] != 'None' else None
        radius = float(row[13]) if row[13] and row[13] != 'None' else None
        data.append((regionID, regionName, x, y, z, xMin, xMax, yMin, yMax, zMin, zMax, factionID, nebula, radius))

    batch_insert(conn, 'regions', ['regionID', 'regionName', 'x', 'y', 'z', 'xMin', 'xMax', 'yMin', 'yMax', 'zMin', 'zMax', 'factionID', 'nebula', 'radius'], data)
 
def load_solar_systems(conn, logger):
    logger.info("Inserting inv_solar_systems")
    data = []

    for row in solar_systems_dict.values():
        solarSystemID = int(row[2]) if row[2] and row[2] != 'None' else None
        regionID = int(row[0]) if row[0] and row[0] != 'None' else None
        constellationID = int(row[1]) if row[1] and row[1] != 'None' else None
        solarSystemName = row[3]
        x = float(row[4]) if row[4] and row[4] != 'None' else None
        y = float(row[5]) if row[5] and row[5] != 'None' else None
        z = float(row[6]) if row[6] and row[6] != 'None' else None
        xMin = float(row[7]) if row[7] and row[7] != 'None' else None
        xMax = float(row[8]) if row[8] and row[8] != 'None' else None
        yMin = float(row[9]) if row[9] and row[9] != 'None' else None
        yMax = float(row[10]) if row[10] and row[10] != 'None' else None
        zMin = float(row[11]) if row[11] and row[11] != 'None' else None
        zMax = float(row[12]) if row[12] and row[12] != 'None' else None
        luminosity = float(row[13]) if row[13] and row[13] != 'None' else None
        border = int(row[14]) if row[14] and row[14] != 'None' else None
        fringe = int(row[15]) if row[15] and row[15] != 'None' else None
        corridor = int(row[16]) if row[16] and row[16] != 'None' else None
        hub = int(row[17]) if row[17] and row[17] != 'None' else None
        international = int(row[18]) if row[18] and row[18] != 'None' else None
        regional = int(row[19]) if row[19] and row[19] != 'None' else None
        constellation = int(row[20]) if row[20] and row[20] != 'None' else None
        security = float(row[21]) if row[21] and row[21] != 'None' else None
        factionID = int(row[22]) if row[22] and row[22] != 'None' else None
        radius = float(row[23]) if row[23] and row[23] != 'None' else None
        sunTypeID = int(row[24]) if row[24] and row[24] != 'None' else None
        securityClass = row[25]
        data.append((solarSystemID, regionID, constellationID, solarSystemName, x, y, z, xMin, xMax, yMin, yMax, zMin, zMax, luminosity, border, fringe, corridor, hub, international, regional, constellation, security, factionID, radius, sunTypeID, securityClass))

    batch_insert(conn, 'solar_systems', ['solarSystemID', 'regionID', 'constellationID', 'solarSystemName', 'x', 'y', 'z', 'xMin', 'xMax', 'yMin', 'yMax', 'zMin', 'zMax', 'luminosity', 'border', 'fringe', 'corridor', 'hub', 'international', 'regional', 'constellation', 'security', 'factionID', 'radius', 'sunTypeID', 'securityClass'], data)

def load_invGroups(conn, logger, data_dir):
    logger.info("Inserting invGroups")
    csv_file_path = data_dir + 'invGroups.csv'
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)  # Get column names
        for row in csv_reader:
            data.append(tuple(row))
    batch_insert(conn, 'invGroups', headers, data)

def load_invCategories(conn, logger, data_dir):
    logger.info("Inserting invCategories")
    csv_file_path = data_dir + 'invCategories.csv'
    data = []
    with open(csv_file_path, mode='r', encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file)
        headers = next(csv_reader)  # Get column names
        for row in csv_reader:
            data.append(tuple(row))
    batch_insert(conn, 'invCategories', headers, data)

def insert_droppedItem(conn, typeID, flagID, quantity, killmail_id):
    sql = f"INSERT INTO droppedItems (typeID, flagID, quantity, killmail_id) VALUES (?,?,?,?)"
    
    cursor = conn.cursor()
    try:
        cursor.execute(sql, [typeID, flagID, quantity, killmail_id])
        conn.commit()
        return cursor.rowcount
    except sqlite3.Error as e:
        conn.rollback()
        logger.info(f"ERROR E1 {e}")
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
        logger.info(f"ERROR X {e}")
        return 0

    logger.info("Unexpected Error")
    return 0

def init_database_only():
    """Initialize database with tables and reference data if needed"""
    global items_dict, flags_dict, solar_systems_dict, regions_dict, groups_dict, categories_dict
    
    data_dir_path = get_data_dir()
    data_dir = str(data_dir_path) + "/"
    
    log_file = data_dir + "zkill_db_init.log"
    logger = setup_logger("zkill_db_init", log_file=log_file, console=True)
    
    config = load_config(data_dir, logger)
    
    logger.info("Starting database initialization...")
    
    db_fname = data_dir + config["db_fname"]
    
    if os.path.exists(db_fname):
        logger.info("Database already exists, checking initialization...")
        try:
            conn = create_database_connection(str(db_fname))
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='killmails'")
            if cursor.fetchone():
                logger.info("Database is already initialized")
                conn.close()
                return
            else:
                logger.info("Database exists but tables missing, reinitializing...")
        except Exception as e:
            logger.info(f"Error checking database: {e}")
    
    logger.info("Creating and initializing database...")
    
    try:
        sql_file = "ZKillQuery_setup.sql"
        
        if initialize_database(db_fname, sql_file, logger):
            logger.info("Database schema created successfully!")
        else:
            logger.error("Failed to create database schema")
            sys.exit(1)
        
        conn = create_database_connection(db_fname)
        
        # Load reference data
        logger.info("Loading reference data...")
        
        items_dict = csv_to_dict_try(data_dir + 'invTypes.csv', 0, logger)
        flags_dict = csv_to_dict_try(data_dir + 'invFlags.csv', 0, logger)
        solar_systems_dict = csv_to_dict_try(data_dir + 'mapSolarSystems.csv', 2, logger)
        regions_dict = csv_to_dict_try(data_dir + 'mapRegions.csv', 0, logger)
        groups_dict = csv_to_dict_try(data_dir + 'invGroups.csv', 0, logger)
        categories_dict = csv_to_dict_try(data_dir + 'invCategories.csv', 0, logger)
        
        load_invTypes(conn, logger)
        load_invFlags(conn, logger)
        load_regions(conn, logger)
        load_solar_systems(conn, logger)
        load_invGroups(conn, logger, data_dir)
        load_invCategories(conn, logger, data_dir)
        
        conn.close()
        
        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)

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
        logger.info(message)

        if not region in regions_to_record:
            logger.info(f"Not Recorded {region}")
            return
        else:
            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
            logger.info(f"Recording {region}")
            logger.info("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

        ret = insert_killmail(conn, int(killmail_id), str(killmail_time), int(solar_system_id), int(ship_type_id))
        logger.info(f"RET :{ret}:")

        if ret == 0:
            logger.info(f"Not Recorded {region}")
            return

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
    # Nice the process to lower priority before starting work
    try:
        os.nice(10)  # Add 10 to nice value (lower priority)
    except PermissionError:
        pass  # Continue if we don't have permission to change priority
    
    data_dir_path = get_data_dir()
    data_dir = str(data_dir_path) + "/"

    log_file = data_dir + "zkill_consumer.log"
    logger = setup_logger ("zkill_consumer", log_file=log_file, console=True)

    config = load_config(data_dir, logger)
    redis_queue_name = config["redis_queue_name"]
    logger.info(f"Redis Queue: {redis_queue_name}")

    regions_string = ', '.join(str(region) for region in config["regions"])

    logger.info(f"Regions of Interest: {regions_string}")
    logger.info(f"DB Fname: {config['db_fname']}")

    for iRegion in config["regions"]:
        regions_to_record[str(iRegion)] = 1

    queue_dir = data_dir + "queue/"

    # Load reference data for processing
    items_dict = csv_to_dict_try(data_dir + 'invTypes.csv',0,logger)
    flags_dict = csv_to_dict_try(data_dir + 'invFlags.csv',0,logger)
    solar_systems_dict = csv_to_dict_try(data_dir + 'mapSolarSystems.csv',2,logger)
    regions_dict = csv_to_dict_try(data_dir + 'mapRegions.csv',0,logger)
    groups_dict = csv_to_dict_try(data_dir + 'invGroups.csv',0,logger)
    categories_dict = csv_to_dict_try(data_dir + 'invCategories.csv',0,logger)

    # Database should be initialized by zkill_db_init service
    db_fname = data_dir + config["db_fname"]
    logger.info(f"Connecting to database: {db_fname}")
    
    conn = create_database_connection(db_fname)
    logger.info("Database connected successfully")

    container_index = os.getenv('CONTAINER_INDEX', '1')
    hostname = os.getenv('HOSTNAME', 'unknown')
    # Generate unique consumer ID from container index and hostname
    consumer_id = f"zkill_consumer_{container_index}"
    
    # Add small random delay to stagger consumer startups
    import random
    import time
    time.sleep(random.uniform(0.5, 2.0))
    while True:
        try:
            logger.info(f"Consumer {consumer_id} checking queue")

            oldest_queued = None
            oldest_queued = claim_file_from_queue(queue_dir, consumer_id)
            if oldest_queued:
                logger.info(f"Consumer {consumer_id} claimed {oldest_queued}")

                data =  json.loads(oldest_queued.read_text())

                try:
                    killID = data['package']['killID']
                    kill_hash = data['package']['zkb']['hash']
                except Exception as e:
                    logger.info(f"Missing key in data: {e} - Skipping...")
                    oldest_queued.unlink()
                    continue

                url_template = "https://esi.evetech.net/latest/killmails/{zkillID}/{hash}/"
                url = url_template.format(zkillID=killID, hash=kill_hash)
                logger.info(f"Killmail info for url {killID} {kill_hash} {url}")

                response = requests.get(url, timeout=30)
                response.raise_for_status()

                data = response.json ()
                insert_zkill(conn, data)

                oldest_queued.unlink()
                logger.info(f"DELETED  ******** {oldest_queued}")
            else:
                logger.info("Queue is empty, sleeping ...")
                time.sleep(10)

        except requests.exceptions.RequestException as e:
            logger.info(f"Network error: {e} - Retrying in 10 seconds...")
            if oldest_queued and oldest_queued.exists():
                oldest_queued.unlink()
            time.sleep(10)  # Backoff to avoid hammering the API
        except json.JSONDecodeError as e:
            logger.info(f"JSON decode error: {e} - Skipping...")
            if oldest_queued and oldest_queued.exists():
                oldest_queued.unlink()
            continue
        except Exception as e:  # Catch-all for unexpected issues
            logger.info(f"Unexpected error: 002 {e}")
            if oldest_queued and oldest_queued.exists():
                oldest_queued.unlink()
            continue

