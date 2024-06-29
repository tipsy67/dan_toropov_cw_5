
from src.exceptions import ExitException

MENU_1 = (('Заполнить БД ',),
          ('Использовать предыдущий запрос', ))


class UserQuery:
    """
    Класс для формирования пользовательского запроса:
        top_n           - количество компаний для вывода в топ N
        filter_words    - ключевые слова для фильтрации компаний
        is_rewrite      - флаг необходимости очистки базы
    """

    # будем запоминать сюда данные предыдущего запроса
    # для подсказок пользователю при вводе новых данных

    last_user_query = {}

    def __init__(self):
        print("Поиск вакансий. Для выхода из программы в любой момент введите: /exit")

        self.__top_n = self.input_top_n()
        self.__filter_words = self.input_filter_words()
        self.__is_rewrite = self.input_is_rewrite()

        self.remember_query()

    @property
    def top_n(self):
        return self.__top_n

    @property
    def filter_words(self):
        return self.__filter_words

    @property
    def is_rewrite(self):
        return self.__is_rewrite

    @classmethod
    def input_processing(cls, message, key) -> str:
        """
        при каждом вводе данных, выводим подсказку если есть данные предыдущего запроса
        и отслеживаем команду выхода из программы
        """
        print(message)
        prompt_last_query = cls.last_user_query.get(key)
        if prompt_last_query is not None and len(prompt_last_query) > 0:
            print(f"предыдущий запрос '{prompt_last_query}'")
        user_input = input()
        if user_input.strip(' ').lower() == "/exit":
            raise ExitException
        return user_input

    def remember_query(self) -> None:
        """
        запомним данные пользовательского запроса
        :param user_query: UserQuery
        :return:
        """
        list_ = [x.replace('_UserQuery__', '') for x in self.__dict__ if not callable(x)]
        for x in list_:
            self.last_user_query[x] = getattr(self, x)

    def input_is_rewrite(self) -> bool:
        is_rewrite = None
        while is_rewrite not in ('1', '2'):
            is_rewrite = self.input_processing("Ввведите цифру:\n"
                                               " 1 - очищать базу данных перед запросом\n"
                                               " 2 - добавлять найденные данные к уже имеющимся",
                                               'is_rewrite')

        return True if is_rewrite == '1' else False

    def input_top_n(self) -> int:
        top_n = ''
        while not top_n.isdigit() or int(top_n) > 20:
            top_n = self.input_processing("Введите количество компаний (до 20) для выбора топ N: ",
                                          'top_n')

        return int(top_n)

    def input_filter_words(self) -> list[str]:
        filter_words = self.input_processing("Введите через пробел"
                                             " ключевые слова для поиска компаний: ",
                                             'filter_words').lower().split()
        filter_words = [x.replace(' ', '') for x in filter_words]

        return filter_words

    @staticmethod
    def print_menu(menu: tuple):
        print("Выберите необходимый пункт меню:")
        len_menu = len(menu)
        for index, item in enumerate(menu):
            print(f'{index + 1}. {item[0]}')
        while True:
            user_input = input().strip().lower()
            if user_input.isdigit() and 0 < int(user_input) < len_menu:
                break
            elif user_input == '/exit':
                raise ExitException
            else:
                print(f"Введите число от 1 до {len_menu}. '/exit' - для выхода")
        menu[int(user_input) - 1][1]()
