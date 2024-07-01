from src.dbmanager import DBManager
from src.exceptions import BackMenuException
from src.interface import UserQuery


# -------------------------------------------------
# Пункт меню 1
def get_companies(dbm: DBManager, user_query: UserQuery):
    menu_1 = (
        ("Ввести id компаний для удаления их из списка", emloyers_del_by_id, (dbm, user_query)),
        ("Ввести ключевые слова для поиска в названии и затем удаления их из списка",
         emloyers_del_by_words, (dbm, user_query)),
        ("Выйти в предыдущее меню", user_query.raise_back_menu),
    )
    try:
        while True:
            dbm.get_companies_and_vacancies_count()
            user_query.print_menu(menu_1)
    except BackMenuException:
        pass


# Пункт меню 1.1
def emloyers_del_by_id(dbm: DBManager, user_query: UserQuery):
    list_id = user_query.input_id_for_del()
    dbm.del_by_id('employers', 'id', list_id)


# Пункт меню 1.2
def emloyers_del_by_words(dbm: DBManager, user_query: UserQuery):
    list_words = user_query.input_words_for_del()
    dbm.del_by_words('employers', 'name', list_words)


# Пункт меню 2
def get_all_vacancies(dbm: DBManager, user_query: UserQuery):
    menu_2 = (
        ("Ввести id вакансий для удаления их из списка", vacancies_del_by_id, (dbm, user_query)),
        ("Ввести диапазон id вакансий для удаления их из списка", vacancies_del_by_range, (dbm, user_query)),
        ("Ввести ключевые слова для поиска в названии и затем удаления их из списка",
         vacancies_del_by_words, (dbm, user_query)),
        ("Выйти в предыдущее меню", user_query.raise_back_menu),
    )
    try:
        while True:
            dbm.get_all_vacancies()
            user_query.print_menu(menu_2)
    except BackMenuException:
        pass


# Пункт меню 2.1
def vacancies_del_by_id(dbm: DBManager, user_query: UserQuery):
    list_id = user_query.input_id_for_del()
    dbm.del_by_id('vacancies', 'id', list_id)


# Пункт меню 2.2
def vacancies_del_by_range(dbm: DBManager, user_query: UserQuery):
    list_id = user_query.input_range_for_del()
    dbm.del_by_range('vacancies', 'id', list_id)


# Пункт меню 2.3
def vacancies_del_by_words(dbm: DBManager, user_query: UserQuery):
    list_words = user_query.input_words_for_del()
    dbm.del_by_words('vacancies', 'name', list_words)


# Пункт меню 3
def get_vacancies_with_higher_salary(dbm: DBManager, user_query: UserQuery):
    menu_3 = (
        ("Удалить вакансии, не вошедшие в список", del_vacancies_without_higher_salary, (dbm, user_query)),
        ("Выйти в предыдущее меню", user_query.raise_back_menu),
    )
    try:
        while True:
            dbm.get_vacancies_with_higher_salary()
            user_query.print_menu(menu_3)
    except BackMenuException:
        pass


# Пункт меню 3.1
def del_vacancies_without_higher_salary(dbm: DBManager, user_query: UserQuery):
    dbm.del_vacancies_without_higher_salary()
    user_query.raise_back_menu()


# Пункт меню 4
def get_vacancies_with_keyword(dbm: DBManager, user_query: UserQuery):
    menu_4 = (
        ("Удалить вакансии, не вошедшие в список", del_vacancies_without_keyword, (dbm, user_query)),
        ("Выйти в предыдущее меню", user_query.raise_back_menu),
    )
    try:
        while True:
            list_words = user_query.input_words_for_del()
            dbm.get_vacancies_with_keyword(list_words)
            user_query.print_menu(menu_4)
    except BackMenuException:
        pass


# Пункт меню 4.1
def del_vacancies_without_keyword(dbm: DBManager, user_query: UserQuery):
    dbm.del_vacancies_without_keyword(user_query.keywords)
    user_query.raise_back_menu()
# Конец меню
# -------------------------------------------------
