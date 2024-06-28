from src.exceptions import ExitException
from src.interface import print_menu, MENU_1


def main():
    print_menu(MENU_1)

if __name__ == '__main__':
    try:
        main()
    except ExitException:
        print("Работа завершена.")