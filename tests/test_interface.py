from src.interface import UserQuery
from tests.test_utils_from_github import set_keyboard_input


def test_top_n(test_user_query):
    assert test_user_query.top_n == 1


def test_filter_words(test_user_query):
    assert test_user_query.filter_words == ['test']


def test_is_rewrite(test_user_query):
    assert test_user_query.is_rewrite is False


def test_keywords(test_user_query):
    assert test_user_query.keywords is None


def test_user_query_class():
    set_keyboard_input(['10', 'test2', '1'])
    test_query = UserQuery()

    assert test_query.top_n == 10
    assert test_query.filter_words == ['test2']
    assert test_query.is_rewrite is True


def test_remember_query(test_user_query):
    dict_ = {
        'top_n': 1,
        'filter_words': ['test'],
        'is_rewrite': False,
        'keywords': None
    }
    test_user_query.remember_query()

    assert UserQuery.last_user_query == dict_


def test_input_id_for_del(test_user_query):
    set_keyboard_input(['test', '10 test2 100'])
    assert test_user_query.input_id_for_del() == ['10', '100']


def test_input_words_for_del(test_user_query):
    set_keyboard_input(['test test2'])
    assert test_user_query.input_words_for_del() == ['test', 'test2']


def test_input_range_for_del(test_user_query):
    set_keyboard_input(['test', '10-test2 100', '101-1001'])
    assert test_user_query.input_range_for_del() == ['101', '1001']
