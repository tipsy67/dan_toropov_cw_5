from configparser import ConfigParser

from src.settings import DEFAULT_INI, DEFAULT_SECTION


def read_config(filename=DEFAULT_INI, section=DEFAULT_SECTION):
    """Заберем конфигурационные данные подключения к базе данных из INI файла"""
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db
