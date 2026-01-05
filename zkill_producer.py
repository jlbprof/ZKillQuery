#!/usr/bin/env python3

import json
import os
import sys

import requests
import time

from pathlib import Path
from typing import Optional

from utils import setup_logger, get_data_dir, generate_timestamp, write_string_to_file, load_config

# global variables
config = {}

# ==============================================
# Main program execution starts here
# ==============================================
if __name__ == "__main__":
    data_dir_path = get_data_dir()
    data_dir = str(data_dir_path) + "/"

    log_file = data_dir + "zkill.log"
    logger = setup_logger ("zkill_listener", log_file=log_file, console=True)

    config = load_config(data_dir, logger)

    queue_dir = data_dir + "queue/"
    try:
        Path(queue_dir).mkdir(parents=True, exist_ok=True)
    except Exception as e:  # Catch-all for unexpected issues
        logger.info(f"Unexpected exception creating directory, {e}")
        sys.exit(1)

    # Sit in a loop and accept notifications from Zkillmails RedisQ

    while True:
        try:
            logger.info("Waiting on Listener")
            response = requests.get("https://zkillredisq.stream/listen.php?queueID=" + config["redis_queue_name"], stream=True, timeout=180)
            logger.info("Response from Listener")
            response.raise_for_status()
            data = response.json()
            pretty_json = json.dumps(data, indent=4)
            logger.info(pretty_json)

            filename = queue_dir + generate_timestamp() + ".json"
            logger.info(filename)
            write_string_to_file(filename, pretty_json)
        except requests.exceptions.RequestException as e:
            logger.info(f"Network error: {e} - Retrying in 10 seconds...")
            time.sleep(10)  # Backoff to avoid hammering the API
        except json.JSONDecodeError as e:
            logger.info(f"JSON decode error: {e} - Skipping...")
            continue
        except Exception as e:  # Catch-all for unexpected issues
            logger.info(f"Unexpected error: {e}")
            raise  # Re-raise to exit if critical, or handle as needed

