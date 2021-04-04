from flask import Blueprint

stepic = Blueprint('stepic', __name__)

from app.stepic import models, stepic_api
from app.stepic.views import main, courses, comments, reviews
