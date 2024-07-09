import pytest

from src.api import HeadHunterAPI, Currency
from src.dbmanager import DBManager
from src.interface import UserQuery
from src.settings import URL_EMPLOYERS
from src.utils import read_config


@pytest.fixture
def test_vacancy():
    return [{'employer_id': '1199213', 'name': 'Тестировщик комфорта квартир', 'salary_min': 350000,
             'salary_max': 450000, 'area': 'Воронеж',
             'url': 'https://hh.ru/vacancy/93353083', 'employment': 'Полная занятость',
             'experience': 'Нет опыта', 'schedule': 'Гибкий график',
             'description': 'Занимать активную жизненную позициюОценивать вид из окна'}]


@pytest.fixture
def test_employer():
    return [{'id': '1199213',
             'name': 'SKYPRO',
             'open_vacancies': 1,
             'url': 'https://hh.ru/employer/1199213',
             'vacancies_url': 'https://api.hh.ru/vacancies?employer_id=1199213'}]


@pytest.fixture(scope='function')
def dbmanager_test():
    params_db = read_config()
    dbmanager_test = DBManager(params_db)

    return dbmanager_test


@pytest.fixture
def dbm_test(dbmanager_test):
    with dbmanager_test as dbm_test:
        dbm_test.create_database('test_base')
        dbm_test.create_tables()
        yield dbm_test
        dbm_test._conn.close()
        dbm_test._params['dbname'] = 'postgres'
        dbm_test._new_connect()
        dbm_test.drop_database('test_base')


@pytest.fixture
def dbm_test_data(dbmanager_test, test_employer, test_vacancy):
    with dbmanager_test as dbm_test:
        dbm_test.create_database('test_base')
        dbm_test.create_tables()
        dbm_test.add_data('employers', test_employer)
        dbm_test.add_data('vacancies', test_vacancy)
        yield dbm_test
        dbm_test._conn.close()
        dbm_test._params['dbname'] = 'postgres'
        dbm_test._new_connect()
        dbm_test.drop_database('test_base')


@pytest.fixture
def hhapi():
    return HeadHunterAPI('test_url')


@pytest.fixture
def test_currency():
    currency = Currency('test_url')
    Currency.currency_rate = {
        "date": "2024-06-10",
        "rub": {
            "byn": 0.02,
            "byr": 200.33285834,
            "rub": 1,
            "usd": 0.01,
        }
    }
    return currency


@pytest.fixture
def test_data_vacancies():
    return [{"id": "93353083", "premium": False, "name": "Тестировщик комфорта квартир", "department": None,
             "has_test": False,
             "response_letter_required": False,
             "area": {"id": "26", "name": "Воронеж", "url": "https://api.hh.ru/areas/26"},
             "salary": {"from": 350000, "to": 450000, "currency": "RUR", "gross": False},
             "type": {"id": "open", "name": "Открытая"},
             "address": None, "response_url": None, "sort_point_distance": None,
             "published_at": "2024-02-16T14:58:28+0300",
             "created_at": "2024-02-16T14:58:28+0300", "archived": False,
             "apply_alternate_url": "https://hh.ru/applicant/vacancy_response?vacancyId=93353083",
             "branding": {"type": "CONSTRUCTOR", "tariff": "BASIC"}, "show_logo_in_search": True,
             "insider_interview": None,
             "url": "https://api.hh.ru/vacancies/93353083?host=hh.ru",
             "alternate_url": "https://hh.ru/vacancy/93353083",
             "relations": [], "employer": {"id": "1199213", "name": "Специализированный застройщик BM GROUP",
                                           "url": "https://api.hh.ru/employers/3499705",
                                           "alternate_url": "https://hh.ru/employer/3499705",
                                           "logo_urls": {
                                               "original": "https://hhcdn.ru/employer-logo-original/1214854.png",
                                               "240": "https://hhcdn.ru/employer-logo/6479866.png",
                                               "90": "https://hhcdn.ru/employer-logo/6479865.png"},
                                           "vacancies_url": "https://api.hh.ru/vacancies?employer_id=3499705",
                                           "accredited_it_employer": False, "trusted": True},
             "snippet": {"requirement": "Занимать активную жизненную позицию",
                         "responsibility": "Оценивать вид из окна"},
             "contacts": None, "schedule": {"id": "flexible", "name": "Гибкий график"}, "working_days": [],
             "working_time_intervals": [], "working_time_modes": [], "accept_temporary": False,
             "professional_roles": [{"id": "107", "name": "Руководитель проектов"}],
             "accept_incomplete_resumes": False,
             "experience": {"id": "noExperience", "name": "Нет опыта"},
             "employment": {"id": "full", "name": "Полная занятость"},
             "adv_response_url": None, "is_adv_vacancy": False, "adv_context": None}]


@pytest.fixture
def test_data_employers():
    return [{'alternate_url': 'https://hh.ru/employer/1199213',
             'id': '1199213',
             'logo_urls': {'240': 'https://img.hhcdn.ru/employer-logo/5764545.png',
                           '90': 'https://img.hhcdn.ru/employer-logo/5764544.png',
                           'original': 'https://img.hhcdn.ru/employer-logo-original/1035946.png'},
             'name': 'SKYPRO',
             'open_vacancies': 1,
             'url': 'https://api.hh.ru/employers/1199213',
             'vacancies_url': 'https://api.hh.ru/vacancies?employer_id=1199213'}]


@pytest.fixture
def test_user_query():
    user_query = UserQuery.__new__(UserQuery)
    print(user_query.__dict__)
    user_query._UserQuery__top_n = 1
    user_query._UserQuery__filter_words = ['test']
    user_query._UserQuery__is_rewrite = False
    user_query._UserQuery__keywords = None

    return user_query
