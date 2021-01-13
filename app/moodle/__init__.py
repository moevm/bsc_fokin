from flask import Blueprint

moodle = Blueprint('moodle', __name__)

from app.moodle import models, moodle_api
from app.moodle.views import main, courses, discussions, posts, filtration
