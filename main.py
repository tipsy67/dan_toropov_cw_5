import psycopg2

from src.api import HeadHunterAPI, Currency
from src.dbmanager import DBManager
from src.exceptions import ExitException, BackMenuException
from src.interface import UserQuery
from src.menu import get_companies, get_all_vacancies, get_vacancies_with_higher_salary, \
    get_vacancies_with_keyword
from src.settings import URL_EMPLOYERS, URL_CURRENCY
from src.utils import read_config


def main():
    user_query = UserQuery()

    data_from_hh = HeadHunterAPI(URL_EMPLOYERS)

    print("Немного подождите, загружаем информацию о компаниях...")
    extend_params = {'sort_by': 'by_vacancies_open', 'only_with_vacancies': True}
    iter_params = [{'text': x} for x in user_query.filter_words]
    data_emp = data_from_hh.load_by_params(iter_params, extend_params)
    data_emp = sorted(data_emp, key=lambda x: x['open_vacancies'], reverse=True)
    data_emp = data_emp[:user_query.top_n]

    print("Загружаем вакансии найденных компаний...")
    extend_params = {'only_with_salary': True}
    list_urls = [x['vacancies_url'] for x in data_emp]
    data_vac = data_from_hh.load_by_urls(list_urls, extend_params)

    print("Заполняем базу данных найденной информацией...")
    params_db = read_config()
    dbmanager = DBManager(params_db)
    with dbmanager as dbm:
        if user_query.is_rewrite:
            dbm.drop_database()
        dbm.create_database()
        dbm.create_tables()

        try:
            data_emp = dbm.refactor_employers_data(data_emp)
            dbm.add_data('employers', data_emp)
        except psycopg2.Error:
            print(f"Ошибка записи в базу. Для избежания дублей попробуйте очищать БД перед запросом.")
        else:
            data_vac = dbm.refactor_vacancies_data(data_vac)
            dbm.add_data('vacancies', data_vac)

        try:
            while True:
                menu = (
                    ("Cписок всех компаний", get_companies, (dbm, user_query)),
                    ("Cписок всех вакансий", get_all_vacancies, (dbm, user_query)),
                    ("Cписок всех вакансий, у которых "
                     "зарплата выше средней", get_vacancies_with_higher_salary, (dbm, user_query)),
                    ("Cписок всех вакансий, в названии "
                     "которых cодержатся ключевые слова", get_vacancies_with_keyword, (dbm, user_query)),
                    ("Выйти в предыдущее меню", user_query.raise_back_menu)
                )
                user_query.print_menu(menu)
        except BackMenuException:
            pass


if __name__ == '__main__':
    try:
        print("Немного подождите, загружаем курсы валют...")
        currency = Currency(URL_CURRENCY)
        currency.update()
        while True:
            main()
    except ExitException:
        print("Работа завершена.")
