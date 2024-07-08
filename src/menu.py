from src.dbmanager import DBManager
from src.exceptions import BackMenuException, ExitException
from src.interface import UserQuery


class SuperMenu:
    """Класс для создания текстовых меню"""

    def __init__(self):
        pass

    def raise_exit(self):
        """Генерация исключения для выхода из программы"""
        raise ExitException

    def raise_back_menu(self):
        """Генерация исключения для выхода в предыдущее меню"""
        raise BackMenuException

    def print_menu(self, menu: tuple):
        """
        Для вывода меню на экран и обработки выбора пользователя
        menu: Кортеж из кортежей вида
        (текст пункта меню, ссылка на вызываемую функцию, позиционные аргументы для функции)
        """
        print()
        print("Выберите необходимый пункт меню:")
        len_menu = len(menu)
        for index, item in enumerate(menu):
            print(f'{index + 1}. {item[0]}')
        while True:
            user_input = input().strip().lower()
            if user_input.isdigit() and 0 < int(user_input) <= len_menu:
                break
            elif user_input == '/exit':
                self.raise_exit()
            else:
                print(f"Введите число от 1 до {len_menu}. '/exit' - для выхода")
        if len(menu[int(user_input) - 1]) > 2:
            menu[int(user_input) - 1][1](*menu[int(user_input) - 1][2])
        else:
            menu[int(user_input) - 1][1]()


class ProjectMenu(SuperMenu):
    """Меню для работы с БД"""
    __slots__ = ['dbm', 'user_query',]

    dbm: DBManager
    user_query: UserQuery

    def __init__(self, dbm, user_query):
        super().__init__()
        self.dbm = dbm
        self.user_query = user_query

    def main_menu(self):
        """
        Главное меню
        """
        menu = (
            ("Cписок всех компаний", self.get_companies),
            ("Cписок всех вакансий", self.get_all_vacancies),
            ("Cписок всех вакансий, у которых "
             "зарплата выше средней", self.get_vacancies_with_higher_salary),
            ("Cписок всех вакансий, в названии "
             "которых cодержатся ключевые слова", self.get_vacancies_with_keyword),
            ("Выйти в предыдущее меню", self.raise_back_menu)
        )
        self.print_menu(menu)

    def get_companies(self):
        """
        Пункт меню 1
        ______________________
        """
        menu_1 = (
            ("Удалить компании, у которых не осталось вакансий в базе", self.employers_zero_vac_del),
            ("Ввести id компаний для удаления их из списка", self.employers_del_by_id),
            ("Ввести ключевые слова для поиска в названии, а затем удаления их из списка",
             self.employers_del_by_words),
            ("Выйти в предыдущее меню", self.raise_back_menu),
        )
        try:
            while True:
                self.dbm.get_companies_and_vacancies_count()
                self.print_menu(menu_1)
        except BackMenuException:
            pass

    def employers_zero_vac_del(self):
        """
        Пункт меню 1.1
        """
        self.dbm.employers_zero_vac_del()

    def employers_del_by_id(self):
        """
        Пункт меню 1.2
        """
        list_id = self.user_query.input_id_for_del()
        self.dbm.del_by_id('employers', 'id', list_id)

    def employers_del_by_words(self):
        """
        Пункт меню 1.3
        """
        list_words = self.user_query.input_words_for_del()
        self.dbm.del_by_words('employers', 'name', list_words)

    def get_all_vacancies(self):
        """
        Пункт меню 2
        ______________________
        """
        menu_2 = (
            ("Ввести id вакансий для удаления их из списка", self.vacancies_del_by_id),
            ("Ввести диапазон id вакансий для удаления их из списка", self.vacancies_del_by_range),
            ("Ввести ключевые слова для поиска в названии, а затем удаления их из списка",
             self.vacancies_del_by_words),
            ("Выйти в предыдущее меню", self.raise_back_menu),
        )
        try:
            while True:
                self.dbm.get_all_vacancies()
                self.print_menu(menu_2)
        except BackMenuException:
            pass

    def vacancies_del_by_id(self):
        """
        Пункт меню 2.1
        """
        list_id = self.user_query.input_id_for_del()
        self.dbm.del_by_id('vacancies', 'id', list_id)

    def vacancies_del_by_range(self):
        """
        Пункт меню 2.2
        """
        list_id = self.user_query.input_range_for_del()
        self.dbm.del_by_range('vacancies', 'id', list_id)

    def vacancies_del_by_words(self):
        """
        Пункт меню 2.3
        """
        list_words = self.user_query.input_words_for_del()
        self.dbm.del_by_words('vacancies', 'name', list_words)

    def get_vacancies_with_higher_salary(self):
        """
        Пункт меню 3
        ______________________
        """
        menu_3 = (
            ("Удалить вакансии, не вошедшие в список", self.del_vacancies_without_higher_salary),
            ("Выйти в предыдущее меню", self.raise_back_menu),
        )
        try:
            while True:
                self.dbm.get_vacancies_with_higher_salary()
                self.print_menu(menu_3)
        except BackMenuException:
            pass

    def del_vacancies_without_higher_salary(self):
        """
        Пункт меню 3.1
        """
        self.dbm.del_vacancies_without_higher_salary()
        self.raise_back_menu()

    def get_vacancies_with_keyword(self):
        """
        Пункт меню 4
        ______________________
        """
        menu_4 = (
            ("Удалить вакансии, не вошедшие в список", self.del_vacancies_without_keyword),
            ("Выйти в предыдущее меню", self.raise_back_menu),
        )
        try:
            while True:
                list_words = self.user_query.input_words_for_del()
                self.dbm.get_vacancies_with_keyword(list_words)
                self.print_menu(menu_4)
        except BackMenuException:
            pass

    def del_vacancies_without_keyword(self):
        """
        Пункт меню 4.1
        """
        self.dbm.del_vacancies_without_keyword(self.user_query.keywords)
        self.raise_back_menu()
