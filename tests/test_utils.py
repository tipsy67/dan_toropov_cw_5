import pytest

from src.settings import PATH
from src.utils import read_config


def test_read_config():
    test_data = read_config(filename=PATH.joinpath('dbase.ini.example'))
    assert test_data['host'] == 'localhost'
    assert test_data['user'] == 'sa'
    assert test_data['password'] == '12345'
    assert test_data['port'] == '5432'
    assert test_data['dbname'] == 'postgres'

def test_read_config_raise():
    with pytest.raises(Exception):
        read_config(filename='raise_dbase.ini.example')


