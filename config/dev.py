from base import *
import os

# set up for the devlopment server
SQLALCHEMY_DATABASE_URI = os.getenv('COBOT_DB_URL', None)

# enviroment varaible
ENV = 'dev'
