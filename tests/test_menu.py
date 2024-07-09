import pytest

from src.exceptions import ExitException
from src.menu import SuperMenu
from tests.test_utils_from_github import set_keyboard_input, get_display_output


def test_print_menu():
    def one():
        print('1')
    def two():
        print('2')

    test_super_menu = SuperMenu()
    test_menu = (
        ('One', one),
        ('Two', two)
    )
    set_keyboard_input(['1'])
    test_super_menu.print_menu(test_menu)
    assert get_display_output() == ['', 'Выберите необходимый пункт меню:', '1. One', '2. Two', '1']

    set_keyboard_input(['2'])
    test_super_menu.print_menu(test_menu)
    assert get_display_output() == ['', 'Выберите необходимый пункт меню:', '1. One', '2. Two', '2']

    with pytest.raises(ExitException):
        set_keyboard_input(['/exit'])
        test_super_menu.print_menu(test_menu)

