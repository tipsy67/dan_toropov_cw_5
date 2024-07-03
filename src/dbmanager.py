import psycopg2

from src.api import Currency
from src.settings import TAGS_FOR_REMOVE


class SuperDBManager:
    """Класс для работы с заданной БД"""
    __slots__ = ('_params', '_conn',)

    def __init__(self, params):
        self._params = params

    def __enter__(self):
        self.__new_connect()
        return self

    def __new_connect(self):
        self._conn = psycopg2.connect(**self._params)
        self._conn.autocommit = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()

    def drop_database(self, database: str):
        """Удалим существующую БД если есть"""
        with self._conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {database} WITH (FORCE)")

    def create_database(self, database: str):
        """Создадим новую БД если ее нет и сделаем реконнект к ней"""
        with self._conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) = 0 FROM pg_catalog.pg_database "
                        f"WHERE datname = '{database}'")
            not_exists, = cur.fetchone()
            if not_exists:
                cur.execute(f"CREATE DATABASE {database}")
        self._conn.close()
        self._params['dbname'] = database
        self.__new_connect()

    def add_data(self, table: str, data: [dict]):
        """
        Добавим данные в базу
        table - имя таблицы
        data  - словарь с ключами, соответствующими наваниям колонок таблицы
        """
        columns = ','.join(data[0].keys())
        count_columns = len(data[0])
        s_str = ','.join(['%s'] * count_columns)
        with self._conn.cursor() as cur:
            args_str = ','.join(cur.mogrify(f"({s_str})", tuple(x.values())).decode('utf-8') for x in data)
            cur.execute(f"INSERT INTO {table}({columns}) "
                        f"VALUES" + args_str)

    def query_and_return(self, query: str) -> [tuple]:
        with self._conn.cursor() as cur:
            cur.execute(query)
            data_from_db = cur.fetchall()

        return data_from_db

    def query_to_db(self, query: str) -> None:
        with self._conn.cursor() as cur:
            cur.execute(query)

    def select_and_print(self, query: str, title: tuple):
        print()
        data_from_db = self.query_and_return(query)
        for name_column in title:
            print(' ' * 5 + name_column, end='')
        print()
        print('-' * 80)
        for row in data_from_db:
            print(*row)

    def del_by_id(self, table_to_delete: str, column_id: str, data: list):
        query = (f"DELETE FROM {table_to_delete} "
                 f"WHERE {column_id} = " + f" OR {column_id} = ".join(data))
        self.query_to_db(query)

    def del_by_range(self, table_to_delete: str, column_id: str, data: list):
        query = (f"DELETE FROM {table_to_delete} "
                 f"WHERE {column_id} BETWEEN {data[0]} AND {data[1]}")
        self.query_to_db(query)

    def del_by_words(self, table_to_delete: str, column_word: str, data: list):
        query = (f"DELETE FROM {table_to_delete} "
                 f"WHERE LOWER({column_word}) LIKE '%" + f"%' OR LOWER({column_word}) LIKE '%".join(data) + "%'")
        self.query_to_db(query)


