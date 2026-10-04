"""
Logging configuration for the EnToolkit package.
"""
import logging
import logging.handlers

from .constants import LOG_FILE_NAME, LOG_MAX_SIZE_MB


def init_logger():
    """Initializes the entoolkit logger.
    
    Sets up a RotatingFileHandler that preserves the previous session 
    by rolling over on startup, and limits file size to LOG_MAX_SIZE_MB.
    """
    logger = logging.getLogger("entoolkit")
    
    # Avoid multiple registrations
    if logger.handlers:
        return logger
    
    logger.setLevel(logging.INFO)
    
    max_bytes = int(LOG_MAX_SIZE_MB * 1024 * 1024)
    
    # RotatingFileHandler keeps only the current log when backupCount is 0
    handler = logging.handlers.RotatingFileHandler(
        LOG_FILE_NAME, 
        maxBytes=max_bytes, 
        backupCount=0, 
        encoding='utf-8'
    )
    
            
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    logger.info("EnToolkit logger initialized (Size limit: %d MB)", LOG_MAX_SIZE_MB)
    
    return logger
