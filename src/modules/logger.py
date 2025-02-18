import logging
import os
import config
import sys
from modules.constants import LOG_FORMAT, LOG_DATE_FORMAT

def setup_logging():
    log_dir = os.path.dirname(config.LOG_FILE_PATH)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE_PATH),
            logging.StreamHandler(sys.stdout)
        ]
    )