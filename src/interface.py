from src.exceptions import ExitException


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

        self.__top_n: int = self.input_top_n()
        self.__filter_words: list[str] = self.input_filter_words()
        self.__is_rewrite: bool = self.input_is_rewrite()
        self.__keywords: list[str] | None = None

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

    @property
    def keywords(self):
        return self.__keywords

    @classmethod
    def input_processing(cls, message, key) -> str:
        """
        При каждом вводе данных, выводим подсказку если есть данные предыдущего запроса
        и отслеживаем команду выхода из программы
        """
        print(message)
        prompt_last_query = cls.last_user_query.get(key)
        if prompt_last_query is not None and len(str(prompt_last_query)) > 0:
            print(f"предыдущий запрос '{prompt_last_query}'")
        user_input = input()
        if user_input.strip(' ').lower() == "/exit":
            raise ExitException
        return user_input

    def remember_query(self) -> None:
        """ Запомним данные пользовательского запроса """
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

    def input_items(self, text: str, key: str) -> list:
        """Для получения от пользователя списка параметров"""
        items = []
        while not (len(items) > 0):
            items = self.input_processing(text, key).lower().split()
            items = [x.replace(' ', '') for x in items]

        return items

    def input_filter_words(self) -> list[str]:
        filter_words = self.input_items("Введите через пробел"
                                        " ключевые слова для поиска компаний: ",
                                        'filter_words')

        return filter_words

    def input_id_for_del(self) -> list[str]:
        id_for_del = []
        while not (len(id_for_del) > 0):
            id_for_del = self.input_items("Введите через пробел"
                                          " id для поиска и удаления:",
                                          'defunct_key')
            id_for_del = [x for x in id_for_del if x.isdigit()]

        return id_for_del

    def input_words_for_del(self) -> list[str]:
        words_for_del = self.input_items("Введите через пробел ключевые слова:",
                                         'defunct_key')
        self.__keywords = words_for_del

        return words_for_del

    def input_range_for_del(self) -> list[str]:
        range_id = ['', '']
        while len(range_id) != 2 or not range_id[0].isdigit() or not range_id[1].isdigit():
            range_id = self.input_processing("Введите диапазон id для удаления через дефис: ",
                                             'salary_range')
            if len(range_id) > 0:
                range_id = range_id.replace(' ', '').split('-')

        return range_id
