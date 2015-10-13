# -*- coding: utf-8 -*-
from flask.ext.api import FlaskAPI
from flask.ext.sqlalchemy import SQLAlchemy

# create a flask application instance
app = FlaskAPI(__name__)

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
