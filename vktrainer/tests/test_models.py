# -*- coding: utf-8 -*-

from vktrainer.models import TrainingResult, User


def test_get_leaderboard(db, training_set, photo):
    def _create_training_result(name):
        user = User.query.filter(User.name == name).first()
        if not user:
            user = User(name=name)
            db.session.add(user)
            db.session.commit()

        result = TrainingResult(training_set=training_set, photo=photo, user=user)
        db.session.add(result)
        db.session.commit()

        return result

    # No results
    assert list(training_set.get_leaderboard()) == []

    # We create one result
    _create_training_result(name='Terry')
    assert list(training_set.get_leaderboard()) == [('Terry', 1)]

    # We create a result from someone else
    _create_training_result(name='John')
    assert list(training_set.get_leaderboard()) == [('Terry', 1), ('John', 1)]

    # Second user has two results
    _create_training_result(name='John')
    assert list(training_set.get_leaderboard()) == [('John', 2), ('Terry', 1)]
