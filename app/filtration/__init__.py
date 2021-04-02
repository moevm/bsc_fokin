from flask import Blueprint

filtration = Blueprint('filtration', __name__)

from app.filtration import models, views
