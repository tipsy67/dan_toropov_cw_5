import psycopg2

from src.api import Currency
from src.settings import DEFAULT_DATABASE, TAGS_FOR_REMOVE


class DBManager:
    __slots__ = ('__params', '__conn',)

    def __init__(self, params):
        self.__params = params

    def __enter__(self):
        self.__new_connect()
        return self

    def __new_connect(self):
        self.__conn = psycopg2.connect(**self.__params)
        self.__conn.autocommit = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.__conn.close()

    def drop_database(self):
        """Создадим новую базу и необходимую таблицу в ней"""
        with self.__conn.cursor() as cur:
            cur.execute(f"DROP DATABASE IF EXISTS {DEFAULT_DATABASE} WITH (FORCE)")

    def create_database(self):
        with self.__conn.cursor() as cur:
            cur.execute(f"SELECT COUNT(*) = 0 FROM pg_catalog.pg_database "
                        f"WHERE datname = '{DEFAULT_DATABASE}'")
            not_exists, = cur.fetchone()
            if not_exists:
                cur.execute(f"CREATE DATABASE {DEFAULT_DATABASE}")
        self.__conn.close()
        self.__params['dbname'] = DEFAULT_DATABASE
        self.__new_connect()

    def create_tables(self):
        with self.__conn.cursor() as cur:
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

    def add_data(self, table: str, data: [dict]):
        """
        Добавим данные в базу
        table - имя таблицы
        data  - словарь с ключами, соответствующими наваниям колонок таблицы
        """
        columns = ','.join(data[0].keys())
        count_columns = len(data[0])
        s_str = ','.join(['%s'] * count_columns)
        with self.__conn.cursor() as cur:
            args_str = ','.join(cur.mogrify(f"({s_str})", tuple(x.values())).decode('utf-8') for x in data)
            cur.execute(f"INSERT INTO {table}({columns}) "
                        f"VALUES" + args_str)

    def query_and_return(self, query: str) -> [tuple]:
        with self.__conn.cursor() as cur:
            cur.execute(query)
            data_from_db = cur.fetchall()

        return data_from_db

    def query_to_db(self, query: str) -> None:
        with self.__conn.cursor() as cur:
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

    def get_companies_and_vacancies_count(self):
        """получает список всех компаний и количество вакансий
           у каждой компании."""
        query = ("SELECT e.id, e.name, e.open_vacancies, e.url, COUNT(v.id) FROM employers AS e "
                 "LEFT JOIN vacancies AS v ON e.id = v.employer_id " 
                 "GROUP BY e.id")
        title = ('id', 'name', 'open_vacancies', 'url', 'vacancies_in_base')
        self.select_and_print(query, title)

    def get_all_vacancies(self):
        """получает список всех вакансий с указанием названия
        компании, названия вакансии и зарплаты и ссылки на вакансию."""
        query = ("SELECT v.id, e.name, v.name, v.salary_min, v.salary_max, v.url "
                 "FROM employers AS e "
                 "JOIN vacancies AS v "
                 "ON e.id = v.employer_id "
                 "ORDER BY v.id")
        title = ('id', 'company', 'vacancy', 'salary_min', 'salary_max', 'url')
        self.select_and_print(query, title)

    def get_avg_salary(self) -> int | float:
        """получает среднюю зарплату по вакансиям"""
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
        """получает список всех вакансий, у которых зарплата выше
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
        """получает список всех вакансий, у которых зарплата выше
        средней по всем вакансиям."""
        avg_salary = self.get_avg_salary()
        query = ("DELETE FROM vacancies "
                 "WHERE (CASE WHEN salary_min = 0 THEN salary_max ELSE salary_min END+"
                 "CASE WHEN salary_max = 0 THEN salary_min ELSE salary_max END"
                 f")/2 <= {avg_salary} ")
        self.query_to_db(query)

    def get_vacancies_with_keyword(self, data: list):
        """получает список всех вакансий, в названии которых
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
        """получает список всех вакансий, в названии которых
        содержатся переданные в метод слова, например python."""
        query = ("DELETE FROM vacancies "
                 f"WHERE LOWER(name) NOT LIKE '%" + f"%' AND LOWER(name) NOT LIKE '%".join(data) + "%' ")
        self.query_to_db(query)

    @staticmethod
    def refactor_employers_data(data_emp: [dict]) -> [dict]:
        new_data_emp = [{'id': x['id'], 'name': x['name'], 'open_vacancies': x['open_vacancies'],
                         'url': x['alternate_url'], 'vacancies_url': x['vacancies_url']} for x in data_emp]
        return new_data_emp

    @staticmethod
    def refactor_vacancies_data(data_vac: [dict]) -> list:
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
        :param data:
        :return:
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
