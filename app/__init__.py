# -*- coding: utf-8 -*-
from flask.ext.api import FlaskAPI
from flask.ext.sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

# create a flask application instance
app = FlaskAPI(__name__)

# create marshmallow instance
ma = Marshmallow(app)

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
