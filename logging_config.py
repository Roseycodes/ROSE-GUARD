import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = os.path.join(os.getenv('APPDATA'), 'ROSE GUARD', 'logs')
try:
    os.makedirs(LOG_DIR, exist_ok=True)
except PermissionError:
    # Fallback to user's home directory if AppData is not accessible
    LOG_DIR = os.path.join(os.path.expanduser('~'), '.roseguard', 'logs')
    os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, 'roseguard.log')

def configure_logging(level=logging.INFO):
    try:
        logger = logging.getLogger()
        logger.setLevel(level)

        # Remove any existing handlers
        logger.handlers = []

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logger.addHandler(ch)

        # Rotating file handler
        try:
            fh = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8')
            fh.setLevel(level)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s'))
            logger.addHandler(fh)
            logger.debug('Logging configured, logs -> %s', LOG_FILE)
        except (PermissionError, OSError) as e:
            logger.warning('Failed to set up file logging: %s', str(e))
            logger.warning('Continuing with console logging only')

        return logger
    except Exception as e:
        print(f"Failed to configure logging: {str(e)}")
        return logging.getLogger()
