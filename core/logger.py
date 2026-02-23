import logging
import os
from pathlib import Path

# Constants for logging
LOG_NAME = "mtree"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_log_file():
    """Returns the path to the log file in the user's temp directory."""
    import tempfile
    return Path(tempfile.gettempdir()) / "mtree_addon.log"

def setup_logger():
    """Configures the logger to write to both console and a temp file."""
    logger = logging.getLogger(LOG_NAME)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(LOG_FORMAT)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # File handler
    try:
        fh = logging.FileHandler(get_log_file(), mode='w', encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception as e:
        print(f"Failed to setup file logging: {e}")

    return logger

def get_logger():
    return logging.getLogger(LOG_NAME)
