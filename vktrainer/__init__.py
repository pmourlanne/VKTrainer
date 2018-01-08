# -*- coding: utf-8 -*-

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config.from_object('settings')

    from vktrainer.views import vktrainer_bp
    app.register_blueprint(vktrainer_bp)

    return app


app = create_app()
db.init_app(app)

# Flask login
login_manager.init_app(app)
login_manager.login_view = "vktrainer.login"
