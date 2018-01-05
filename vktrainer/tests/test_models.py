# -*- coding: utf-8 -*-

from vktrainer.tests.conftest import assert_num_queries


def test_get_leaderboard(db, training_set, user_factory, result_factory):
    # No results
    assert list(training_set.get_leaderboard()) == []

    # We create one result
    terry = user_factory.get(name='Terry')
    result_factory.get(user=terry)
    assert list(training_set.get_leaderboard()) == [('Terry', 1)]

    # We create a result from someone else
    john = user_factory.get(name='John')
    result_factory.get(user=john)
    assert list(training_set.get_leaderboard()) == [('Terry', 1), ('John', 1)]

    # Second user has two results
    result_factory.get(user=john)
    assert list(training_set.get_leaderboard()) == [('John', 2), ('Terry', 1)]


def test_list_results_nb_queries(db, training_set, result_factory):
    nb_queries_no_results = 2
    nb_queries = 3

    # No results
    with assert_num_queries(db, nb_queries_no_results):
        assert training_set.get_results() == []

    # Number of queries is fixed
    result_factory.get()
    with assert_num_queries(db, nb_queries):
        assert len(training_set.get_results()) == 1

    [result_factory.get() for i in xrange(10)]
    with assert_num_queries(db, nb_queries):
        assert len(training_set.get_results()) == 11
