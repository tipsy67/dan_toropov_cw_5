import pytest

from src.dbmanager import DBManager
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