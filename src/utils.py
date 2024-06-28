from configparser import ConfigParser

from src.api import HeadHunterAPI
from src.interface import UserQuery
from src.settings import URL_EMPLOYERS, DEFAULT_INI, DEFAULT_SECTION


def load_top_x():
    print(1)


def load_json_employers(user_query: UserQuery) -> list:
    employers = HeadHunterAPI(URL_EMPLOYERS)
    text = employers.load_employers(user_query)[:user_query.top_n]

    return text


def use_last_query():
    print(3)


def read_config(filename=DEFAULT_INI, section=DEFAULT_SECTION):
    """Заберем конфигурационные данные подключения к базе данных из INI файла"""
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db
