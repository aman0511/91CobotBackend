from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)

# config set up
app.config.from_object('config')

# create db instance
db = SQLAlchemy(app)

# import views
from app.views import main

# register blueprints
app.register_blueprint(main.mod)

# import helper utilities
from app import helpers

# import models
from app import models
