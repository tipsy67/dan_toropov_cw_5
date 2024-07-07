# ВНИМАНИЕ! Данный блок тестов требует подключения к БД
# соотвественно необходим корректно заполненный файл dbase.ini

from src.api import Currency
from src.dbmanager import DBManager


def test_refactor_vacancies_data(test_vacancy, test_data_vacancies):
    assert DBManager.refactor_vacancies_data(test_data_vacancies)[0] == test_vacancy[0]


def test_get_salary():
    assert DBManager.get_salary(None) == (0, 0)

    Currency.is_complete = False

    test_salary = {"from": 350000, "to": 450000, "currency": "RUR", "gross": False}
    assert DBManager.get_salary(test_salary) == (350000, 450000)

    test_salary = {"from": 350000, "to": 450000, "currency": "BYR", "gross": False}
    assert DBManager.get_salary(test_salary) == (350000, 450000)


def test_refactor_employers_data(test_employer, test_data_employers):
    assert DBManager.refactor_employers_data(test_data_employers)[0] == test_employer[0]


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
