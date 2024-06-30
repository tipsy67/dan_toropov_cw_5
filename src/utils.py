from configparser import ConfigParser
from pprint import pprint

from src.api import HeadHunterAPI
from src.dbmanager import DBManager
from src.exceptions import ExitException
from src.interface import UserQuery
from src.settings import URL_EMPLOYERS, DEFAULT_INI, DEFAULT_SECTION

# Пункт меню 1
def get_companies(dbm: DBManager, user_query: UserQuery):
    menu_1 = (
        ("Ввести id компаний для удаления их из списка", del_by_id, (dbm, user_query)),
        ("Ввести ключевые слова для поиска и удаления компаний из списка", del_by_words, (dbm, user_query)),
        ("Выйти в предыдущее меню", user_query.raise_exit),
    )
    try:
        while True:
            dbm.get_companies_and_vacancies_count()
            user_query.print_menu(menu_1)
    except ExitException:
        pass


# Пункт меню 1.1
def del_by_id(dbm: DBManager, user_query: UserQuery):
    list_id = user_query.input_id_for_del()
    dbm.del_by_id(list_id)

# Пункт меню 1.2
def del_by_words(dbm: DBManager, user_query: UserQuery):
    list_words = user_query.input_words_for_del()
    dbm.del_by_words(list_words)

# Пункт меню 2
def get_all_vacancies(dbm: DBManager, user_query: UserQuery):
    dbm.get_all_vacancies()

# Пункт меню 3
def get_vacancies_with_keyword(dbm: DBManager, user_query: UserQuery):
    dbm.get_vacancies_with_keyword()

# Пункт меню 4
def get_vacancies_with_higher_salary(dbm: DBManager, user_query: UserQuery):
    dbm.get_vacancies_with_higher_salary()
# Конец меню

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
