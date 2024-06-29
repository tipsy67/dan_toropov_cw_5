from pprint import pprint

from src.api import HeadHunterAPI, Currency
from src.dbmanager import DBManager
from src.exceptions import ExitException
from src.interface import UserQuery
from src.settings import URL_EMPLOYERS, URL_CURRENCY

from src.utils import read_config


def main():
    print("Немного подождите, загружаем курсы валют...")
    currency = Currency(URL_CURRENCY)
    currency.update()

    user_query = UserQuery()

    employers = HeadHunterAPI(URL_EMPLOYERS)

    print("Немного подождите, загружаем информацию о компаниях...")
    extend_params = {'sort_by': 'by_vacancies_open', 'only_with_vacancies': True}
    iter_params = [{'text': x} for x in user_query.filter_words]
    data_emp = employers.load_by_params(iter_params, extend_params)[:user_query.top_n]

    print("Загружаем вакансии найденных компаний...")
    list_urls = [x['vacancies_url'] for x in data_emp]
    data_vac = employers.load_by_urls(list_urls)

    print("Заполняем базу данных найденной информацией...")
    params_db = read_config()
    dbmanager = DBManager(params_db)
    with dbmanager as dbm:
        if user_query.is_rewrite:
            dbm.drop_database()
        dbm.create_database()
        dbm.create_tables()

        data_emp = dbm.refactor_employers_data(data_emp)
        dbm.add_data('employers', data_emp)

        data_vac = dbm.refactor_vacancies_data(data_vac)
        dbm.add_data('vacancies', data_vac)


if __name__ == '__main__':
    try:
        main()
    except ExitException:
        print("Работа завершена.")
