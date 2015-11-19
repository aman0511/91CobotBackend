# -*- coding: utf-8 -*-
from flask.ext.cors import CORS
from app import app
from app.views.root import root
from app.views.api import api

# One of the simplest configurations. Exposes all resources  to
# CORS and allows the Content-Type header, which is necessary to POST JSON
# cross origin.
CORS(app, allow_headers='Content-Type')

# register blueprints
app.register_blueprint(root)
app.register_blueprint(api)
