import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "uspto_sync.log")

# Formatter: timestamps, log level, app id, email subject
formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(name)s | App:%(application_number)s | Customer:%(customer_number)s | Subject:%(email_subject)s | %(message)s"
)

# Rotating file handler: 5MB per file, keep 5 backups
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5)
file_handler.setFormatter(formatter)

# Root logger config
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)