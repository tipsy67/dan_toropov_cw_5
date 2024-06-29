import requests

from src.interface import UserQuery
from src.settings import SEARCH_PER_PAGE, SEARCH_PAGE


class HeadHunterAPI:
    """
    Класс для получения списка вакансий с ресурса НН
    """
    __slots__ = ['__url', '__headers', '__params']
    def __init__(self, url):
        self.__headers = {'User-Agent': 'HH-User-Agent'}
        self.__url = url
        self.__params = None
        self.reset_params()


    def reset_params(self):
        self.__params = {'text': '', 'page': 0, 'per_page': SEARCH_PER_PAGE}

    def set_extended_params(self, dict_):
        self.reset_params()
        if dict_ is not None:
            self.dict_to_params(dict_)

    def dict_to_params(self, dict_):
        for key, value in dict_.items():
            self.__params[key] = value

    def load_by_params(self, iter_params: [dict], extended_params=None) -> list:
        self.set_extended_params(extended_params)
        list_data = []
        for dict_ in iter_params:
            self.dict_to_params(dict_)
            self.__params['page'] = 0
            list_data.extend(self.load_json_from_hh())

        return list_data


    def load_by_urls(self, list_url: list, extended_params=None) -> list:
        self.set_extended_params(extended_params)
        list_data = []
        for url in list_url:
            self.__url = url
            self.__params['page'] = 0
            list_data.extend(self.load_json_from_hh())

        return list_data


    def load_json_from_hh(self) -> list:
        all_items = []
        while self.__params.get('page') != SEARCH_PAGE:
            response = requests.get(self.__url, headers=self.__headers, params=self.__params)
            items = response.json()['items']
            if not items:
                break
            all_items.extend(items)
            self.__params['page'] += 1

        return all_items


class Currency:
    """
    Для получения курса валют по заданной ссылке на JSON файл
    """
    __slots__ = ['user_url']
    currency_rate = {}

    def __init__(self, user_url):
        self.user_url = user_url

    def update(self):
        Currency.currency_rate = requests.get(self.user_url).json()

    @classmethod
    def get_rate(cls, currency) -> float | int:
        """
        Вернем коэффициент отношения заданной валюты к рублю
        :param currency: трехбуквенный валютный код
        :return:
        """
        currency = currency.lower()
        if currency == 'byr':
            currency = 'byn'
        return cls.currency_rate['rub'].get(currency, 1)
