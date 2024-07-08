from pprint import pprint

import pytest
import requests
from src.api import Currency
from src.settings import SEARCH_PER_PAGE, SEARCH_PAGE


def test_init(hhapi):
    assert hhapi._HeadHunterAPI__url == 'test_url'
    assert hhapi._HeadHunterAPI__headers == {'User-Agent': 'HH-User-Agent'}
    assert hhapi._HeadHunterAPI__params == {'text': '', 'page': 0, 'per_page': SEARCH_PER_PAGE}


def test_reset_params(hhapi):
    assert hhapi._HeadHunterAPI__params['page'] == 0
    hhapi._HeadHunterAPI__params['page'] = 1
    assert hhapi._HeadHunterAPI__params['page'] == 1
    hhapi.reset_params()
    assert hhapi._HeadHunterAPI__params['page'] == 0


def test_dict_to_params(hhapi):
    assert hhapi._HeadHunterAPI__params['page'] == 0
    with pytest.raises(KeyError):
        assert hhapi._HeadHunterAPI__params['test']
    hhapi.dict_to_params({'page': 1, 'test': 'testtest'})
    assert hhapi._HeadHunterAPI__params['page'] == 1
    assert hhapi._HeadHunterAPI__params['test'] == 'testtest'


def test_set_extended_params(hhapi):
    hhapi._HeadHunterAPI__params['test'] = 'testtest'
    hhapi.set_extended_params({'page': 1, 'test_new': 'test_new_test'})
    assert hhapi._HeadHunterAPI__params['page'] == 1
    with pytest.raises(KeyError):
        assert hhapi._HeadHunterAPI__params['test']
    assert hhapi._HeadHunterAPI__params['test_new'] == 'test_new_test'


def test_get_currency_rate(test_currency):
    assert test_currency.get_rate('byn') == 1
    assert test_currency.get_rate('byr') == 1
    assert test_currency.get_rate('usd') == 1

    Currency.is_complete = True

    assert test_currency.get_rate('byn') == 0.02
    assert test_currency.get_rate('byr') == 0.02
    assert test_currency.get_rate('usd') == 0.01


def test_load_from_api(test_data_employers, hhapi, monkeypatch):
    class MockResponse:
        def __init__(self, *args, **kwargs):
            self.status_code = 200
            self.url = 'test_url'
            self.headers = {'User-Agent': 'HH-User-Agent'}

        def json(self):
            return {'items': test_data_employers}

    def mock_get(*args, **kwargs):

        return MockResponse(*args, **kwargs)

    monkeypatch.setattr(requests, 'get', mock_get)

    res = hhapi.load_by_urls(['test_url'])
    assert res[0] == test_data_employers[0]

    res = hhapi.load_by_params([{'test_url': 'http///test///'}])
    assert res[0] == test_data_employers[0]
