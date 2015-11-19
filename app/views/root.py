# -*- coding: utf-8 -*-
from flask import url_for, Blueprint
from flask.ext.api import status

# create blueprint instance
root = Blueprint('ROOT', __name__)


# root endpoint
@root.route('/', methods=['GET'])
def index():
    res = {
        "cards": url_for('API.get_cards', _external=True),
        "reports": url_for('API.get_reports', _external=True),
    }
    return (res, status.HTTP_200_OK)
