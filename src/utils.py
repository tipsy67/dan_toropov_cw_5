from pprint import pprint

from src.api import HeadHunterAPI
from src.settings import URL_EMPLOYERS


def load_top_x():
    print(1)


def load_keyword():
    keywords = input()
    employers = HeadHunterAPI(URL_EMPLOYERS)
    text = employers.load_vacancies(keywords)
    pprint(text)


def use_last_query():
    print(3)