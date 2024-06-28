from src.exceptions import ExitException
from src.utils import load_top_x, load_keyword, use_last_query

MENU_1 = (('Загрузить ТОР х компаний по кол-ву вакансий', load_top_x),
          ('Ввести ключевые слова в названии компаний', load_keyword),
          ('Использовать предыдущий запрос', use_last_query))

def print_menu (menu: tuple) -> int:
    print ("Выберите необходимый пункт меню:")
    len_menu = len(menu)
    for index, item in enumerate(menu):
        print(f'{index+1}. {item[0]}')
    while True:
        user_input = input().strip().lower()
        if user_input.isdigit() and 0 < int(user_input) < len_menu:
            break
        elif user_input == 'exit':
            raise ExitException
        else:
            print(f"Введите число от 1 до {len_menu}. 'exit' - для выхода")
    menu[int(user_input)-1][1]()



