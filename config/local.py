from base import *

# set up for the local server
SQLALCHEMY_DATABASE_URI = os.getenv('COBOT_DB_URL', None)

# enviroment varaible
ENV = 'local'

DEBUG=True
