# -*- coding: utf-8 -*-
from flask.ext.api import FlaskAPI
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.cache import Cache

# create a flask application instance
app = FlaskAPI(__name__)

# Check Configuring Flask-Cache section for more details
cache = Cache(app, config={'CACHE_TYPE': 'simple'})

# create SQLAlchemy instance
db = SQLAlchemy(app)

# config set up
app.config.from_object('config')

# import helper utilities
from app import helpers

# import models
from app import models

# import views
from app import views

# import logger
from app import logger
