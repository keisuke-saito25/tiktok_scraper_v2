import logging
import os
import config
from modules.constants import LOG_FORMAT, LOG_DATE_FORMAT

def setup_logging():
    log_dir = os.path.dirname(config.LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        filename=config.LOG_FILE_PATH,
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT
    )