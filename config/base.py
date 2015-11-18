# common set up which will use in all case
import os

SECRET_KEY = '311bdbb47de9f01d352535685df764886c87623293e20fe0'
basedir = os.path.abspath(os.path.dirname(__file__))

# cobot constants
COBOT_TOKEN = '5648dc761e47988579bbc2645547e04d16f322a1d27fa286caf545086e3\
ce47f'
MEMBERSHIPS_URL_STR = 'http://%s.cobot.me/api/memberships'

# Flask-Cache settings
CACHE_DEFAULT_TIMEOUT=86400
