# -*- coding: utf-8 -*-
from app import app
from flask.ext.cors import CORS
from main import api

# One of the simplest configurations. Exposes all resources matching /api/* to
# CORS and allows the Content-Type header, which is necessary to POST JSON
# cross origin.
CORS(api, resources={r"/api/*": {"origins": "*"}},
     allow_headers='Content-Type')

# register blueprints
app.register_blueprint(api)