class DBManager(SuperDBManager):
    """ Класс для работы со списком работодателей и вакансий"""
    __slots__ = ('_params', '_conn',)

    def create_tables(self):
        with self._conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS employers("
                        "id INT PRIMARY KEY,"
                        "name VARCHAR(100),"
                        "open_vacancies INT,"
                        "url VARCHAR(100),"
                        "vacancies_url VARCHAR(100))")

            cur.execute("CREATE TABLE IF NOT EXISTS vacancies("
                        "id SERIAL PRIMARY KEY,"
                        "employer_id INT REFERENCES employers(id) ON DELETE CASCADE,"
                        "name VARCHAR(100),"
                        "salary_min INT,"
                        "salary_max INT,"
                        "area VARCHAR(100),"
                        "employment VARCHAR(100),"
                        "experience VARCHAR(100),"
                        "schedule VARCHAR(100),"
                        "description TEXT,"
                        "url VARCHAR(100))")

    def get_companies_and_vacancies_count(self):
        """Получаем список всех компаний и количество вакансий
           у каждой компании."""
        query = ("SELECT e.id, e.name, e.open_vacancies, e.url, COUNT(v.id) FROM employers AS e "
                 "LEFT JOIN vacancies AS v ON e.id = v.employer_id "
                 "GROUP BY e.id")
        title = ('id', 'name', 'open_vacancies', 'url', 'vacancies_in_base')
        self.select_and_print(query, title)

    def get_all_vacancies(self):
        """Получаем список всех вакансий с указанием названия
        компании, названия вакансии и зарплаты и ссылки на вакансию."""
        query = ("SELECT v.id, e.name, v.name, v.salary_min, v.salary_max, v.url "
                 "FROM employers AS e "
                 "JOIN vacancies AS v "
                 "ON e.id = v.employer_id "
                 "ORDER BY v.id")
        title = ('id', 'company', 'vacancy', 'salary_min', 'salary_max', 'url')
        self.select_and_print(query, title)

    def get_avg_salary(self) -> int | float:
        """Получаем среднюю зарплату по вакансиям"""
        query = ("SELECT SUM("
                 "CASE WHEN salary_min = 0 THEN salary_max ELSE salary_min END+"
                 "CASE WHEN salary_max = 0 THEN salary_min ELSE salary_max END"
                 ")/2 AS sum_,"
                 "COUNT(*) AS all_ "
                 "FROM vacancies")
        data_from_db = self.query_and_return(query)
        sum_, all_ = data_from_db[0][0], data_from_db[0][1]
        if not all_:
            print("Запрос вернул 0")
            return 0
        return sum_ / all_

    def get_vacancies_with_higher_salary(self):
        """Получаем список всех вакансий, у которых зарплата выше
        средней по всем вакансиям."""
        avg_salary = self.get_avg_salary()
        query = ("SELECT v.id, e.name, v.name, v.salary_min, v.salary_max, v.url "
                 "FROM employers AS e "
                 "JOIN vacancies AS v "
                 "ON e.id = v.employer_id "
                 "WHERE (CASE WHEN salary_min = 0 THEN salary_max ELSE salary_min END+"
                 "CASE WHEN salary_max = 0 THEN salary_min ELSE salary_max END"
                 f")/2 > {avg_salary} "
                 "ORDER BY v.id ")
        title = ('id', 'company', 'vacancy', 'salary_min', 'salary_max', 'url')
        self.select_and_print(query, title)

    def del_vacancies_without_higher_salary(self):
        """Удаляем все вакансии, у которых зарплата ниже или равна
        средней по всем вакансиям."""
        avg_salary = self.get_avg_salary()
        query = ("DELETE FROM vacancies "
                 "WHERE (CASE WHEN salary_min = 0 THEN salary_max ELSE salary_min END+"
                 "CASE WHEN salary_max = 0 THEN salary_min ELSE salary_max END"
                 f")/2 <= {avg_salary} ")
        self.query_to_db(query)

    def get_vacancies_with_keyword(self, data: list):
        """Получаем список всех вакансий, в названии которых
        содержатся переданные в метод слова, например python."""
        query = ("SELECT v.id, e.name, v.name, v.salary_min, v.salary_max, v.url "
                 "FROM employers AS e "
                 "JOIN vacancies AS v "
                 "ON e.id = v.employer_id "
                 f"WHERE LOWER(v.name) LIKE '%" + f"%' OR LOWER(v.name) LIKE '%".join(data) + "%' "
                                                                                              "ORDER BY v.id")
        title = ('id', 'company', 'vacancy', 'salary_min', 'salary_max', 'url')
        self.select_and_print(query, title)

    def del_vacancies_without_keyword(self, data: list):
        """Удаляем все вакансии, в названии которых не
        содержатся переданные в метод слова, например python."""
        query = ("DELETE FROM vacancies "
                 f"WHERE LOWER(name) NOT LIKE '%" + f"%' AND LOWER(name) NOT LIKE '%".join(data) + "%' ")
        self.query_to_db(query)

    def employers_zero_vac_del(self):
        query = ("WITH cte AS("
                 "SELECT e.id, COUNT(v.id) AS quantity FROM employers AS e "
                 "LEFT JOIN vacancies AS v ON e.id = v.employer_id "
                 "GROUP BY e.id "
                 ") "
                 "DELETE FROM employers AS e "
                 f"WHERE e.id IN (SELECT cte.id FROM cte WHERE cte.quantity = 0)")
        self.query_to_db(query)


    @staticmethod
    def refactor_employers_data(data_emp: [dict]) -> [dict]:
        """Преобразуем данные о компаниях с НН для последущей записи в БД"""
        new_data_emp = [{'id': x['id'], 'name': x['name'], 'open_vacancies': x['open_vacancies'],
                         'url': x['alternate_url'], 'vacancies_url': x['vacancies_url']} for x in data_emp]
        return new_data_emp

    @staticmethod
    def refactor_vacancies_data(data_vac: [dict]) -> list:
        """Преобразуем данные о вакансиях с НН для последущей записи в БД"""
        new_data_vac = []
        for x in data_vac:
            salary = DBManager.get_salary(x['salary'])
            new_vacancy = {
                'employer_id': x['employer']['id'],
                'name': x['name'],
                'salary_min': salary[0],
                'salary_max': salary[1],
                'area': x['area']['name'],
                'url': x['alternate_url'],
                'employment': x['employment']['name'],
                'experience': x['experience']['name'],
                'schedule': x['schedule']['name'],
                'description': (x['snippet']['requirement'] if x['snippet']['requirement'] is not None else '') +
                               (x['snippet']['responsibility'] if x['snippet']['responsibility'] is not None else '')
            }
            for element in TAGS_FOR_REMOVE:
                new_vacancy['description'] = new_vacancy['description'].replace(element, '')
            new_data_vac.append(new_vacancy)
        return new_data_vac

    @staticmethod
    def get_salary(data) -> tuple:
        """
        Переведем зарплату в валюте по текущему курсу
        :param data: словарь данных о зарплате с НН
        {"from": 350000, "to": 450000, "currency": "RUR", "gross": False}
        :return: возвращаем вилку зарплат в рублях
        (350000, 450000)
        """
        if data is not None:
            if data['currency'] is not None and data['currency'] != 'RUR':
                rate = Currency.get_rate(data['currency'])
            else:
                rate = 1

            return (
                int(data['from'] / rate) if data['from'] is not None else 0,
                int(data['to'] / rate) if data['to'] is not None else 0
            )
        else:
            return 0, 0
