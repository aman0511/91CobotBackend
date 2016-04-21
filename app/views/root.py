# -*- coding: utf-8 -*-
from flask import url_for, Blueprint, request
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
    return res, status.HTTP_200_OK


@root.route('/run_task_data', methods=['POST'])
def run_code():
    data = request.get_json()
    from app.tasks import start_data_task_of_day
    start_data_task_of_day(data["date_str"], data["hub_name"])
    return {"status": "OK"}, status.HTTP_200_OK

