# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))

DB_PATH = os.path.join(basedir, 'test_app.db')
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_PATH

TESTING = True

SQLALCHEMY_TRACK_MODIFICATIONS = False
