from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from config.config import DevConfig


app = Flask(__name__)
app.config.from_object(DevConfig)

db = MongoEngine(app)
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
oauth = OAuth(app)
