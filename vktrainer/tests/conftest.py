# -*- coding: utf-8 -*-

import os

import pytest

from vktrainer import create_app, db as _db
from vktrainer.models import TrainingSet, Photo


@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config.from_object('test_settings')
    return app


@pytest.fixture(scope='session')
def db(app, request):
    if os.path.exists(app.config['DB_PATH']):
        os.unlink(app.config['DB_PATH'])

    def teardown():
        _db.drop_all()
        os.unlink(app.config['DB_PATH'])

    _db.init_app(app)
    _db.create_all()

    request.addfinalizer(teardown)
    return _db


@pytest.fixture
def training_set(db, photo):
    training_set = TrainingSet(name='Test training set')

    db.session.add(training_set)
    db.session.commit()

    training_set.photos.append(photo)
    db.session.commit()

    return training_set


@pytest.fixture
def photo(db):
    photo = Photo(name='Text photo', picture='/fake/path/', md5='deadbeef')

    db.session.add(photo)
    db.session.commit()

    return photo
