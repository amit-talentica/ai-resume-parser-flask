import logging
import os
from config.settings import LOG_DIR, LOG_LEVEL

# Define log file path
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Configure logging
logging.basicConfig(
    filename=LOG_FILE,
    level=LOG_LEVEL,
    format=LOG_FORMAT,
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Console handler for real-time logging
console_handler = logging.StreamHandler()
console_handler.setLevel(LOG_LEVEL)
console_handler.setFormatter(logging.Formatter(LOG_FORMAT))

# Get root logger and attach handlers
logger = logging.getLogger()
logger.addHandler(console_handler)

logger.info("Logging system initialized successfully.")
