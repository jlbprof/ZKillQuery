#!/usr/bin/env python3

import csv
import json
import os
import sys

import requests
import time
import datetime
import sqlite3

import logging

from pathlib import Path
from typing import Optional

from utils import setup_logger, get_data_dir, generate_timestamp, write_string_to_file

# global variables
config = {}

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

    else:
        logger.info("config.json does not exist")
        sys.exit(1)

    queue_dir = data_dir + "queue/"

    # Sit in a loop and accept notifications from Zkillmails RedisQ

    while True:
        try:
            logger.info("Waiting on Listener")
            response = requests.get("https://zkillredisq.stream/listen.php?queueID=" + config["redis_queue_name"], stream=True)
            logger.info("Response from Listener")
            response.raise_for_status()
            data = response.json()
            pretty_json = json.dumps(data, indent=4)
            logger.info(pretty_json)

            filename = queue_dir + generate_timestamp() + ".json"
            logger.info(filename)
            write_string_to_file(filename, pretty_json)
        except requests.exceptions.RequestException as e:
            print(f"Network error: {e} - Retrying in 10 seconds...")
            time.sleep(10)  # Backoff to avoid hammering the API
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e} - Skipping...")
            continue
        except Exception as e:  # Catch-all for unexpected issues
            print(f"Unexpected error: {e}")
            raise  # Re-raise to exit if critical, or handle as needed

