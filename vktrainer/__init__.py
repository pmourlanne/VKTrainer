# -*- coding: utf-8 -*-

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = "vktrainer.login"


def create_app():
    app = Flask(__name__)

    # Config
    app.config.from_object('settings')

    # Blueprint
    from vktrainer.views import vktrainer_bp
    app.register_blueprint(vktrainer_bp)

    return app


app = create_app()
db.init_app(app)
login_manager.init_app(app)
