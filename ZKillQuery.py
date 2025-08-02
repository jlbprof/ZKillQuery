#!/usr/bin/env python3

import csv
import json
import os

import sqlite3
from pathlib import Path
from typing import Optional

# global variables
config = {}

items_dict = {}
flags_dict = {}
solar_systems_dict = {}
regions_dict = {}

def create_database_connection(db_path: str) -> sqlite3.Connection:
    """Create and return a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        raise

def execute_sql_file(conn: sqlite3.Connection, sql_file: Path) -> bool:
    """Execute SQL commands from a file within a transaction."""
    if not sql_file.is_file():
        print(f"Error: SQL file not found at {sql_file}")
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
        print(f"Error executing SQL script: {e}")
        return False
    except Exception as e:
        conn.rollback()
        print(f"Unexpected error: {e}")
        return False

def validate_sql_file(sql_file: Path) -> bool:
    """Perform basic validation on the SQL file."""
    if not sql_file.exists():
        print(f"Error: File {sql_file} does not exist")
        return False
    if sql_file.suffix.lower() != '.sql':
        print("Warning: File extension is not .sql")
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
 
# ==============================================
# Main program execution starts here
# ==============================================
if __name__ == "__main__":
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
        print("DB FName:", config["db_fname"])

    else:
        print("config.json does not exist")
        os.exit(1)

    # Load the tables

    items_dict = csv_to_dict('invTypes.csv',0)
    flags_dict = csv_to_dict('invFlags.csv',0)
    solar_systems_dict = csv_to_dict('mapSolarSystems.csv',2)
    regions_dict = csv_to_dict('mapRegions.csv',0)

    # Do we need to create the database?

    db_fname = config["db_fname"]
    sql_path = Path(config["db_fname"])
    created = False

    if not os.path.exists(db_fname):
        try:
            sql_file = "ZKillQuery_setup.sql"

            if initialize_database(sql_path, sql_file):
                print("Database initialized successfully!")
                created = True
            else:
                print("Failed to initialize database.")
                exit(1)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user.")
            exit(1)
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            exit(1)
    else:
        print("Database already exists")

    conn = create_database_connection(sql_path)

    if created:
        load_invTypes(conn)
        load_invFlags(conn)
        load_regions(conn)
        load_solar_systems(conn)


