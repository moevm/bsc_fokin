from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
from flask_oauthlib.client import OAuth
from config.config import DevConfig, ProdConfig


app = Flask(__name__)
# app.config.from_object(DevConfig)
app.config.from_object(ProdConfig)

db = MongoEngine(app)
# login manager for Stepic and Moodle
login_manager = LoginManager(app)
login_manager.session_protection = "strong"
# oauth for Stepic oauth2
oauth = OAuth(app)
