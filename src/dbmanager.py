import psycopg2

from src.settings import DEFAULT_DATABASE


class DBManager:
    __slots__ = ('__params', '__conn', )

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
            cur.execute(f"SELECT COUNT(*) = 0 FROM pg_catalog.pg_database WHERE datname = '{DEFAULT_DATABASE}'")
            not_exists, = cur.fetchone()
            if not_exists:
                cur.execute(f"CREATE DATABASE {DEFAULT_DATABASE}")
        self.__conn.close()
        self.__params['dbname'] = DEFAULT_DATABASE
        self.__new_connect()

    def create_tables(self):
        with self.__conn.cursor() as cur:
            cur.execute("CREATE TABLE IF NOT EXISTS repos("
                        "rep_id SERIAL PRIMARY KEY,"
                        "name VARCHAR(50),"
                        "full_name VARCHAR(50),"
                        "language VARCHAR(50),"
                        "watchers_count INTEGER,"
                        "description TEXT,"
                        "forks INTEGER)")

    def get_companies_and_vacancies_count(self):
        """получает список всех компаний и количество вакансий
           у каждой компании."""
        pass

    def get_all_vacancies(self):
        """получает список всех вакансий с указанием названия
        компании, названия вакансии и зарплаты и ссылки на вакансию."""
        pass

    def get_avg_salary(self):
        """получает среднюю зарплату по вакансиям"""
        pass

    def get_vacancies_with_higher_salary(self):
        """получает список всех вакансий, у которых зарплата выше
        средней по всем вакансиям."""
        pass

    def get_vacancies_with_keyword(self):
        """получает список всех вакансий, в названии которых
        содержатся переданные в метод слова, например python."""
        pass
