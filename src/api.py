from abc import ABC, abstractmethod

import requests

from src.settings import SEARCH_PER_PAGE, SEARCH_PAGE


class MainAPI(ABC):
    """
    Обяжем создавать метод со дним названием для получения JSON
    из разных ресурсов
    """

    @abstractmethod
    def load_vacancies(self, *args, **kwargs):
        pass


class HeadHunterAPI(MainAPI):
    """
    Класс для получения списка вакансий с ресурса НН
    """
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'HH-User-Agent'}
        self.params = {'text': '', 'page': 0, 'per_page': SEARCH_PER_PAGE}

    def load_vacancies(self, user_query):
        """
        Получаем список вакансий в виде словаря
        :param user_query: пользовательский запрос
        'user_query' - текст запроса
        :return:
        """
        self.params['text'] = user_query
        vacancies = {}
        while self.params.get('page') != SEARCH_PAGE:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            vacancies = response.json()['items']
            vacancies.extend(vacancies)
            self.params['page'] += 1
        return vacancies


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