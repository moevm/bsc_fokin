from flask import Blueprint

moodle = Blueprint('moodle', __name__)

# from app.moodle import views, models, moodle_api
from app.moodle import views, models, moodle_api
