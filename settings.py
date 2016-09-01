# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))


SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migrations')

PICTURES_FOLDER = 'pictures/'
TMP_PICTURES_FOLDER = '/tmp/'

# Possible values : 'linear' and 'semi-random'
SHOW_PICTURES_ORDERING = 'linear'

from local_settings import *
