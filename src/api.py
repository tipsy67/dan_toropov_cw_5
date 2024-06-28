import requests

from src.interface import UserQuery
from src.settings import SEARCH_PER_PAGE, SEARCH_PAGE


class HeadHunterAPI:
    """
    Класс для получения списка вакансий с ресурса НН
    """

    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent': 'HH-User-Agent'}
        self.params = {'text': '', 'page': 0, 'per_page': SEARCH_PER_PAGE}

    def load_employers(self, user_query: UserQuery) -> list:
        """
        Получаем список вакансий в виде словаря
        :param user_query: пользовательский запрос
        'user_query' - текст запроса
        :return:
        """
        keywords = user_query.filter_words
        employers = []
        self.params['only_with_vacancies'] = True
        for keyword in keywords:
            self.params['text'] = keyword
            self.params['page'] = 0
            self.params['sort_by'] = 'by_vacancies_open'
            employers.extend(self.load_json_from_hh())

        return employers

    def load_json_from_hh(self) -> list:
        all_items = []
        while self.params.get('page') != SEARCH_PAGE:
            response = requests.get(self.url, headers=self.headers, params=self.params)
            items = response.json()['items']
            if not items:
                break
            all_items.extend(items)
            self.params['page'] += 1
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
