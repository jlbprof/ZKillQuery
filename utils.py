# utils.py

import logging
import sys
import os
import json

from datetime import datetime, timezone

from pathlib import Path

def setup_logger(
    name: str,
    log_file: str | Path | None = "app.log",
    level: int = logging.INFO,
    console: bool = True
) -> logging.Logger:
    """
    Set up a logger with a unique name and consistent formatting.
    
    Args:
        name: Unique identifier for the script/component (e.g., "REDIS_LISTENER")
        log_file: Path to log file. If None, no file logging.
        level: Logging level (default INFO)
        console: Whether to also log to console
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid adding handlers multiple times (important when importing in multiple modules)
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    if console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)  # Ensure directory exists
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def get_data_dir(
    container_path: str = "/app/ZKillQueryData/",
    local_path: str | None = None
) -> Path:
    """
    Determine the appropriate data directory for ZKillQuery.
    
    Priority:
    1. Container path (default: /app/ZKillQueryData/)
    2. Local user path: $HOME/ZKillQueryData/ (or custom if provided)
    
    Returns:
        Path object pointing to the existing data directory.
    
    Exits the program with an error message if neither directory exists.
    """
    # Convert to Path objects for easier handling
    container_dir = Path(container_path)
    
    if container_dir.exists():
        print(f"DATA_DIR is {container_dir}")
        return container_dir
    
    # Fallback to local home directory
    home = os.getenv('HOME')
    if home is None:
        print("Error: HOME environment variable not set.")
        sys.exit(1)
    
    local_dir = Path(local_path) if local_path else Path(home) / "ZKillQueryData"
    
    if local_dir.exists():
        return local_dir
    
    # Neither exists
    print(f"Unable to access data directory.")
    print(f"   Tried container path: {container_path}")
    print(f"   Tried local path:     {local_dir}")
    print("")
    print("Please create one of these directories and ensure it contains required data.")
    sys.exit(1)

def generate_timestamp() -> str:
    now = datetime.now(timezone.utc)
    sortable_timestamp = now.strftime("%Y-%m-%d-%H-%M-%S-%f")  # .%f gives microseconds
    return sortable_timestamp

def write_string_to_file(filename: str, content: str) -> None:
    """
    Overwrites the file with the given string content.
    
    Args:
        filename: Path to the file
        content: String to write
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)

def claim_file_from_queue(directory: str | Path, consumer_id: str) -> Path | None:
    """
    Atomically claims the oldest file from the queue by renaming it.
    This prevents multiple consumers from processing same file.
    
    Args:
        directory: Path to the queue directory
        consumer_id: Unique identifier for the consumer
        
    Returns:
        Path to the claimed file (with processing suffix), or None if no files available
    """
    import os
    import time
    
    dir_path = Path(directory)
    
    max_attempts = 3  # Try to claim files multiple times
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        
        # Refresh file list on each attempt
        files = sorted([
            f for f in dir_path.iterdir() 
            if f.is_file() and not f.name.startswith('.') and '.processing-' not in f.name
        ])
        
        if not files:
            return None
        
        # Try to claim a file
        for oldest_file in files:
            claimed_file = oldest_file.with_name(f"{oldest_file.name}.processing-{consumer_id}")
            
            try:
                # Atomic rename - only one consumer can succeed
                oldest_file.rename(claimed_file)
                return claimed_file
            except (FileExistsError, FileNotFoundError):
                # Another consumer already claimed this file or it disappeared
                continue  # Try next file
            except PermissionError:
                # Temporary filesystem issue, wait briefly and retry
                time.sleep(0.1)
                try:
                    oldest_file.rename(claimed_file)
                    return claimed_file
                except (FileExistsError, FileNotFoundError, PermissionError):
                    continue
        
        # If we get here, all files were claimed by others, wait and retry
        if attempt < max_attempts:
            time.sleep(0.5 * attempt)  # Increasing backoff
    
    return None
    
    # Try to claim a file with retry logic
    for oldest_file in files:
        claimed_file = oldest_file.with_name(f"{oldest_file.name}.processing-{consumer_id}")
        
        try:
            # Atomic rename - only one consumer can succeed
            oldest_file.rename(claimed_file)
            return claimed_file
        except (FileExistsError, FileNotFoundError):
            # Another consumer already claimed this file or it disappeared
            continue  # Try the next file
        except PermissionError:
            # Temporary filesystem issue, wait briefly and retry
            time.sleep(0.1)
            try:
                oldest_file.rename(claimed_file)
                return claimed_file
            except (FileExistsError, FileNotFoundError, PermissionError):
                continue
    
    return None

def get_file_from_queue(directory: str | Path) -> Path | None:
    """
    Returns the alphabetically oldest file in the directory,
    or None if the directory is empty or contains no files.
    
    Args:
        directory: Path to the directory
        
    Returns:
        Path to the oldest file, or None if no files
    """
    dir_path = Path(directory)
    
    # Get all files (not directories) and sort them by name
    files = sorted(dir_path.iterdir(), key=lambda p: p.name)
    
    # Filter to only actual files (exclude subdirectories)
    files_only = [f for f in files if f.is_file()]
    
    if not files_only:
        # You can return None, raise an exception, or do something else here
        return None
    
    oldest_file = files_only[0]
    return oldest_file

def load_config(data_dir, logger): 
    config = {}

    if os.path.exists(data_dir + 'config.json'):
        config_fname = data_dir + 'config.json'
        logger.info("Config Exists :" + config_fname + ":")
        try:
            with open(config_fname, 'r', encoding='utf-8') as file:
                config = json.load(file)
        except Exception as e:
            logger.info(f"Error loading config: {e}")
            sys.exit(1)

    else:
        logger.info("config.json does not exist")
        sys.exit(1)

    return config

