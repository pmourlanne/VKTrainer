# -*- coding: utf-8 -*-

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('settings')

db = SQLAlchemy(app)

# Flask login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


from vktrainer import views
