from flask import Blueprint, render_template

mod = Blueprint('main', __name__, url_prefix="",
                template_folder="templates")


@mod.before_request
def before_request():
    pass


@mod.after_request
def after_request(response):
    return response


@mod.teardown_request
def teardown_request(response):
    return response


@mod.route("/", methods=['GET'])
def index():
    return render_template('index.html')
