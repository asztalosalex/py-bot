import logging
from logging.handlers import RotatingFileHandler
import os

# Könyvtár létrehozása
if not os.path.exists('logs'):
    os.makedirs('logs')

def setup_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)
    
    # Minden logger ugyanazt a fájlt használja
    file_handler = logging.FileHandler('logs/error.log', encoding='utf-8')
    
    formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(name)s: %(message)s')
    file_handler = RotatingFileHandler(
        'logs/error.log',
        maxBytes=1024*1024,
        encoding='utf-8'
    )

    file_handler.setFormatter(formatter)
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger