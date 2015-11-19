import logging
from logging.handlers import RotatingFileHandler
from app import app

# specify format for log
formatter = logging.Formatter(
        "[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s")

# logging handler
fileHandler = RotatingFileHandler(app.config['LOG_FILE'],
                                  maxBytes=1024 * 1024 * 100,
                                  backupCount=20)

# set logging level for logger
fileHandler.setLevel(logging.ERROR)

# set formatter for logger
fileHandler.setFormatter(formatter)

# check if DEBUG=True is set or not
if app.debug is not True:
    # add logger if debug mode is off
    app.logger.addHandler(fileHandler)
