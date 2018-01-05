# -*- coding: utf-8 -*-

import os

import pytest
import sqlalchemy

from vktrainer import create_app, db as _db
from vktrainer.models import (
    TrainingSet,
    Photo,
    User,
    TrainingResult,
)


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
    photo = Photo(name='Test photo', picture='/fake/path/', md5='deadbeef')

    db.session.add(photo)
    db.session.commit()

    return photo


@pytest.fixture
def user(db):
    user = User(name='Test name')
    db.session.add(user)
    db.session.commit()

    return user


@pytest.fixture
def user_factory(db):
    class factory():
        def get(self, name):
            user = User(name=name)
            db.session.add(user)
            db.session.commit()

            return user

    return factory()


@pytest.fixture
def result_factory(db, training_set, photo, user):
    class factory():
        def get(self, **kwargs):
            kwargs.setdefault('training_set', training_set)
            kwargs.setdefault('photo', photo)
            kwargs.setdefault('user', user)
            kwargs.setdefault('result', '{}')

            result = TrainingResult(**kwargs)
            db.session.add(result)
            db.session.commit()
            return result

    return factory()


# Inspired from https://stackoverflow.com/a/33691585/1669977
class NumQueryAssertion(object):
    def __init__(self, db, expected_query_count):
        self.db = db
        self.expected_query_count = expected_query_count

        self.queries = []

    def callback(self, conn, cursor, statement, parameters, context, executemany):
        self.queries.append('QUERY:\n%s\nPARAMS:\n%s' % (statement, parameters))

    def __enter__(self):
        sqlalchemy.event.listen(self.db.engine, 'after_cursor_execute', self.callback)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        sqlalchemy.event.remove(self.db.engine, 'after_cursor_execute', self.callback)

        self.assert_condition()

    def assert_condition(self):
        nb_queries = len(self.queries)

        if nb_queries != self.expected_query_count:
            msg = "%d queries executed, %d expected" % (nb_queries, self.expected_query_count)

            msg += '\nCaptured queries were:\n'
            msg += '\n---------\n'.join(self.queries)

            raise AssertionError(msg)

assert_num_queries = NumQueryAssertion
