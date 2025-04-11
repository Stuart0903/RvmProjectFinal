import logging
import os
from ..config.settings import Settings

def setup_logging(settings: Settings):
    os.makedirs(os.path.dirname(settings.LOG_FILE), exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format=settings.LOG_FORMAT,
        handlers=[
            logging.FileHandler(settings.LOG_FILE),
            logging.StreamHandler()
        ]
    )