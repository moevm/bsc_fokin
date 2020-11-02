from flask import Blueprint

stepic = Blueprint('stepic', __name__)

from app.stepic import views, models, stepic_api
