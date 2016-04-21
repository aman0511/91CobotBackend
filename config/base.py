# common set up which will use in all case
import os

SECRET_KEY = '311bdbb47de9f01d352535685df764886c87623293e20fe0'
basedir = os.path.abspath(os.path.dirname(__file__))

# MYSQL for dev
SQLALCHEMY_DATABASE_URI = os.environ.get('COBOT_DB_URL',
                                         "mysql://root:p1@localhost/91Cobot")

# cobot constants
COBOT_TOKEN = os.getenv('COBOT_TOKEN', None)
MEMBERSHIPS_URL_STR = 'http://%s.cobot.me/api/memberships'

# Flask-Cache settings
CACHE_DEFAULT_TIMEOUT = 86400

# Dump data folder
DUMP_FOLDER_PATH = os.environ.get('DUMP_FOLDER_PATH', None)

# logger config
LOG_FILE_PATH = os.environ.get('LOG_FILE_PATH', None)
