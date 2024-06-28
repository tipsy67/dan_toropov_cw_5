from pathlib import Path

SEARCH_PER_PAGE = 100  # 100
SEARCH_PAGE = 20  # 20

PATH = Path(__file__).parent

URL_VACANCIES = 'https://api.hh.ru/vacancies'
URL_EMPLOYERS = 'https://api.hh.ru/employers'

DEFAULT_DATABASE = 'hhinfo'

DEFAULT_INI = PATH.joinpath('dbase.ini')
DEFAULT_SECTION = 'postgres1'


