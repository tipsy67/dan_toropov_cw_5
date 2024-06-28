from src.dbmanager import DBManager
from src.exceptions import ExitException
from src.interface import UserQuery

from src.utils import load_json_employers, read_config


def main():
    user_query = UserQuery()
    load_json_employers(user_query)
    params_db = read_config()
    dbmanager = DBManager(params_db)
    with dbmanager as dbm:
        if user_query.is_rewrite:
            dbm.drop_database()
        dbm.create_database()
        dbm.create_tables()

if __name__ == '__main__':
    try:
        main()
    except ExitException:
        print("Работа завершена.")