import os
import logging
from logging.handlers import RotatingFileHandler

from valutatrade_hub.infra.settings import SettingsLoader


def setup_logging():
    settings = SettingsLoader()
    log_file = settings.get("log_file")
    log_format = settings.get("log_format")
    
    dir_name = os.path.dirname(log_file)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    
    logger = logging.getLogger("valutatrade")
    logger.setLevel(logging.INFO)
    
    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=3, encoding="utf-8")
        formatter = logging.Formatter(log_format, datefmt="%Y-%m-%dT%H:%M:%S")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        
    return logger
