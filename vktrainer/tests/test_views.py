# -*- coding: utf-8 -*-

from flask import url_for

from vktrainer.models import User
from vktrainer.tests.conftest import assert_url


def test_home(client, training_set):
    res = client.get(url_for('vktrainer.home'))

    assert b'Voight-Kampff' in res.data
    assert b'Training sets' in res.data
    assert training_set.name.encode('ascii') in res.data


def test_login(client, user, no_csrf):
    url = url_for('vktrainer.login')

    initial_nb_users = User.query.count()

    # We login with an existing name
    res = client.post(url, data={
        'name': user.name,
    })
    # We get redirected to the home
    assert res.status_code == 302
    assert_url(res.location, url_for('vktrainer.home'))
    # No new users were created
    assert User.query.count() == initial_nb_users

    # We login with a new user
    res = client.post(url, data={
        'name': 'new user',
    })
    # We get redirected to the home
    assert res.status_code == 302
    assert_url(res.location, url_for('vktrainer.home'))
    # A new user was created
    assert User.query.count() == initial_nb_users + 1
    assert User.query.filter(User.name == 'new user').count() == 1
