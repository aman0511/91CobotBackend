# -*- coding: utf-8 -*-
# Standard Library Imports
import logging
import os
from logging.handlers import RotatingFileHandler

# Third Party Imports
import config as conf

# Local Imports

# create logger
logger = logging.getLogger("api")
logger.setLevel(logging.DEBUG)

# create file handler which logs even debug messages
LOG_PATH = getattr(conf, "LOG_FILE_PATH") or os.getcwd()
FILE_PATH = LOG_PATH + '/91cobotbackend-app-access.log'
fh = RotatingFileHandler(FILE_PATH, maxBytes=5242880)
fh.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - '
                              '%(funcName)s - %(message)s',
                              datefmt='%m-%d-%Y %I:%M:%S %p')

# add formatter to handlers
ch.setFormatter(formatter)
fh.setFormatter(formatter)

# add handlers to logger
logger.addHandler(ch)
logger.addHandler(fh)
