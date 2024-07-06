import sys

from src.dbmanager import DBManager


def test_refactor_vacancies_data(test_vacancy):
    test_data = [{"id": "93353083", "premium": False, "name": "Тестировщик комфорта квартир", "department": None,
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

    assert DBManager.refactor_vacancies_data(test_data)[0] == test_vacancy[0]


def test_get_salary():
    assert DBManager.get_salary(None) == (0, 0)

    test_salary = {"from": 350000, "to": 450000, "currency": "RUR", "gross": False}
    assert DBManager.get_salary(test_salary) == (350000, 450000)

    test_salary = {"from": 350000, "to": 450000, "currency": "BYR", "gross": False}
    assert DBManager.get_salary(test_salary) == (350000, 450000)


def test_refactor_employers_data(test_employer):
    test_data = ([{'alternate_url': 'https://hh.ru/employer/1199213',
                   'id': '1199213',
                   'logo_urls': {'240': 'https://img.hhcdn.ru/employer-logo/5764545.png',
                                 '90': 'https://img.hhcdn.ru/employer-logo/5764544.png',
                                 'original': 'https://img.hhcdn.ru/employer-logo-original/1035946.png'},
                   'name': 'SKYPRO',
                   'open_vacancies': 1,
                   'url': 'https://api.hh.ru/employers/1199213',
                   'vacancies_url': 'https://api.hh.ru/vacancies?employer_id=1199213'}])

    assert DBManager.refactor_employers_data(test_data)[0] == test_employer[0]


def test_create_db(dbmanager_test):
    with dbmanager_test as dbm:
        dbm.drop_database('test_base')
        not_exists = dbm.if_db_not_exists('test_base')
        assert not_exists

        dbm.create_database('test_base')
        not_exists = dbm.if_db_not_exists('test_base')
        assert not not_exists


def test_drop_db(dbmanager_test):
    with dbmanager_test as dbm:
        dbm.drop_all_connection('test_base')
        dbm.drop_database('test_base')
        not_exists = dbm.if_db_not_exists('test_base')
        assert not_exists


def test_create_tables(dbm_test):
    with dbm_test._conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS vacancies")
        cur.execute("DROP TABLE IF EXISTS employers")
    assert dbm_test.if_table_not_exists('employers') is True
    assert dbm_test.if_table_not_exists('vacancies') is True

    dbm_test.create_tables()
    assert dbm_test.if_table_not_exists('employers') is False
    assert dbm_test.if_table_not_exists('vacancies') is False


def is_tables_empty(test_conn):
    with test_conn._conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) = 0 FROM employers")
        res1, = cur.fetchone()
        cur.execute("SELECT COUNT(*) = 0 FROM vacancies")
        res2, = cur.fetchone()
    return res1, res2


def test_add_data(dbm_test, test_employer, test_vacancy):
    res_emp, res_vac = is_tables_empty(dbm_test)
    assert res_emp is True
    assert res_vac is True

    dbm_test.add_data('employers', test_employer)
    dbm_test.add_data('vacancies', test_vacancy)
    res_emp, res_vac = is_tables_empty(dbm_test)
    assert res_emp is False
    assert res_vac is False


def test_query_and_return(dbm_test, test_employer):
    dbm_test.add_data('employers', test_employer)

    query = "SELECT * FROM employers"
    res = dbm_test.query_and_return(query)

    assert res is not None


def test_query_to_db(dbm_test, test_employer):
    dbm_test.add_data('employers', test_employer)

    query = "DELETE FROM employers"
    dbm_test.query_to_db(query)

    query = "SELECT * FROM employers"
    res = dbm_test.query_and_return(query)

    assert res == []


def test_select_and_print(capsys, dbm_test, test_employer):
    dbm_test.add_data('employers', test_employer)

    query = "SELECT * FROM employers"
    dbm_test.select_and_print(query, 't')

    captured = capsys.readouterr()
    str_ = '\n' + ' ' * 5 + 't\n'
    str_ = str_ + '-' * 80 + '\n'
    str_ = str_ + '1199213 SKYPRO 1 https://hh.ru/employer/1199213 https://api.hh.ru/vacancies?employer_id=1199213\n'

    assert captured.out == str_


def test_del_by_id(dbm_test_data):
    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_emp is False
    assert res_vac is False

    dbm_test_data.del_by_id('employers', 'id', ['1199213'])

    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_emp is True
    assert res_vac is True


def test_del_by_range(dbm_test_data):
    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_emp is False
    assert res_vac is False

    dbm_test_data.del_by_range('employers', 'id', ['1199213', '1199299'])

    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_emp is True
    assert res_vac is True


def test_del_by_words(dbm_test_data):
    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_emp is False
    assert res_vac is False

    dbm_test_data.del_by_words('employers', 'name', ['sky'])

    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_emp is True
    assert res_vac is True


def test_get_companies_and_vacancies_count(capsys, dbm_test_data):
    dbm_test_data.get_companies_and_vacancies_count()

    captured = capsys.readouterr()
    str_ = ("\n"
            "     id     name     open_vacancies     url     vacancies_in_base\n"
            "--------------------------------------------------------------------------------\n"
            "1199213 SKYPRO 1 https://hh.ru/employer/1199213 1\n")

    assert captured.out == str_


def test_get_all_vacancies(capsys, dbm_test_data):
    dbm_test_data.get_all_vacancies()

    captured = capsys.readouterr()
    str_ = ("\n"
            "     id     company     vacancy     salary_min     salary_max     url\n"
            "--------------------------------------------------------------------------------\n"
            "1 SKYPRO Тестировщик комфорта квартир 350000 450000 https://hh.ru/vacancy/93353083\n")

    assert captured.out == str_


def test_get_vacancies_with_higher_salary(capsys, dbm_test_data):
    dbm_test_data.get_vacancies_with_higher_salary()

    captured = capsys.readouterr()
    str_ = ("\n"
            "     id     company     vacancy     salary_min     salary_max     url\n"
            "--------------------------------------------------------------------------------\n")

    assert captured.out == str_


def test_get_vacancies_with_keyword(capsys, dbm_test_data):
    dbm_test_data.get_vacancies_with_keyword('python')
    captured = capsys.readouterr()
    str_ = ("\n"
            "     id     company     vacancy     salary_min     salary_max     url\n"
            "--------------------------------------------------------------------------------\n")

    assert captured.out == str_

    dbm_test_data.get_vacancies_with_keyword('тест')
    captured = capsys.readouterr()
    str_ = ("\n"
            "     id     company     vacancy     salary_min     salary_max     url\n"
            "--------------------------------------------------------------------------------\n"
            "1 SKYPRO Тестировщик комфорта квартир 350000 450000 https://hh.ru/vacancy/93353083\n")

    assert captured.out == str_


def test_del_vacancies_without_higher_salary(dbm_test_data):
    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_vac is False

    dbm_test_data.del_vacancies_without_higher_salary()

    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_vac is True

def test_del_vacancies_without_keyword(dbm_test_data):
    dbm_test_data.del_vacancies_without_keyword('тест')

    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_vac is False

    dbm_test_data.del_vacancies_without_keyword('python')

    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_vac is True

def test_employers_zero_vac_del(dbm_test_data):
    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_vac is False
    assert res_emp is False

    dbm_test_data.del_vacancies_without_higher_salary()
    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_vac is True

    dbm_test_data.employers_zero_vac_del()
    res_emp, res_vac = is_tables_empty(dbm_test_data)
    assert res_emp is True
